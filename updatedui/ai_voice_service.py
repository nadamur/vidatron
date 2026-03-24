"""
Voice AI bridge for Kivy UI using vidatron_ai stack.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import wave
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

import numpy as np
from scipy import signal


def _vidatron_ai_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "vidatron_ai"


def _ensure_ai_path() -> Path:
    root = _vidatron_ai_dir()
    s = str(root)
    if s not in sys.path:
        sys.path.insert(0, s)
    return root


def _vidatron_ai_config_class():
    import importlib.util

    root = _vidatron_ai_dir()
    mod_name = "vidatron_ai._runtime_config"
    if mod_name in sys.modules:
        return sys.modules[mod_name].Config
    path = root / "config.py"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load vidatron_ai config from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod.Config


class AIState(str, Enum):
    OFF = "off"
    WAITING = "waiting"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    FOLLOW_UP = "follow_up"


def _play_wav_blocking(path: str) -> None:
    if sys.platform == "darwin" and shutil.which("afplay"):
        subprocess.run(["afplay", path], check=False, capture_output=True)
    elif shutil.which("ffplay"):
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path],
            check=False,
            capture_output=True,
        )
    else:
        time.sleep(min(2.0, os.path.getsize(path) / 32000.0))


class AIVoiceService:
    def __init__(self, ui_callback: Callable[..., None]):
        self._ui = ui_callback
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._stream = None
        self._running = False

        self.mic_sample_rate = 16000
        self.target_sample_rate = 16000
        self.chunk_size = 1280
        self.silence_threshold = 0.01
        # Keep latency low: once you stop speaking, we trigger Whisper quickly.
        # (Also helps the "thinking" -> "transcribing" transition feel immediate.)
        self.silence_duration = 0.85
        self.min_speech_duration = 0.3
        self.follow_up_timeout = 45.0

        self._config = None
        self._ollama = None
        self._router = None
        self._tts = None
        self._wake = None
        self._weather = None
        self._news = None
        self._cloud = None

        self.wake_phrase = "Hey Veedatron"
        self.wake_threshold = 0.45
        self.conversation_active = False
        self.state = AIState.OFF
        self.recording_buffer: list = []
        self.speech_started = False
        self.speech_start_time = 0.0
        self.silence_counter = 0
        self.processing = False
        self.current_request_id = 0
        self.follow_up_start_time = 0.0

    def _emit(self, **kwargs):
        kwargs.setdefault("conversation_active", self.conversation_active)
        self._ui(**kwargs)

    def _is_conversation_end(self, text: str) -> bool:
        t = re.sub(r"[^\w\s]", " ", (text or "").lower())
        t = " ".join(t.split())
        if not t:
            return False
        endings = (
            "bye vidatron",
            "bye veedatron",
            "goodbye vidatron",
            "goodbye veedatron",
            "see you vidatron",
            "stop listening",
            "end conversation",
            "exit voice",
        )
        if any(e in t for e in endings):
            return True
        if t in ("bye", "goodbye", "see ya", "cya"):
            return True
        return False

    def _strip_wake_phrase(self, text: str) -> str:
        t = (text or "").strip()
        low = t.lower()
        for p in (
            self.wake_phrase.lower(),
            "hey vidatron",
            "hey veedatron",
            "hey, vidatron",
            "hey, veedatron",
        ):
            if low.startswith(p):
                rest = t[len(p) :].lstrip(" ,.;:!?-\u2014")
                return rest if rest.strip() else t
        return t

    def _end_conversation(self):
        self.conversation_active = False
        self.state = AIState.WAITING
        self.processing = False
        self.recording_buffer = []
        self.speech_started = False
        self.silence_counter = 0
        self.current_request_id += 1
        if self._wake:
            try:
                self._wake.reset()
            except Exception:
                pass
        self._emit(
            state=AIState.WAITING,
            conversation_active=False,
            conversation_ended=True,
            wake_confidence=0.0,
        )

    def _load_brain(self):
        _ensure_ai_path()
        VAIConfig = _vidatron_ai_config_class()
        from brain.ollama_client import OllamaClient
        from brain.router import Router, ToolType
        from brain.tools.time_tool import get_current_time
        from brain.tools.system_tool import get_system_status
        from brain.tools.joke_tool import get_joke
        from brain.tools.weather_tool import WeatherTool
        from brain.tools.news_tool import NewsTool
        from brain.cloud_client import KimiClient
        from audio.tts_engine import PiperTTS
        from openwakeword.model import Model as WakeWordModel
        from openwakeword_resources import ensure_openwakeword_feature_models

        self._get_time = get_current_time
        self._get_system = get_system_status
        self._get_joke = get_joke
        self._ToolType = ToolType

        self._config = VAIConfig.load()
        self.mic_sample_rate = int(self._config.mic_sample_rate)
        self.target_sample_rate = int(self._config.target_sample_rate)
        self.chunk_size = max(128, int(self.mic_sample_rate * 0.08))
        self.wake_threshold = float(self._config.wake_word_threshold)

        wn = Path(self._config.wake_word_model).name.lower()
        if "jarvis" in wn:
            self.wake_phrase = "Hey Jarvis"
        elif "veedatron" in wn or "vidatron" in wn:
            self.wake_phrase = "Hey Veedatron"

        if not Path(self._config.piper_voice).is_file():
            raise FileNotFoundError(f"Piper voice missing: {self._config.piper_voice}")
        if not Path(self._config.whisper_path).is_file():
            raise FileNotFoundError(f"Whisper missing: {self._config.whisper_path}")
        if not Path(self._config.wake_word_model).is_file():
            raise FileNotFoundError(f"Wake model missing: {self._config.wake_word_model}")

        self._ollama = OllamaClient(model=self._config.chat_model)
        if not self._ollama.is_available():
            raise RuntimeError("Ollama is not running (need: ollama serve)")

        self._router = Router(self._ollama)
        self._tts = PiperTTS(model_path=self._config.piper_voice)
        ensure_openwakeword_feature_models()
        self._wake = WakeWordModel(
            wakeword_models=[self._config.wake_word_model],
            inference_framework="onnx",
        )

        self._weather = None
        if self._config.openweather_api_key:
            try:
                self._weather = WeatherTool(api_key=self._config.openweather_api_key)
            except Exception:
                pass

        self._news = None
        if self._config.newsapi_key:
            try:
                self._news = NewsTool(api_key=self._config.newsapi_key)
            except Exception:
                pass

        self._cloud = None
        if self._config.moonshot_api_key:
            try:
                self._cloud = KimiClient(
                    api_key=self._config.moonshot_api_key,
                    soul_path=self._config.cloud_soul_path,
                )
            except Exception:
                pass

    def _resample(self, audio, orig_sr, target_sr):
        if orig_sr == target_sr:
            return audio
        g = np.gcd(int(orig_sr), int(target_sr))
        up = int(target_sr) // g
        down = int(orig_sr) // g
        return signal.resample_poly(audio, up, down).astype(np.float32)

    def _rms(self, chunk):
        return float(np.sqrt(np.mean(chunk**2)))

    def _ollama_general_answer(self, user_text: str, hint: str = "") -> str:
        """Use local Ollama for general knowledge when cloud/API tools are unavailable."""
        if not self._ollama:
            return "I'm not sure how to help with that."
        sys_parts = [
            "You are Vidatron, a friendly voice robot assistant.",
            "Reply in 1-3 short sentences for text-to-speech. No markdown or lists.",
            "Be clear and accurate for general knowledge questions.",
        ]
        if hint:
            sys_parts.append(hint)
        messages = [
            {"role": "system", "content": " ".join(sys_parts)},
            {"role": "user", "content": user_text},
        ]
        try:
            r = self._ollama.chat(messages, tools=None)
            out = (r.content or "").strip()
            return out if out else "I'm not sure."
        except Exception:
            return "Sorry, I couldn't work that out just now."

    def _route_response(self, text: str, req_id: int) -> str:
        ToolType = self._ToolType
        cfg = self._config
        result = self._router.route(text)
        if result.tool == ToolType.NONE:
            ans = (result.response or "").strip()
            if len(ans) < 4:
                return self._ollama_general_answer(text)
            return ans
        if result.tool == ToolType.TIME:
            return self._get_time()
        if result.tool == ToolType.SYSTEM_STATUS:
            return self._get_system()
        if result.tool == ToolType.JOKE:
            return self._get_joke()
        if result.tool == ToolType.WEATHER:
            if self._weather:
                loc = result.arguments.get("location") or cfg.local_location or "New York"
                try:
                    return self._weather.get_weather(loc)
                except Exception:
                    pass
            return self._ollama_general_answer(
                text,
                "They asked about weather. You do not have live radar data. "
                "Answer briefly: suggest checking a weather app or site for current conditions, "
                "and you may add one short general tip (e.g. dress for the season) if helpful.",
            )
        if result.tool == ToolType.NEWS:
            if self._news:
                cat = result.arguments.get("category", "")
                try:
                    return self._news.get_news(cat)
                except Exception:
                    return "Sorry, I couldn't get the news."
            return self._ollama_general_answer(
                text,
                "They asked for news. You cannot browse live headlines. Suggest checking a news app or website briefly.",
            )
        if result.tool == ToolType.CLOUD:
            if self._cloud:
                for attempt in range(2):
                    if req_id != self.current_request_id:
                        return ""
                    try:
                        q = result.arguments.get("query", text)
                        cloud_ans = self._cloud.chat(q, stream=False) or ""
                        if cloud_ans.strip():
                            return cloud_ans.strip()
                    except Exception as e:
                        if "429" in str(e) and attempt == 0:
                            time.sleep(3)
            return self._ollama_general_answer(text)
        return result.response or self._ollama_general_answer(text)

    def _process_recording(self):
        req_id = self.current_request_id
        try:
            if not self.recording_buffer:
                if self.conversation_active:
                    self.state = AIState.FOLLOW_UP
                    self.follow_up_start_time = time.time()
                    self._emit(state=AIState.FOLLOW_UP, phase="Listening…")
                else:
                    self._emit(state=AIState.WAITING, line=f"Say '{self.wake_phrase}' to start.")
                self.processing = False
                return

            audio = np.concatenate(self.recording_buffer)
            max_val = np.max(np.abs(audio)) if len(audio) else 0
            if max_val > 0.001:
                audio = audio / max_val * 0.95
            audio_i16 = (audio * 32767).astype(np.int16)

            fd, wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.target_sample_rate)
                wf.writeframes(audio_i16.tobytes())

            self._emit(state=AIState.THINKING, phase="Transcribing…")
            r = subprocess.run(
                [self._config.whisper_path, "-m", self._config.whisper_model, "-l", "en", "-ng", wav_path],
                capture_output=True,
                text=True,
                timeout=120,
            )
            os.unlink(wav_path)
            raw = (r.stdout or "").strip()
            text = re.sub(r"\[\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}\]\s*", "", raw).strip()
            for m in ("[BLANK_AUDIO]", "[MUSIC]", "[NOISE]", "[SILENCE]", "(silence)", "[inaudible]"):
                text = text.replace(m, "")
            text = text.strip()

            if not text or req_id != self.current_request_id:
                if self.conversation_active:
                    self.state = AIState.FOLLOW_UP
                    self.follow_up_start_time = time.time()
                    self._emit(state=AIState.FOLLOW_UP, phase="Listening…")
                else:
                    self._emit(state=AIState.WAITING, line=f"Didn't catch that. Say '{self.wake_phrase}' again.")
                self.processing = False
                return

            if self.conversation_active and self._is_conversation_end(text):
                self._end_conversation()
                self.processing = False
                return

            heard = self._strip_wake_phrase(text)
            if not heard:
                heard = text

            self._emit(state=AIState.THINKING, title="You", line=heard, phase="Thinking…")
            reply = self._route_response(heard, req_id)
            if req_id != self.current_request_id:
                self.processing = False
                return

            self._emit(state=AIState.SPEAKING, title="Vidatron", line=reply[:900], phase="Speaking…")
            out = self._tts.synthesize(reply)
            try:
                _play_wav_blocking(out)
            finally:
                try:
                    os.unlink(out)
                except OSError:
                    pass

            if req_id == self.current_request_id and self.conversation_active:
                self.recording_buffer = []
                self.speech_started = False
                self.silence_counter = 0
                self.state = AIState.FOLLOW_UP
                self.follow_up_start_time = time.time()
                self._emit(state=AIState.FOLLOW_UP, phase="Listening — follow-up or say bye")
            elif req_id == self.current_request_id:
                self.state = AIState.WAITING
                self._emit(state=AIState.WAITING, wake_confidence=0.0)
            self.processing = False
        except Exception as e:
            self.processing = False
            if self.conversation_active:
                self.state = AIState.FOLLOW_UP
                self.follow_up_start_time = time.time()
                self._emit(state=AIState.FOLLOW_UP, line=("Error: " + str(e))[:220], phase="Listening…")
            else:
                self._emit(state=AIState.WAITING, line=("Error: " + str(e))[:220])

    def _audio_cb(self, indata, frames, _ti, _st):
        if self._stop.is_set():
            return
        audio = indata[:, 0].copy()
        if self.mic_sample_rate != self.target_sample_rate:
            audio = self._resample(audio, self.mic_sample_rate, self.target_sample_rate).astype(np.float32)
        rms = self._rms(audio)

        st = self.state
        if st == AIState.WAITING:
            if self.conversation_active:
                return
            pred = self._wake.predict((audio * 32767).astype(np.int16))
            scores = list(pred.values()) if pred else []
            conf = max(scores) if scores else 0.0
            self._emit(wake_confidence=conf)
            if conf >= self.wake_threshold:
                self._wake.reset()
                self.current_request_id += 1
                self.conversation_active = True
                self.state = AIState.LISTENING
                self.recording_buffer = []
                self.speech_started = False
                self.silence_counter = 0
                self._emit(state=AIState.LISTENING, title="Vidatron", phase="Listening…")
        elif st in (AIState.LISTENING, AIState.FOLLOW_UP, AIState.THINKING):
            if self.processing:
                return
            if st == AIState.FOLLOW_UP and time.time() - self.follow_up_start_time > self.follow_up_timeout:
                self._end_conversation()
                return
            self.recording_buffer.append(audio.copy())
            if not self.speech_started and rms > self.silence_threshold * 2:
                self.speech_started = True
                self.speech_start_time = time.time()
                # Start "thinking" as soon as speech begins (not after Whisper returns).
                # We keep recording while in THINKING so audio collection still works.
                if self.state != AIState.THINKING:
                    self.state = AIState.THINKING
                    self._emit(state=AIState.THINKING, phase="Thinking…")
            if self.speech_started:
                dur = time.time() - self.speech_start_time
                if rms < self.silence_threshold:
                    self.silence_counter += 1
                    silence_t = self.silence_counter * (frames / self.mic_sample_rate)
                    if dur > self.min_speech_duration and silence_t > self.silence_duration:
                        self.processing = True
                        self.state = AIState.THINKING
                        threading.Thread(target=self._process_recording, daemon=True).start()
                else:
                    self.silence_counter = 0

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self, quiet: bool = False):
        self._stop.set()
        self._running = False
        self.conversation_active = False
        self.state = AIState.OFF
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        if not quiet:
            self._emit(state=AIState.OFF, line="Voice assistant stopped.", wake_confidence=0.0)

    def _run(self):
        import sounddevice as sd

        try:
            self._load_brain()
        except Exception as e:
            self._emit(state=AIState.OFF, line=("AI init failed: " + str(e))[:220])
            self._running = False
            return

        self.conversation_active = False
        self.state = AIState.WAITING
        self._emit(state=AIState.WAITING, wake_confidence=0.0)

        try:
            self._stream = sd.InputStream(
                samplerate=self.mic_sample_rate,
                channels=1,
                blocksize=self.chunk_size,
                callback=self._audio_cb,
                dtype="float32",
            )
            self._stream.start()
            while not self._stop.is_set():
                time.sleep(0.1)
        except Exception as e:
            self._emit(state=AIState.OFF, line=("Mic error: " + str(e))[:220])
        finally:
            if self._stream:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None
            self._running = False
