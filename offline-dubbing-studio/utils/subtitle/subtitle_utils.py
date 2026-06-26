"""
Subtitle utilities — read/write SRT, adjust timing, merge, split.
"""

import re
import os
from typing import List, Optional


def _seconds_to_srt(s: float) -> str:
    """Convert fractional seconds to SRT timestamp (HH:MM:SS,mmm)."""
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int(round((s - int(s)) * 1000))
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def _srt_to_seconds(ts: str) -> float:
    """Parse an SRT timestamp string to fractional seconds."""
    ts = ts.strip().replace(",", ".")
    parts = ts.split(":")
    if len(parts) == 3:
        h, m, rest = parts
        return float(h) * 3600 + float(m) * 60 + float(rest)
    if len(parts) == 2:
        m, rest = parts
        return float(m) * 60 + float(rest)
    return float(ts)


class SubtitleSegment:
    """A single subtitle segment with index, timing, and text."""

    def __init__(self, index: int, start: float, end: float, text: str):
        self.index = index
        self.start = start
        self.end = end
        self.text = text

    def __repr__(self):
        return (
            f"SubtitleSegment(#{self.index}, "
            f"{_seconds_to_srt(self.start)} --> {_seconds_to_srt(self.end)}, "
            f"{self.text!r})"
        )


class SubtitleUtils:
    """Static methods for subtitle file operations."""

    @staticmethod
    def write_srt(segments, path: str) -> str:
        """
        Write a list of subtitle segments (SubtitleSegment or compatible dict)
        to an SRT file.
        """
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        lines = []
        for i, seg in enumerate(segments, start=1):
            if hasattr(seg, "start"):
                start, end, text = seg.start, seg.end, seg.text
            else:
                start, end, text = seg["start"], seg["end"], seg["text"]
            lines.append(str(i))
            lines.append(f"{_seconds_to_srt(start)} --> {_seconds_to_srt(end)}")
            lines.append(text.strip())
            lines.append("")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path

    @staticmethod
    def read_srt(path: str) -> List[SubtitleSegment]:
        """Parse an SRT file and return a list of SubtitleSegment objects."""
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()

        segments = []
        blocks = re.split(r"\n{2,}", content.strip())
        for block in blocks:
            lines = block.strip().splitlines()
            if len(lines) < 3:
                continue
            try:
                index = int(lines[0].strip())
            except ValueError:
                continue
            time_match = re.match(
                r"(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}[,\.]\d{3})",
                lines[1].strip(),
            )
            if not time_match:
                continue
            start = _srt_to_seconds(time_match.group(1))
            end = _srt_to_seconds(time_match.group(2))
            text = "\n".join(lines[2:]).strip()
            segments.append(SubtitleSegment(index, start, end, text))
        return segments

    @staticmethod
    def shift_timing(segments: List[SubtitleSegment], offset: float) -> List[SubtitleSegment]:
        """Shift all subtitle timings by `offset` seconds."""
        shifted = []
        for seg in segments:
            shifted.append(
                SubtitleSegment(seg.index, max(0, seg.start + offset), max(0, seg.end + offset), seg.text)
            )
        return shifted

    @staticmethod
    def scale_timing(segments: List[SubtitleSegment], factor: float) -> List[SubtitleSegment]:
        """Scale all subtitle timings by `factor` (e.g. 0.9 to speed up)."""
        return [
            SubtitleSegment(seg.index, seg.start * factor, seg.end * factor, seg.text)
            for seg in segments
        ]

    @staticmethod
    def merge_short_segments(
        segments: List[SubtitleSegment],
        min_duration: float = 1.0,
        max_gap: float = 0.3,
    ) -> List[SubtitleSegment]:
        """
        Merge adjacent short segments that are close together in time.
        Helps prevent overly fragmented subtitles.
        """
        if not segments:
            return []
        merged = [segments[0]]
        for seg in segments[1:]:
            last = merged[-1]
            gap = seg.start - last.end
            duration = last.end - last.start
            if gap <= max_gap and duration < min_duration:
                merged[-1] = SubtitleSegment(
                    last.index, last.start, seg.end, f"{last.text} {seg.text}"
                )
            else:
                merged.append(seg)
        for i, seg in enumerate(merged, start=1):
            seg.index = i
        return merged

    @staticmethod
    def split_long_segments(
        segments: List[SubtitleSegment], max_chars: int = 80
    ) -> List[SubtitleSegment]:
        """Split subtitle segments whose text exceeds max_chars into two lines."""
        result = []
        for seg in segments:
            text = seg.text
            if len(text) <= max_chars:
                result.append(seg)
                continue
            midpoint = len(text) // 2
            split_at = text.rfind(" ", 0, midpoint)
            if split_at == -1:
                split_at = midpoint
            mid_time = seg.start + (seg.end - seg.start) * (split_at / len(text))
            result.append(SubtitleSegment(seg.index, seg.start, mid_time, text[:split_at].strip()))
            result.append(SubtitleSegment(seg.index + 1, mid_time, seg.end, text[split_at:].strip()))
        for i, seg in enumerate(result, start=1):
            seg.index = i
        return result

    @staticmethod
    def clean_text(segments: List[SubtitleSegment]) -> List[SubtitleSegment]:
        """Remove leading/trailing whitespace and repeated spaces from subtitle text."""
        cleaned = []
        for seg in segments:
            text = re.sub(r"\s+", " ", seg.text).strip()
            if text:
                cleaned.append(SubtitleSegment(seg.index, seg.start, seg.end, text))
        for i, seg in enumerate(cleaned, start=1):
            seg.index = i
        return cleaned
