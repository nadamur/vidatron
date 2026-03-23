#!/usr/bin/env python3
"""
Test UI for Vidatron - Wake word activated with automatic silence detection.
Say "Hey Veedatron" to activate, then speak your command!
"""

import sys
import os
import threading
import time
import tempfile
import subprocess
import re
import wave
import random
import numpy as np
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from collections import deque
from scipy import signal

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import pygame
import sounddevice as sd

from config import Config
from brain.ollama_client import OllamaClient
from brain.router import Router, ToolType
from brain.tools.time_tool import get_current_time
from brain.tools.system_tool import get_system_status
from brain.tools.joke_tool import get_joke
from brain.tools.weather_tool import WeatherTool
from brain.tools.news_tool import NewsTool
from brain.cloud_client import KimiClient
from audio.tts_engine import PiperTTS

# Import wake word detector
from openwakeword.model import Model as WakeWordModel


class State(Enum):
    WAITING = "waiting"      # Waiting for wake word
    LISTENING = "listening"  # Recording user speech
    THINKING = "thinking"    # Processing/generating response
    SPEAKING = "speaking"    # Playing TTS response
    FOLLOW_UP = "follow_up"  # Waiting for follow-up (no wake word needed)


@dataclass
class UIColors:
    """Color scheme - Cyberpunk/Neon aesthetic"""
    BG = (15, 15, 25)
    PANEL = (25, 28, 40)
    ACCENT = (0, 255, 200)  # Cyan
    ACCENT_DIM = (0, 150, 120)
    PINK = (255, 50, 150)
    PURPLE = (150, 50, 255)
    TEXT = (240, 240, 250)
    TEXT_DIM = (140, 145, 165)
    SUCCESS = (50, 255, 120)
    WARNING = (255, 200, 50)
    ERROR = (255, 80, 80)
    ORANGE = (255, 150, 50)


