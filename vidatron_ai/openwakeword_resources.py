"""
Ensure openWakeWord feature ONNX files exist.
"""

from __future__ import annotations

import importlib.util
import urllib.request
from pathlib import Path

_RELEASE = "https://github.com/dscripka/openWakeWord/releases/download/v0.5.1"
_FEATURE_ONNX = {
    "melspectrogram.onnx": f"{_RELEASE}/melspectrogram.onnx",
    "embedding_model.onnx": f"{_RELEASE}/embedding_model.onnx",
}


def _openwakeword_root() -> Path:
    spec = importlib.util.find_spec("openwakeword")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError("openWakeWord is not installed in this environment.")
    return Path(list(spec.submodule_search_locations)[0])


def ensure_openwakeword_feature_models() -> None:
    models_dir = _openwakeword_root() / "resources" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    for fname, url in _FEATURE_ONNX.items():
        dest = models_dir / fname
        if dest.is_file():
            continue
        tmp = dest.with_suffix(dest.suffix + ".part")
        try:
            with urllib.request.urlopen(url, timeout=120) as resp, open(tmp, "wb") as out:
                out.write(resp.read())
            tmp.replace(dest)
        finally:
            if tmp.exists():
                tmp.unlink(missing_ok=True)

    missing = [f for f in _FEATURE_ONNX if not (models_dir / f).is_file()]
    if missing:
        raise RuntimeError("openWakeWord feature models missing: " + ", ".join(missing))


if __name__ == "__main__":
    ensure_openwakeword_feature_models()
    print("openWakeWord resources ready")
