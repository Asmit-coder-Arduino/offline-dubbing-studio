"""
FFmpeg utility wrapper for all video and audio operations.
Handles extraction, merging, subtitle embedding, and compression.
"""

import os
import subprocess
import shutil
import json
import tempfile
from typing import List, Dict


def _ffmpeg_bin() -> str:
    """Return path to the ffmpeg binary, searching common locations."""
    candidates = [
        "ffmpeg",
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets/ffmpeg/ffmpeg"),
    ]
    for c in candidates:
        if shutil.which(c) or (os.path.isfile(c) and os.access(c, os.X_OK)):
            return c
    raise FileNotFoundError(
        "ffmpeg not found. Install it or bundle it in assets/ffmpeg/ffmpeg."
    )


def _run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess command, capturing output."""
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg command failed (exit {result.returncode}):\n"
            f"CMD: {' '.join(cmd)}\n"
            f"STDERR: {result.stderr[-2000:]}"
        )
    return result


class FFmpegUtils:
    """Static helper class for all FFmpeg operations."""

    @staticmethod
    def get_duration(path: str) -> float:
        """Return the duration of a media file in seconds."""
        ff = _ffmpeg_bin().replace("ffmpeg", "ffprobe")
        if not (shutil.which(ff) or os.path.isfile(ff)):
            ff = "ffprobe"
        cmd = [
            ff, "-v", "quiet", "-print_format", "json",
            "-show_format", path,
        ]
        result = _run(cmd)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])

    @staticmethod
    def extract_audio(video_path: str, output_wav: str) -> str:
        """Extract audio from a video file to a 16kHz mono WAV (optimal for Whisper)."""
        cmd = [
            _ffmpeg_bin(), "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            output_wav,
        ]
        _run(cmd)
        return output_wav

    @staticmethod
    def replace_audio(video_path: str, audio_path: str, output_path: str) -> str:
        """Replace the audio track of a video with a new audio file."""
        cmd = [
            _ffmpeg_bin(), "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_path,
        ]
        _run(cmd)
        return output_path

    @staticmethod
    def add_subtitles(video_path: str, srt_path: str, output_path: str) -> str:
        """Embed SRT subtitles as a soft subtitle track in the output MP4."""
        cmd = [
            _ffmpeg_bin(), "-y",
            "-i", video_path,
            "-i", srt_path,
            "-c:v", "copy",
            "-c:a", "copy",
            "-c:s", "mov_text",
            "-metadata:s:s:0", "language=eng",
            output_path,
        ]
        _run(cmd)
        return output_path

    @staticmethod
    def compress_output(input_path: str, output_path: str,
                        video_bitrate: str = "4000k",
                        audio_bitrate: str = "192k") -> str:
        """Re-encode the video at the specified bitrate for final delivery."""
        cmd = [
            _ffmpeg_bin(), "-y",
            "-i", input_path,
            "-c:v", "libx264",
            "-b:v", video_bitrate,
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-movflags", "+faststart",
            output_path,
        ]
        _run(cmd)
        return output_path

    @staticmethod
    def build_silence_padded_audio(
        segments: List[Dict], output_path: str, total_duration: float
    ) -> str:
        """
        Construct a full-length audio track by placing each dubbed segment at
        its correct timestamp, padding with silence between them.

        Args:
            segments: list of {"path": wav_path, "start": float, "end": float}
            output_path: destination WAV file
            total_duration: total duration of the video in seconds
        """
        SAMPLE_RATE = 44100
        CHANNELS = 2

        inputs = []
        filter_parts = []

        for i, seg in enumerate(segments):
            inputs += ["-i", seg["path"]]
            duration = seg["end"] - seg["start"]
            filter_parts.append(
                f"[{i}:a]atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,"
                f"adelay={int(seg['start'] * 1000)}|{int(seg['start'] * 1000)}[s{i}]"
            )

        if not segments:
            silence_duration = max(1, int(total_duration))
            cmd = [
                _ffmpeg_bin(), "-y",
                "-f", "lavfi",
                "-i", f"anullsrc=r={SAMPLE_RATE}:cl=stereo:d={silence_duration}",
                "-t", str(total_duration),
                output_path,
            ]
            _run(cmd)
            return output_path

        n = len(segments)
        mix_inputs = "".join(f"[s{i}]" for i in range(n))
        filter_parts.append(
            f"{mix_inputs}amix=inputs={n}:normalize=0,atrim=0:{total_duration:.3f}[out]"
        )
        filter_complex = ";".join(filter_parts)

        cmd = (
            [_ffmpeg_bin(), "-y"]
            + inputs
            + [
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-c:a", "pcm_s16le",
                "-ar", str(SAMPLE_RATE),
                "-ac", str(CHANNELS),
                output_path,
            ]
        )
        _run(cmd)
        return output_path

    @staticmethod
    def normalize_audio(input_path: str, output_path: str) -> str:
        """Normalize audio loudness using the loudnorm filter (EBU R128)."""
        cmd = [
            _ffmpeg_bin(), "-y",
            "-i", input_path,
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            output_path,
        ]
        _run(cmd)
        return output_path

    @staticmethod
    def remove_silence(input_path: str, output_path: str,
                        threshold_db: float = -50.0,
                        min_silence_s: float = 0.3) -> str:
        """Remove silent sections from an audio file."""
        cmd = [
            _ffmpeg_bin(), "-y",
            "-i", input_path,
            "-af", (
                f"silenceremove=stop_periods=-1"
                f":stop_duration={min_silence_s}"
                f":stop_threshold={threshold_db}dB"
            ),
            output_path,
        ]
        _run(cmd)
        return output_path

    @staticmethod
    def trim_video(input_path: str, start: float, end: float, output_path: str) -> str:
        """Trim a video to the given start/end time range."""
        duration = end - start
        cmd = [
            _ffmpeg_bin(), "-y",
            "-ss", str(start),
            "-i", input_path,
            "-t", str(duration),
            "-c:v", "copy",
            "-c:a", "copy",
            output_path,
        ]
        _run(cmd)
        return output_path

    @staticmethod
    def resize_video(input_path: str, width: int, height: int, output_path: str) -> str:
        """Resize a video to the given dimensions."""
        cmd = [
            _ffmpeg_bin(), "-y",
            "-i", input_path,
            "-vf", f"scale={width}:{height}:flags=lanczos",
            "-c:a", "copy",
            output_path,
        ]
        _run(cmd)
        return output_path

    @staticmethod
    def get_video_info(path: str) -> Dict:
        """Return basic video metadata as a dict."""
        ff = _ffmpeg_bin().replace("ffmpeg", "ffprobe")
        if not (shutil.which(ff) or os.path.isfile(ff)):
            ff = "ffprobe"
        cmd = [
            ff, "-v", "quiet", "-print_format", "json",
            "-show_streams", "-show_format", path,
        ]
        result = _run(cmd)
        data = json.loads(result.stdout)
        info = {
            "duration": float(data["format"].get("duration", 0)),
            "size": int(data["format"].get("size", 0)),
            "bitrate": int(data["format"].get("bit_rate", 0)),
        }
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                info["width"] = stream.get("width")
                info["height"] = stream.get("height")
                info["fps"] = stream.get("avg_frame_rate", "0/1")
                info["video_codec"] = stream.get("codec_name")
            elif stream.get("codec_type") == "audio":
                info["audio_codec"] = stream.get("codec_name")
                info["sample_rate"] = stream.get("sample_rate")
                info["channels"] = stream.get("channels")
        return info

    @staticmethod
    def extract_background_music(video_path: str, speech_path: str,
                                  output_path: str) -> str:
        """
        Attempt to isolate background music by subtracting the speech track.
        Uses the `pan` filter to reduce center-channel (speech) content.
        """
        cmd = [
            _ffmpeg_bin(), "-y",
            "-i", video_path,
            "-af", "pan=stereo|c0=c0-0.5*FC|c1=c1-0.5*FC",
            output_path,
        ]
        _run(cmd)
        return output_path

    @staticmethod
    def merge_background_music(dubbed_path: str, bg_music_path: str,
                                output_path: str, bg_volume: float = 0.3) -> str:
        """Mix background music at a lower volume under the dubbed audio."""
        cmd = [
            _ffmpeg_bin(), "-y",
            "-i", dubbed_path,
            "-i", bg_music_path,
            "-filter_complex",
            f"[1:a]volume={bg_volume}[bg];[0:a][bg]amix=inputs=2:normalize=0[out]",
            "-map", "0:v",
            "-map", "[out]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path,
        ]
        _run(cmd)
        return output_path
