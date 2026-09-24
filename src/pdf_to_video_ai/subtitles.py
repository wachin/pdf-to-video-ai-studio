from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

try:
    import pysrt
except Exception:
    pysrt = None


@dataclass
class SubtitleBlock:
    text: str
    start: float
    duration: float
    source_elements: list[str] = None  # type: ignore


def get_audio_duration(audio_path: Path) -> float:
    """Get actual audio duration using ffprobe."""
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", str(audio_path)
        ], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception:
        return 0.0


def _to_subrip_time(seconds: float) -> pysrt.SubRipTime:
    """Convert seconds to pysrt SubRipTime."""
    if pysrt is None:
        raise RuntimeError("pysrt not installed")
    # from_ordinal takes milliseconds
    return pysrt.SubRipTime.from_ordinal(int(seconds * 1000))


def write_srt(blocks: list[SubtitleBlock], output_path: Path) -> None:
    """Write SRT file using pysrt for robust formatting."""
    if pysrt is None:
        raise RuntimeError("pysrt not installed. Run: pip install pysrt")
    
    subs = pysrt.SubRipFile()
    for i, b in enumerate(blocks, 1):
        start_time = _to_subrip_time(b.start)
        end_time = _to_subrip_time(b.start + b.duration)
        item = pysrt.SubRipItem(
            index=i,
            start=start_time,
            end=end_time,
            text=b.text
        )
        subs.append(item)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subs.save(str(output_path), encoding="utf-8")


def generate_subtitles_from_audio(audio_dir: Path, script_blocks: list, output_path: Path) -> list[SubtitleBlock]:
    """Generate subtitles using actual audio durations from files."""
    audio_files = sorted(audio_dir.glob("audio_*.mp3"))
    subtitles = []
    current_time = 0.0

    for i, (script_blk, audio_file) in enumerate(zip(script_blocks, audio_files)):
        duration = get_audio_duration(audio_file)
        if duration <= 0:
            duration = script_blk.estimated_duration_sec
        subtitles.append(SubtitleBlock(
            text=script_blk.text_narrated,
            start=current_time,
            duration=duration,
            source_elements=getattr(script_blk, 'source_elements', []),
        ))
        current_time += duration

    write_srt(subtitles, output_path)
    return subtitles


def generate_subtitles_from_word_boundaries(audio_dir: Path, script_blocks: list, output_path: Path) -> list[SubtitleBlock]:
    """Generate word-level subtitles using edge-tts WordBoundary data."""
    audio_files = sorted(audio_dir.glob("audio_*.mp3"))
    wb_files = sorted(audio_dir.glob("word_boundaries_*.json"))
    
    if not wb_files or len(wb_files) != len(audio_files):
        # Fallback to block-level subtitles
        return generate_subtitles_from_audio(audio_dir, script_blocks, output_path)
    
    subtitles = []
    current_time = 0.0
    
    for i, (script_blk, audio_file, wb_file) in enumerate(zip(script_blocks, audio_files, wb_files)):
        duration = get_audio_duration(audio_file)
        if duration <= 0:
            duration = script_blk.estimated_duration_sec
        
        # Load word boundaries
        try:
            wb_data = json.loads(wb_file.read_text(encoding="utf-8"))
        except Exception:
            wb_data = []
        
        if wb_data:
            # Create subtitle block for each word
            for wb in wb_data:
                word_text = wb.get("text", "")
                offset = wb.get("offset", 0) / 10_000_000  # edge-tts offset is in 100ns units
                dur = wb.get("duration", 0) / 10_000_000
                if word_text.strip():
                    subtitles.append(SubtitleBlock(
                        text=word_text,
                        start=current_time + offset,
                        duration=dur,
                        source_elements=getattr(script_blk, 'source_elements', []),
                    ))
            current_time += duration
        else:
            # No word boundaries, use block-level
            subtitles.append(SubtitleBlock(
                text=script_blk.text_narrated,
                start=current_time,
                duration=duration,
                source_elements=getattr(script_blk, 'source_elements', []),
            ))
            current_time += duration

    write_srt(subtitles, output_path)
    return subtitles