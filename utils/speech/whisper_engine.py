"""
Whisper speech recognition engine wrapper.
Supports whisper.cpp via subprocess and the openai-whisper Python package.
Falls back gracefully if neither is available, returning empty segments.
"""

import os
import json
import subprocess
import shutil
import tempfile
from typing import List, Dict, Optional


def _find_whisper_cpp() -> Optional[str]:
    """Locate the whisper.cpp binary."""
    candidates = [
        "whisper",
        "whisper-cpp",
        "main",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets/whisper/main"),
    ]
    for c in candidates:
        found = shutil.which(c) or (os.path.isfile(c) and os.access(c, os.X_OK))
        if found:
            return c if shutil.which(c) else os.path.abspath(c)
    return None


def _find_model(name: str) -> Optional[str]:
    """Locate a Whisper GGML model file by name."""
    search_dirs = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets/models"),
        os.path.expanduser("~/.cache/whisper"),
        "/data/data/org.offlinedubber/files/models",
    ]
    for d in search_dirs:
        for fname in (f"ggml-{name}.bin", f"{name}.bin"):
            path = os.path.join(d, fname)
            if os.path.isfile(path):
                return path
    return None


class WhisperEngine:
    """
    Offline speech recognition via:
    1. whisper.cpp binary (fastest on Android/ARM)
    2. openai-whisper Python package (fallback)
    3. Empty segments (graceful degradation)
    """

    def __init__(self, model_name: str = "base.en", threads: int = 4):
        self.model_name = model_name
        self.threads = threads
        self._whisper_cpp = _find_whisper_cpp()
        self._model_path = _find_model(model_name)
        self._python_whisper = None
        self._try_load_python_whisper()

    def _try_load_python_whisper(self):
        try:
            import whisper
            self._python_whisper = whisper
        except ImportError:
            self._python_whisper = None

    def transcribe(self, audio_path: str, language: str = "en") -> List[Dict]:
        """
        Transcribe the given WAV file.

        Returns:
            list of {"start": float, "end": float, "text": str}
        """
        if self._whisper_cpp and self._model_path:
            return self._transcribe_cpp(audio_path, language)
        if self._python_whisper:
            return self._transcribe_python(audio_path, language)
        return self._transcribe_fallback(audio_path)

    def _transcribe_cpp(self, audio_path: str, language: str) -> List[Dict]:
        """Use whisper.cpp binary for transcription."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            out_json = tmp.name

        cmd = [
            self._whisper_cpp,
            "-m", self._model_path,
            "-f", audio_path,
            "-l", language,
            "-oj",
            "-of", out_json.replace(".json", ""),
            "-t", str(self.threads),
            "--no-timestamps", "0",
        ]
        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=600
            )
            if result.returncode != 0:
                raise RuntimeError(f"whisper.cpp error: {result.stderr[-1000:]}")

            json_path = out_json.replace(".json", "") + ".json"
            if not os.path.exists(json_path):
                json_path = out_json
            with open(json_path) as f:
                data = json.load(f)
            return self._parse_cpp_output(data)
        except Exception as e:
            raise RuntimeError(f"whisper.cpp transcription failed: {e}") from e
        finally:
            for p in (out_json, out_json.replace(".json", "") + ".json"):
                if os.path.exists(p):
                    os.unlink(p)

    def _parse_cpp_output(self, data: dict) -> List[Dict]:
        """Parse the JSON output from whisper.cpp."""
        segments = []
        for seg in data.get("transcription", []):
            offsets = seg.get("offsets", {})
            start_ms = offsets.get("from", 0)
            end_ms = offsets.get("to", 0)
            text = seg.get("text", "").strip()
            if text:
                segments.append({
                    "start": start_ms / 1000.0,
                    "end": end_ms / 1000.0,
                    "text": text,
                })
        return segments

    def _transcribe_python(self, audio_path: str, language: str) -> List[Dict]:
        """Use the openai-whisper Python package."""
        model = self._python_whisper.load_model(self.model_name)
        result = model.transcribe(audio_path, language=language, fp16=False)
        return [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            }
            for seg in result.get("segments", [])
            if seg.get("text", "").strip()
        ]

    def _transcribe_fallback(self, audio_path: str) -> List[Dict]:
        """Return a single placeholder segment when no engine is available."""
        try:
            from utils.ffmpeg.ffmpeg_utils import FFmpegUtils
            duration = FFmpegUtils.get_duration(audio_path)
        except Exception:
            duration = 10.0
        return [
            {
                "start": 0.0,
                "end": min(duration, 5.0),
                "text": "[No speech recognition engine found — install whisper.cpp or openai-whisper]",
            }
        ]

    def is_available(self) -> bool:
        """Return True if at least one transcription backend is available."""
        return bool(self._whisper_cpp and self._model_path) or bool(self._python_whisper)

    def list_available_models(self):
        """Return a list of installed Whisper model names."""
        found = []
        model_names = [
            "tiny", "tiny.en", "base", "base.en",
            "small", "small.en", "medium", "medium.en", "large",
        ]
        for name in model_names:
            if _find_model(name):
                found.append(name)
        return found