class TestUI:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
        
        # Window setup
        self.width = 900
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("🤖 Vidatron - Say 'Hey Veedatron'")
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_title = pygame.font.Font(None, 56)
        
        # State
        self.state = State.WAITING
        self.user_text = ""
        self.bot_response = ""
        self.status_message = "Say 'Hey Veedatron' to activate..."
        self.wake_word_confidence = 0.0
        self.audio_level = 0.0
        self.silence_counter = 0
        
        # Animation
        self.animation_frame = 0
        self.pulse_value = 0
        
        # Audio settings - use 16kHz directly for whisper compatibility
        self.mic_sample_rate = 16000  # Record at whisper's native rate
        self.target_sample_rate = 16000  # What whisper/openwakeword expects
        self.channels = 1
        self.chunk_size = 1280  # 80ms chunks at 16kHz
        
        # Silence detection settings
        self.silence_threshold = 0.01  # RMS threshold
        self.silence_duration = 1.5    # Seconds of silence to stop
        self.min_speech_duration = 0.5 # Minimum speech before silence detection kicks in
        
        # Follow-up mode settings
        self.follow_up_timeout = 8.0   # Seconds to wait for follow-up before returning to wake word mode
        self.follow_up_start_time = 0  # When follow-up mode started
        
        # Request tracking - for cancelling stale cloud responses
        self.current_request_id = 0
        
        # Audio buffers
        self.audio_buffer = deque(maxlen=100)  # For wake word
        self.recording_buffer = []
        self.speech_started = False
        self.speech_start_time = 0
        
        # Load face images
        self.faces = self._load_faces()
        
        # Initialize AI components
        print("Initializing AI components...")
        self.config = Config.load()
        
        print(f"  Loading Ollama ({self.config.chat_model})...")
        self.ollama = OllamaClient(model=self.config.chat_model)
        self.router = Router(self.ollama)
        
        # Warm up the local model
        print("  Warming up local model...")
        try:
            self.ollama.ensure_model_loaded()
        except:
            pass
        
        # Initialize cloud client (optional - for complex questions)
        self.cloud = None
        if self.config.moonshot_api_key:
            print("  Loading Cloud AI (Kimi)...")
            try:
                self.cloud = KimiClient(
                    api_key=self.config.moonshot_api_key,
                    soul_path=self.config.cloud_soul_path
                )
                print("  ✓ Cloud AI ready!")
            except Exception as e:
                print(f"  Warning: Cloud AI unavailable: {e}")
        else:
            print("  ℹ Cloud AI not configured (set MOONSHOT_API_KEY for complex questions)")
        
        # Initialize weather tool (optional)
        self.weather = None
        if self.config.openweather_api_key:
            print("  Loading Weather API...")
            try:
                self.weather = WeatherTool(api_key=self.config.openweather_api_key)
                print("  ✓ Weather API ready!")
            except Exception as e:
                print(f"  Warning: Weather unavailable: {e}")
        else:
            print("  ℹ Weather not configured (set OPENWEATHER_API_KEY)")
        
        # Initialize news tool (optional)
        self.news = None
        if self.config.newsapi_key:
            print("  Loading News API...")
            try:
                self.news = NewsTool(api_key=self.config.newsapi_key)
                print("  ✓ News API ready!")
            except Exception as e:
                print(f"  Warning: News unavailable: {e}")
        else:
            print("  ℹ News not configured (set NEWSAPI_KEY)")
        
        print("  Loading TTS...")
        self.tts = PiperTTS(model_path=self.config.piper_voice)
        
        print("  Loading wake word model...")
        self.wake_word_model = WakeWordModel(
            wakeword_models=[self.config.wake_word_model],
            inference_framework='onnx'
        )
        self.wake_word_threshold = self.config.wake_word_threshold
        
        # Load filler audio files
        print("  Loading filler audio...")
        self.filler_sounds = []
        fillers_dir = PROJECT_ROOT / "assets" / "fillers"
        for i in range(5):
            filler_path = fillers_dir / f"filler_{i}.wav"
            if filler_path.exists():
                self.filler_sounds.append(str(filler_path))
        print(f"  ✓ Loaded {len(self.filler_sounds)} filler phrases")
        
        # Thread control
        self.running = True
        self.processing = False
        
        print("✓ UI Ready!")
        print("\n" + "="*50)
        print("  🎤 Say 'Hey Veedatron' to activate!")
        print("="*50 + "\n")
    
    def _load_faces(self):
        """Load face images from assets."""
        faces = {}
        face_dir = PROJECT_ROOT / "assets" / "face"
        
        face_mapping = {
            State.WAITING: "happy.png",
            State.LISTENING: "thinking.png",
            State.THINKING: "thinking.png",
            State.SPEAKING: "happy_eye_glistening.png",
            State.FOLLOW_UP: "happy.png",  # Attentive, waiting for follow-up
        }
        
        for state, filename in face_mapping.items():
            path = face_dir / filename
            if path.exists():
                img = pygame.image.load(str(path))
                img = pygame.transform.scale(img, (200, 200))
                faces[state] = img
            else:
                faces[state] = None
        
        return faces
    
    def _draw_rounded_rect(self, rect, color, radius=15, border=0, border_color=None):
        """Draw a rounded rectangle."""
        if border > 0 and border_color:
            pygame.draw.rect(self.screen, border_color, rect, border, radius)
        pygame.draw.rect(self.screen, color, rect.inflate(-border*2, -border*2), 0, radius)
    
    def _draw_text_wrapped(self, text, font, color, rect, line_height=None):
        """Draw text wrapped to fit within a rectangle."""
        if not text:
            return
        
        if line_height is None:
            line_height = font.get_height() + 5
        
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= rect.width - 20:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        y = rect.y + 10
        for line in lines:
            if y + line_height > rect.y + rect.height - 10:
                break
            text_surface = font.render(line, True, color)
            self.screen.blit(text_surface, (rect.x + 10, y))
            y += line_height
    
    def _draw_waveform(self):
        """Draw audio level visualization."""
        center_x = self.width // 2
        y = 85
        
        # Draw audio level bars
        num_bars = 15
        bar_width = 8
        spacing = 12
        start_x = center_x - (num_bars * spacing) // 2
        
        for i in range(num_bars):
            # Create wave pattern based on audio level
            if self.state == State.LISTENING:
                wave = np.sin(self.animation_frame * 0.15 + i * 0.5)
                height = int(5 + self.audio_level * 40 * (0.5 + 0.5 * abs(wave)))
                color = UIColors.ERROR
            elif self.state == State.SPEAKING:
                wave = np.sin(self.animation_frame * 0.2 + i * 0.4)
                height = int(10 + 25 * (0.5 + 0.5 * abs(wave)))
                color = UIColors.SUCCESS
            elif self.state == State.THINKING:
                wave = np.sin(self.animation_frame * 0.1 + i * 0.3)
                height = int(5 + 15 * (0.5 + 0.5 * abs(wave)))
                color = UIColors.PURPLE
            elif self.state == State.FOLLOW_UP:
                # Follow-up - pulsing orange, responsive to audio
                wave = np.sin(self.animation_frame * 0.12 + i * 0.4)
                height = int(8 + self.audio_level * 30 * (0.5 + 0.5 * abs(wave)))
                color = UIColors.ORANGE
            else:
                # Waiting - show wake word confidence as subtle pulse
                pulse = 0.3 + 0.7 * self.wake_word_confidence
                height = int(3 + 8 * pulse * abs(np.sin(self.animation_frame * 0.05 + i * 0.2)))
                color = UIColors.ACCENT_DIM
            
            bar_x = start_x + i * spacing
            pygame.draw.rect(self.screen, color, 
                           (bar_x, y - height // 2, bar_width, height), 0, 3)
    
    def _draw_state_badge(self):
        """Draw state indicator badge."""
        center_x = self.width // 2
        y = 130
        
        state_config = {
            State.WAITING: ("🎤 Waiting for 'Hey Veedatron'", UIColors.ACCENT_DIM),
            State.LISTENING: ("🔴 Listening... (speak now!)", UIColors.ERROR),
            State.THINKING: ("🧠 Thinking...", UIColors.PURPLE),
            State.SPEAKING: ("🔊 Speaking...", UIColors.SUCCESS),
            State.FOLLOW_UP: ("💬 Listening for follow-up...", UIColors.ORANGE),
        }
        
        text, color = state_config.get(self.state, ("Unknown", UIColors.TEXT_DIM))
        
        # Badge background
        badge_text = self.font_medium.render(text, True, color)
        badge_rect = badge_text.get_rect(center=(center_x, y))
        badge_bg = badge_rect.inflate(30, 15)
        
        pygame.draw.rect(self.screen, UIColors.PANEL, badge_bg, 0, 20)
        pygame.draw.rect(self.screen, color, badge_bg, 2, 20)
        
        self.screen.blit(badge_text, badge_rect)
    
    def _draw_face(self):
        """Draw the robot face with glow effect."""
        face = self.faces.get(self.state)
        face_x = self.width // 2 - 100
        face_y = 160
        
        # Animated glow
        self.pulse_value = (self.pulse_value + 0.08) % (2 * 3.14159)
        pulse = 0.7 + 0.3 * abs(np.sin(self.pulse_value))
        
        glow_color = {
            State.WAITING: tuple(int(c * pulse) for c in UIColors.ACCENT_DIM),
            State.LISTENING: UIColors.ERROR,
            State.THINKING: UIColors.PURPLE,
            State.SPEAKING: UIColors.SUCCESS,
            State.FOLLOW_UP: UIColors.ORANGE,
        }.get(self.state, UIColors.ACCENT_DIM)
        
        # Outer glow rings
        for i in range(3):
            radius = 115 + i * 8
            alpha = int(255 * (1 - i / 3) * pulse)
            pygame.draw.circle(self.screen, glow_color, 
                             (face_x + 100, face_y + 100), radius, 2)
        
        if face:
            self.screen.blit(face, (face_x, face_y))
    
    def _draw_conversation(self):
        """Draw conversation panels."""
        # User text panel
        user_panel = pygame.Rect(50, 390, self.width - 100, 90)
        self._draw_rounded_rect(user_panel, UIColors.PANEL, 12, 2, UIColors.ACCENT_DIM)
        
        label = self.font_small.render("📢 You said:", True, UIColors.ACCENT)
        self.screen.blit(label, (user_panel.x + 10, user_panel.y - 25))
        
        if self.user_text:
            self._draw_text_wrapped(self.user_text, self.font_medium, UIColors.TEXT, user_panel)
        elif self.state == State.LISTENING:
            # Show recording indicator
            dots = "." * (1 + (self.animation_frame // 15) % 3)
            placeholder = self.font_medium.render(f"Recording{dots}", True, UIColors.ERROR)
            self.screen.blit(placeholder, (user_panel.x + 10, user_panel.y + 30))
        else:
            placeholder = self.font_medium.render("(waiting for speech...)", True, UIColors.TEXT_DIM)
            self.screen.blit(placeholder, (user_panel.x + 10, user_panel.y + 30))
        
        # Bot response panel
        bot_panel = pygame.Rect(50, 510, self.width - 100, 130)
        self._draw_rounded_rect(bot_panel, UIColors.PANEL, 12, 2, UIColors.PINK)
        
        label = self.font_small.render("🤖 Vidatron:", True, UIColors.PINK)
        self.screen.blit(label, (bot_panel.x + 10, bot_panel.y - 25))
        
        if self.bot_response:
            self._draw_text_wrapped(self.bot_response, self.font_medium, UIColors.TEXT, bot_panel)
        elif self.state == State.THINKING:
            dots = "." * (1 + (self.animation_frame // 10) % 3)
            placeholder = self.font_medium.render(f"Generating response{dots}", True, UIColors.PURPLE)
            self.screen.blit(placeholder, (bot_panel.x + 10, bot_panel.y + 50))
        else:
            placeholder = self.font_medium.render("(waiting for response...)", True, UIColors.TEXT_DIM)
            self.screen.blit(placeholder, (bot_panel.x + 10, bot_panel.y + 50))
    
    def _draw_status(self):
        """Draw status bar at bottom."""
        # Status message
        status = self.font_small.render(self.status_message, True, UIColors.TEXT_DIM)
        status_rect = status.get_rect(center=(self.width // 2, self.height - 35))
        self.screen.blit(status, status_rect)
        
        # Instructions
        if self.state == State.WAITING:
            hint = "Say 'Hey Veedatron' to start • Press ESC to exit"
        elif self.state == State.LISTENING:
            hint = "Speak now! Will auto-detect when you stop talking"
        elif self.state == State.FOLLOW_UP:
            remaining = max(0, self.follow_up_timeout - (time.time() - self.follow_up_start_time))
            hint = f"Ask a follow-up question or wait {remaining:.0f}s to exit conversation"
        else:
            hint = "Press ESC to exit"
        
        hint_text = self.font_small.render(hint, True, UIColors.TEXT_DIM)
        hint_rect = hint_text.get_rect(center=(self.width // 2, self.height - 15))
        self.screen.blit(hint_text, hint_rect)
    
    def _draw_wake_word_indicator(self):
        """Draw wake word confidence meter."""
        if self.state != State.WAITING:
            return
        
        x = 50
        y = self.height - 80
        width = 200
        height = 20
        
        # Background
        pygame.draw.rect(self.screen, UIColors.PANEL, (x, y, width, height), 0, 5)
        
        # Confidence bar
        conf_width = int(width * min(self.wake_word_confidence, 1.0))
        if conf_width > 0:
            color = UIColors.SUCCESS if self.wake_word_confidence > self.wake_word_threshold else UIColors.ORANGE
            pygame.draw.rect(self.screen, color, (x, y, conf_width, height), 0, 5)
        
        # Threshold line
        thresh_x = x + int(width * self.wake_word_threshold)
        pygame.draw.line(self.screen, UIColors.TEXT, (thresh_x, y - 3), (thresh_x, y + height + 3), 2)
        
        # Label
        label = self.font_small.render(f"Wake word: {self.wake_word_confidence:.1%}", True, UIColors.TEXT_DIM)
        self.screen.blit(label, (x, y - 22))
    
    def draw(self):
        """Draw the entire UI."""
        # Background with subtle gradient
        self.screen.fill(UIColors.BG)
        
        # Title
        title = self.font_title.render("🤖 Vidatron", True, UIColors.ACCENT)
        title_rect = title.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title, title_rect)
        
        # Draw components
        self._draw_waveform()
        self._draw_state_badge()
        self._draw_face()
        self._draw_conversation()
        self._draw_wake_word_indicator()
        self._draw_status()
        
        # Update animation
        self.animation_frame += 1
        
        pygame.display.flip()
    
    def _calculate_rms(self, audio_chunk):
        """Calculate RMS (volume level) of audio chunk."""
        return np.sqrt(np.mean(audio_chunk ** 2))
    
    def _resample(self, audio, orig_sr, target_sr):
        """Resample audio using proper anti-aliasing filter."""
        if orig_sr == target_sr:
            return audio
        
        # Calculate resampling parameters
        gcd = np.gcd(int(orig_sr), int(target_sr))
        up = int(target_sr) // gcd
        down = int(orig_sr) // gcd
        
        # Use scipy's resample_poly for high-quality resampling with anti-aliasing
        resampled = signal.resample_poly(audio, up, down)
        return resampled.astype(np.float32)
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for continuous audio streaming."""
        if not self.running:
            return
        
        # Get audio (already at 16kHz)
        audio = indata[:, 0].copy()
        self.audio_level = self._calculate_rms(audio)
        
        if self.state == State.WAITING:
            # Feed to wake word detector (needs 16kHz int16)
            audio_int16 = (audio * 32767).astype(np.int16)
            prediction = self.wake_word_model.predict(audio_int16)
            
            # Get the confidence score
            scores = list(prediction.values())
            if scores:
                self.wake_word_confidence = max(scores)
                
                if self.wake_word_confidence >= self.wake_word_threshold:
                    print("🎤 Wake word detected!")
                    self._on_wake_word()
        
        elif self.state == State.LISTENING:
            # Record audio directly (already at 16kHz)
            self.recording_buffer.append(audio.copy())
            
            rms = self.audio_level
            
            # Check if speech has started
            if not self.speech_started and rms > self.silence_threshold * 2:
                self.speech_started = True
                self.speech_start_time = time.time()
                print("  Speech started...")
            
            # Check for silence after speech
            if self.speech_started:
                speech_duration = time.time() - self.speech_start_time
                
                if rms < self.silence_threshold:
                    self.silence_counter += 1
                    silence_time = self.silence_counter * (frames / self.mic_sample_rate)
                    
                    if speech_duration > self.min_speech_duration and silence_time > self.silence_duration:
                        print(f"  Silence detected after {speech_duration:.1f}s of speech")
                        self._on_silence_detected()
                else:
                    self.silence_counter = 0
        
        elif self.state == State.FOLLOW_UP:
            # In follow-up mode: listen for speech without wake word
            rms = self.audio_level
            
            # Check for timeout - go back to waiting if no speech
            if time.time() - self.follow_up_start_time > self.follow_up_timeout:
                print("  Follow-up timeout, returning to wake word mode")
                self.state = State.WAITING
                self.status_message = "Say 'Hey Veedatron' to activate..."
                self.wake_word_model.reset()
                return
            
            # If user starts speaking, switch to listening mode
            if rms > self.silence_threshold * 2:
                print("💬 Follow-up detected!")
                self._start_listening_mode()
    
    def _on_wake_word(self):
        """Called when wake word is detected."""
        self._start_listening_mode()
        self.user_text = ""
        self.bot_response = ""
        # Reset wake word model
        self.wake_word_model.reset()
    
    def _start_listening_mode(self):
        """Start listening for speech (used by both wake word and follow-up)."""
        # Cancel any pending request by incrementing ID
        self.current_request_id += 1
        
        # Stop any audio that's currently playing
        pygame.mixer.stop()
        
        self.state = State.LISTENING
        self.recording_buffer = []
        self.speech_started = False
        self.silence_counter = 0
        self.status_message = "Listening... speak now!"
    
    def _play_filler(self):
        """Play a random filler sound while thinking."""
        if self.filler_sounds:
            filler_path = random.choice(self.filler_sounds)
            try:
                sound = pygame.mixer.Sound(filler_path)
                sound.play()
                # Wait for filler to finish before continuing
                while pygame.mixer.get_busy():
                    time.sleep(0.05)
            except Exception as e:
                print(f"  Filler error: {e}")
    
    def _on_silence_detected(self):
        """Called when silence is detected after speech."""
        if self.state != State.LISTENING or self.processing:
            return
        
        self.processing = True
        self.state = State.THINKING
        self.status_message = "Processing your request..."
        
        # Play filler sound while thinking
        self._play_filler()
        
        # Process in background
        threading.Thread(target=self._process_audio, daemon=True).start()
    
    def _process_audio(self):
        """Process recorded audio."""
        # Capture request ID at start - we'll check this before responding
        my_request_id = self.current_request_id
        
        try:
            if not self.recording_buffer:
                self.state = State.WAITING
                self.status_message = "No audio recorded. Say 'Hey Veedatron' again!"
                self.processing = False
                return
            
            # Concatenate audio (already at 16kHz from resampling in callback)
            audio = np.concatenate(self.recording_buffer)
            duration_sec = len(audio) / self.target_sample_rate
            
            # Debug: check audio stats
            max_val = np.max(np.abs(audio))
            rms = np.sqrt(np.mean(audio ** 2))
            print(f"  Recording: {len(audio)} samples = {duration_sec:.2f}s")
            print(f"  Audio stats: max={max_val:.4f}, rms={rms:.4f}")
            
            # Aggressive normalization - boost quiet audio significantly
            if max_val > 0.001:
                # Normalize to 95% of max range
                audio = audio / max_val * 0.95
            else:
                print("  WARNING: Audio too quiet!")
            
            # Apply a small amount of gain if RMS is low
            audio_rms = np.sqrt(np.mean(audio ** 2))
            if audio_rms < 0.1:
                gain = min(0.3 / audio_rms, 10.0)  # Cap gain at 10x
                audio = np.clip(audio * gain, -1.0, 1.0)
                print(f"  Applied gain: {gain:.1f}x")
            
            # Convert to int16
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Save to temp WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                wav_path = f.name
            
            with wave.open(wav_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.target_sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            # Also save a debug copy
            debug_path = "/tmp/vidatron_last_recording.wav"
            with wave.open(debug_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.target_sample_rate)
                wf.writeframes(audio_int16.tobytes())
            print(f"  Debug WAV saved to: {debug_path}")
            
            # Transcribe with Whisper
            self.status_message = "Transcribing speech..."
            print(f"  Transcribing {len(audio)} samples ({len(audio)/self.target_sample_rate:.1f}s)...")
            
            result = subprocess.run(
                [
                    self.config.whisper_path,
                    '-m', self.config.whisper_model,
                    '-l', 'en',
                    '-ng',  # Disable GPU - fixes Metal memory allocation crash on Mac
                    wav_path  # file as positional argument
                ],
                capture_output=True,
                text=True,
                timeout=60  # CPU mode is slower, allow more time
            )
            
            # Debug: print raw output
            if result.stderr:
                print(f"  Whisper stderr: {result.stderr[:200]}")
            
            # Parse output - strip timestamps like [00:00:00.000 --> 00:00:30.000]
            text = result.stdout.strip()
            
            # Remove timestamp lines (format: [HH:MM:SS.mmm --> HH:MM:SS.mmm])
            text = re.sub(r'\[\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}\]\s*', '', text)
            
            # Remove common artifacts
            for marker in ['[BLANK_AUDIO]', '[MUSIC]', '[NOISE]', '[SILENCE]', '(silence)', '[inaudible]']:
                text = text.replace(marker, '')
            text = text.strip()
            
            os.unlink(wav_path)
            
            if not text:
                self.state = State.WAITING
                self.status_message = "Couldn't understand. Say 'Hey Veedatron' again!"
                self.processing = False
                return
            
            self.user_text = text
            print(f"  You said: {text}")
            self.status_message = "Generating response..."
            
            # Route through AI
            result = self.router.route(text)
            print(f"  Router selected: {result.tool.name} (args: {result.arguments})")
            
            # Get response based on tool type
            if result.tool == ToolType.NONE:
                response = result.response
            elif result.tool == ToolType.TIME:
                response = get_current_time()
            elif result.tool == ToolType.SYSTEM_STATUS:
                response = get_system_status()
            elif result.tool == ToolType.JOKE:
                response = get_joke()
            elif result.tool == ToolType.WEATHER:
                if self.weather:
                    location = result.arguments.get("location") or self.config.local_location or "New York"
                    print(f"  [weather] Checking weather for {location}...")
                    try:
                        response = self.weather.get_weather(location)
                    except Exception as e:
                        print(f"  Weather error: {e}")
                        response = f"Sorry, I couldn't get the weather for {location} right now."
                else:
                    response = "Weather lookup isn't configured. Add OPENWEATHER_API_KEY to enable it."
            elif result.tool == ToolType.NEWS:
                if self.news:
                    category = result.arguments.get("category", "")
                    print(f"  [news] Fetching headlines{' for ' + category if category else ''}...")
                    try:
                        response = self.news.get_news(category)
                    except Exception as e:
                        print(f"  News error: {e}")
                        response = "Sorry, I couldn't get the news right now."
                else:
                    response = "News lookup isn't configured. Add NEWSAPI_KEY to enable it."
            elif result.tool == ToolType.CLOUD:
                if self.cloud:
                    print("  [cloud] Sending to Kimi K2...")
                    response = None
                    
                    # Check for cancellation before slow cloud call
                    if my_request_id != self.current_request_id:
                        print("  ⏹ Request cancelled before cloud call")
                        self.processing = False
                        return
                    
                    # Try cloud with retry
                    for attempt in range(2):
                        try:
                            query = result.arguments.get("query", text)
                            response = self.cloud.chat(query, stream=False)
                            break  # Success!
                        except Exception as e:
                            error_msg = str(e)
                            print(f"  Cloud error (attempt {attempt+1}): {error_msg}")
                            if "429" in error_msg and attempt == 0:
                                # Check for cancellation before waiting
                                if my_request_id != self.current_request_id:
                                    print("  ⏹ Request cancelled during retry wait")
                                    self.processing = False
                                    return
                                print("  Waiting 3 seconds before retry...")
                                time.sleep(3)
                            else:
                                break
                    
                    # If cloud failed, fall back to local model
                    if response is None:
                        # Check cancellation before fallback
                        if my_request_id != self.current_request_id:
                            print("  ⏹ Request cancelled before fallback")
                            self.processing = False
                            return
                        print("  [fallback] Using local model...")
                        try:
                            messages = [
                                {"role": "system", "content": "You are Vidatron, a healthy lifestyle robot and AI assistant. Give a concise answer in 1-3 sentences."},
                                {"role": "user", "content": text}
                            ]
                            local_response = self.ollama.chat(messages, tools=None)
                            response = local_response.content or "I'm not sure about that."
                        except:
                            response = "Sorry, I'm having trouble thinking right now. Try again in a moment."
                else:
                    # No cloud configured - use local model
                    print("  [local fallback] No cloud configured...")
                    try:
                        messages = [
                            {"role": "system", "content": "You are Vidatron, a healthy lifestyle robot and AI assistant. Give a concise answer in 1-3 sentences."},
                            {"role": "user", "content": text}
                        ]
                        local_response = self.ollama.chat(messages, tools=None)
                        response = local_response.content or "I'm not sure about that."
                    except:
                        response = "That's a complex question. I'm having trouble answering right now."
            else:
                response = result.response or "I'm not sure how to respond to that."
            
            # Check if this request was cancelled (user asked a new question)
            if my_request_id != self.current_request_id:
                print("  ⏹ Request cancelled (new question detected)")
                self.processing = False
                return
            
            self.bot_response = response
            print(f"  Bot: {response[:50]}...")
            
            # Speak response
            self.state = State.SPEAKING
            self.status_message = "Speaking response..."
            
            wav_file = self.tts.synthesize(response)
            
            # Check again before playing - user might have interrupted
            if my_request_id != self.current_request_id:
                print("  ⏹ Request cancelled before playback")
                os.unlink(wav_file)
                self.processing = False
                return
            
            # Play audio
            sound = pygame.mixer.Sound(wav_file)
            sound.play()
            
            # Wait for playback (but check for cancellation)
            while pygame.mixer.get_busy():
                if my_request_id != self.current_request_id:
                    print("  ⏹ Stopping playback (new question)")
                    pygame.mixer.stop()
                    break
                time.sleep(0.1)
            
            os.unlink(wav_file)
            
            # Only go to follow-up if this request wasn't cancelled
            if my_request_id == self.current_request_id:
                self.state = State.FOLLOW_UP
                self.follow_up_start_time = time.time()
                self.status_message = "Ask a follow-up question..."
                print("💬 Ready for follow-up (or wait 8s to exit conversation)")
            
            self.processing = False
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            self.state = State.WAITING
            self.status_message = f"Error: {str(e)[:40]}. Try again!"
            self.processing = False
    
    def run(self):
        """Main loop."""
        clock = pygame.time.Clock()
        
        print("\n" + "="*55)
        print("  🤖 Vidatron Voice Assistant - Test Interface")
        print("="*55)
        print("  • Say 'Hey Veedatron' to activate")
        print("  • Speak your command after activation")
        print("  • Ask follow-up questions without wake word!")
        print("  • Wait 8s of silence to end conversation")
        print("  • Press ESC to exit")
        print("="*55 + "\n")
        
        # Start audio stream at mic's native sample rate
        self.stream = sd.InputStream(
            samplerate=self.mic_sample_rate,
            channels=self.channels,
            blocksize=self.chunk_size,
            callback=self._audio_callback,
            dtype='float32'
        )
        self.stream.start()
        print(f"  Audio stream started at {self.mic_sample_rate}Hz")
        
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        # Manual trigger with SPACE (backup)
                        elif event.key == pygame.K_SPACE and self.state == State.WAITING:
                            self._on_wake_word()
                
                self.draw()
                clock.tick(30)
        
        finally:
            self.stream.stop()
            self.stream.close()
            pygame.quit()


def main():
    print("Starting Vidatron Test UI...")
    print("Checking components...")
    
    config = Config.load()
    
    # Check Ollama
    ollama = OllamaClient(model=config.chat_model)
    if not ollama.is_available():
        print("ERROR: Ollama is not running!")
        print("Start it with: ollama serve")
        sys.exit(1)
    print("✓ Ollama connected")
    
    # Check wake word model
    if not Path(config.wake_word_model).exists():
        print(f"ERROR: Wake word model not found: {config.wake_word_model}")
        sys.exit(1)
    print("✓ Wake word model found")
    
    # Check whisper
    if not Path(config.whisper_path).exists():
        print(f"ERROR: Whisper not found: {config.whisper_path}")
        sys.exit(1)
    print("✓ Whisper found")
    
    # Check TTS
    if not Path(config.piper_voice).exists():
        print(f"ERROR: Piper voice not found: {config.piper_voice}")
        sys.exit(1)
    print("✓ Piper TTS found")
    
    print()
    
    ui = TestUI()
    ui.run()


if __name__ == "__main__":
    main()
