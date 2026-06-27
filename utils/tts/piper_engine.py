"""
Piper TTS engine wrapper for offline neural text-to-speech synthesis.
Uses the piper binary (or piper-tts Python package) to generate audio.
"""

import os
import json
import shutil
import subprocess
import tempfile
from typing import Optional, List, Dict


def _find_piper_bin() -> Optional[str]:
    """Locate the piper TTS binary."""
    candidates = [
        "piper",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets/piper/piper"),
        "/data/data/org.offlinedubber/files/piper/piper",
    ]
    for c in candidates:
        found = shutil.which(c) or (os.path.isfile(c) and os.access(c, os.X_OK))
        if found:
            return c if shutil.which(c) else os.path.abspath(c)
    return None


def _find_voice_model(voice_id: str) -> Optional[str]:
    """Locate a Piper voice model (.onnx) file."""
    search_dirs = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets/models/piper"),
        os.path.expanduser("~/.local/share/piper"),
        "/data/data/org.offlinedubber/files/models/piper",
    ]
    for d in search_dirs:
        for fname in (f"{voice_id}.onnx", f"{voice_id}"):
            path = os.path.join(d, fname)
            if os.path.isfile(path):
                return path
    return None


class PiperEngine:
    """
    Offline TTS via:
    1. Piper binary (fastest, recommended for Android)
    2. piper-tts Python package (fallback)
    3. espeak-ng via subprocess (last resort)
    4. Silent WAV generation (graceful degradation)
    """

    def __init__(self):
        self._piper_bin = _find_piper_bin()
        self._python_piper = None
        self._try_load_python_piper()

    def _try_load_python_piper(self):
        try:
            from piper import PiperVoice
            self._python_piper = PiperVoice
        except ImportError:
            self._python_piper = None

    def synthesize(self, text: str, voice_id: str, output_wav: str,
                   speed: float = 1.0) -> str:
        """
        Synthesize speech from text and write it to output_wav.

        Args:
            text: The text to convert to speech.
            voice_id: The Piper voice model ID (e.g. "en_US-amy-medium").
            output_wav: Path to the output WAV file.
            speed: Speaking rate multiplier (1.0 = normal).

        Returns:
            The path to the generated WAV file.
        """
        model_path = _find_voice_model(voice_id)

        if self._piper_bin and model_path:
            return self._synthesize_binary(text, model_path, output_wav, speed)
        if self._python_piper and model_path:
            return self._synthesize_python(text, model_path, output_wav, speed)
        return self._synthesize_espeak(text, output_wav)

    def _synthesize_binary(self, text: str, model_path: str,
                            output_wav: str, speed: float) -> str:
        """Call the piper binary via stdin → WAV file."""
        config_path = model_path + ".json"
        cmd = [
            self._piper_bin,
            "--model", model_path,
            "--output_file", output_wav,
            "--length_scale", str(1.0 / speed),
        ]
        if os.path.isfile(config_path):
            cmd += ["--config", config_path]

        result = subprocess.run(
            cmd,
            input=text,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"piper synthesis failed (exit {result.returncode}):\n{result.stderr[-1000:]}"
            )
        return output_wav

    def _synthesize_python(self, text: str, model_path: str,
                            output_wav: str, speed: float) -> str:
        """Use the piper-tts Python package."""
        import wave
        voice = self._python_piper.load(model_path)
        with wave.open(output_wav, "w") as wf:
            voice.synthesize(text, wf, length_scale=1.0 / speed)
        return output_wav

    def _synthesize_espeak(self, text: str, output_wav: str) -> str:
        """Fallback: use espeak-ng if piper is not available."""
        espeak = shutil.which("espeak-ng") or shutil.which("espeak")
        if espeak:
            cmd = [espeak, "-w", output_wav, text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return output_wav

        return self._write_silence(output_wav, duration=max(1, len(text.split()) // 2))

    def _write_silence(self, output_wav: str, duration: float = 1.0) -> str:
        """Write a silent WAV file of the given duration as absolute last resort."""
        import wave, struct
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        with wave.open(output_wav, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(struct.pack(f"<{n_samples}h", *([0] * n_samples)))
        return output_wav

    def is_available(self) -> bool:
        """Return True if at least one synthesis backend is available."""
        return bool(self._piper_bin) or bool(self._python_piper)

    def list_installed_voices(self) -> List[str]:
        """Return a list of installed voice model IDs."""
        search_dirs = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets/models/piper"),
            os.path.expanduser("~/.local/share/piper"),
            "/data/data/org.offlinedubber/files/models/piper",
        ]
        voices = []
        for d in search_dirs:
            if not os.path.isdir(d):
                continue
            for fname in os.listdir(d):
                if fname.endswith(".onnx"):
                    voices.append(fname.replace(".onnx", ""))
        return voices

    def get_voice_config(self, voice_id: str) -> Optional[Dict]:
        """Load the JSON config for a Piper voice model."""
        model_path = _find_voice_model(voice_id)
        if not model_path:
            return None
        config_path = model_path + ".json"
        if not os.path.isfile(config_path):
            return None
        with open(config_path) as f:
            return json.load(f)
