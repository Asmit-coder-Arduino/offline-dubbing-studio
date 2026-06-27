"""
Video utility helpers for metadata reading, format detection, and batch operations.
"""

import os
import glob
from typing import List, Dict, Optional, Tuple

SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".3gp", ".flv"}
SUPPORTED_AUDIO_EXTENSIONS = {".aac", ".wav", ".flac", ".mp3", ".ogg", ".m4a"}


class VideoUtils:
    """Utility class for video file operations."""

    @staticmethod
    def is_video(path: str) -> bool:
        """Return True if the file is a supported video format."""
        return os.path.splitext(path)[1].lower() in SUPPORTED_VIDEO_EXTENSIONS

    @staticmethod
    def is_audio(path: str) -> bool:
        """Return True if the file is a supported audio format."""
        return os.path.splitext(path)[1].lower() in SUPPORTED_AUDIO_EXTENSIONS

    @staticmethod
    def scan_directory(directory: str, recursive: bool = False) -> List[str]:
        """
        Scan a directory for video files.

        Args:
            directory: Path to scan.
            recursive: If True, scan subdirectories as well.

        Returns:
            Sorted list of absolute video file paths.
        """
        found = []
        if recursive:
            for ext in SUPPORTED_VIDEO_EXTENSIONS:
                pattern = os.path.join(directory, "**", f"*{ext}")
                found.extend(glob.glob(pattern, recursive=True))
        else:
            for name in os.listdir(directory):
                full = os.path.join(directory, name)
                if os.path.isfile(full) and VideoUtils.is_video(full):
                    found.append(full)
        return sorted(set(found))

    @staticmethod
    def get_thumbnail_path(video_path: str, cache_dir: str) -> str:
        """
        Generate a thumbnail from a video and return the path.
        Creates the thumbnail if it does not yet exist.
        """
        import hashlib
        vid_hash = hashlib.md5(video_path.encode()).hexdigest()[:12]
        thumb_path = os.path.join(cache_dir, f"thumb_{vid_hash}.jpg")
        if not os.path.isfile(thumb_path):
            try:
                from utils.ffmpeg.ffmpeg_utils import FFmpegUtils, _ffmpeg_bin, _run
                cmd = [
                    _ffmpeg_bin(), "-y",
                    "-i", video_path,
                    "-ss", "00:00:01",
                    "-vframes", "1",
                    "-q:v", "3",
                    "-vf", "scale=320:-1",
                    thumb_path,
                ]
                _run(cmd, check=False)
            except Exception:
                pass
        return thumb_path

    @staticmethod
    def estimate_output_size(video_path: str, video_bitrate_kbps: int = 4000,
                              audio_bitrate_kbps: int = 192,
                              duration: Optional[float] = None) -> int:
        """
        Estimate the output file size in bytes given target bitrates.

        Args:
            video_path: Path to the source video.
            video_bitrate_kbps: Target video bitrate in kilobits per second.
            audio_bitrate_kbps: Target audio bitrate in kilobits per second.
            duration: Override duration in seconds (uses source duration if None).

        Returns:
            Estimated size in bytes.
        """
        if duration is None:
            try:
                from utils.ffmpeg.ffmpeg_utils import FFmpegUtils
                duration = FFmpegUtils.get_duration(video_path)
            except Exception:
                duration = 60.0
        total_kbps = video_bitrate_kbps + audio_bitrate_kbps
        return int(total_kbps * 1000 / 8 * duration)

    @staticmethod
    def build_batch_queue(paths: List[str]) -> List[Dict]:
        """
        Build a processing queue for batch dubbing.

        Args:
            paths: List of video file paths.

        Returns:
            List of job dicts with "path", "status", "progress", "error" keys.
        """
        return [
            {
                "path": p,
                "name": os.path.basename(p),
                "status": "queued",
                "progress": 0,
                "error": None,
                "output": None,
            }
            for p in paths
            if VideoUtils.is_video(p)
        ]

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Remove unsafe characters from a filename."""
        import re
        name = re.sub(r'[\\/*?:"<>|]', "_", name)
        name = name.strip(". ")
        return name or "output"

    @staticmethod
    def free_disk_space(path: str) -> int:
        """Return free disk space in bytes at the given path."""
        stat = os.statvfs(path)
        return stat.f_bavail * stat.f_frsize

    @staticmethod
    def has_audio_track(video_path: str) -> bool:
        """Return True if the video file has at least one audio stream."""
        try:
            from utils.ffmpeg.ffmpeg_utils import FFmpegUtils
            info = FFmpegUtils.get_video_info(video_path)
            return "audio_codec" in info
        except Exception:
            return False

    @staticmethod
    def get_resolution(video_path: str) -> Optional[Tuple[int, int]]:
        """Return the (width, height) of the video, or None on error."""
        try:
            from utils.ffmpeg.ffmpeg_utils import FFmpegUtils
            info = FFmpegUtils.get_video_info(video_path)
            w = info.get("width")
            h = info.get("height")
            if w and h:
                return (int(w), int(h))
        except Exception:
            pass
        return None
