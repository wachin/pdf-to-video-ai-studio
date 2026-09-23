from __future__ import annotations

import json
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


def _get_audio_duration(audio_path: Path) -> float:
    """Get audio duration using ffprobe."""
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(audio_path)
    ], capture_output=True, text=True, check=True)
    return float(json.loads(probe.stdout)["format"]["duration"])


@dataclass
class Orientation:
    name: str
    width: int
    height: int


VERTICAL = Orientation("vertical", 1080, 1920)
HORIZONTAL = Orientation("horizontal", 1920, 1080)


def assemble_video(slides_dir: Path, audio_dir: Path, output_path: Path,
                   orientation: Orientation = VERTICAL,
                   srt_path: Optional[Path] = None) -> Path:
    """Assemble video with proper synchronization: each slide duration matches its audio block."""
    audio_files = sorted(audio_dir.glob("audio_*.mp3"))
    if not audio_files:
        raise RuntimeError("No audio files found")

    slides = sorted(slides_dir.glob("slide_*.png"))
    if not slides:
        raise RuntimeError("No slides found")

    if len(audio_files) != len(slides):
        raise RuntimeError(f"Mismatch: {len(audio_files)} audio files vs {len(slides)} slides")

    cmd = ["ffmpeg", "-y"]

    for i, img in enumerate(slides):
        duration = _get_audio_duration(audio_files[i])
        cmd.extend(["-loop", "1", "-framerate", "30", "-t", str(duration), "-i", str(img)])

    for audio_file in audio_files:
        cmd.extend(["-i", str(audio_file)])

    n_slides = len(slides)
    n_audio = len(audio_files)

    video_inputs = "".join(f"[{i}:v]" for i in range(n_slides))
    audio_inputs = "".join(f"[{n_slides + i}:a]" for i in range(n_audio))

    filter_parts = []
    filter_parts.append(f"{video_inputs}concat=n={n_slides}:v=1:a=0[v]")
    filter_parts.append(f"{audio_inputs}concat=n={n_audio}:v=0:a=1[a]")

    vf = f"scale={orientation.width}:{orientation.height}:force_original_aspect_ratio=decrease,pad={orientation.width}:{orientation.height}:(ow-iw)/2:(oh-ih)/2"
    if srt_path and srt_path.exists():
        filter_parts.append(f"[v]subtitles='{srt_path.resolve()}',{vf}[vout]")
    else:
        filter_parts.append(f"[v]{vf}[vout]")

    filter_complex = ";".join(filter_parts)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = ["ffmpeg", "-y"]

    for i, img in enumerate(slides):
        duration = _get_audio_duration(audio_files[i])
        cmd.extend(["-loop", "1", "-framerate", "30", "-t", str(duration), "-i", str(img)])

    for audio_file in audio_files:
        cmd.extend(["-i", str(audio_file)])

    n_slides = len(slides)
    n_audio = len(audio_files)

    video_inputs = "".join(f"[{i}:v]" for i in range(n_slides))
    audio_inputs = "".join(f"[{n_slides + i}:a]" for i in range(n_audio))

    filter_parts = []
    filter_parts.append(f"{video_inputs}concat=n={n_slides}:v=1:a=0[v]")
    filter_parts.append(f"{audio_inputs}concat=n={n_audio}:v=0:a=1[a]")

    vf = f"scale={orientation.width}:{orientation.height}:force_original_aspect_ratio=decrease,pad={orientation.width}:{orientation.height}:(ow-iw)/2:(oh-ih)/2"
    if srt_path and srt_path.exists():
        filter_parts.append(f"[v]subtitles='{srt_path.resolve()}',{vf}[vout]")
    else:
        filter_parts.append(f"[v]{vf}[vout]")

    filter_complex = ";".join(filter_parts)

    cmd.extend(["-filter_complex", filter_complex])
    cmd.extend(["-map", "[vout]", "-map", "[a]"])
    cmd.extend(["-c:v", "libx264", "-r", "30", "-pix_fmt", "yuv420p"])
    cmd.extend(["-c:a", "aac", "-b:a", "192k"])
    cmd.extend(["-shortest", str(output_path)])

    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")

    return output_path


def assemble_both_orientations(slides_dir: Path, audio_dir: Path,
                               base_output: Path,
                               orientations: Optional[List[Orientation]] = None,
                               srt_path: Optional[Path] = None) -> List[Path]:
    if orientations is None:
        orientations = [VERTICAL, HORIZONTAL]
    outputs = []
    for orient in orientations:
        out_path = base_output.parent / f"{base_output.stem}_{orient.name}{base_output.suffix}"
        assemble_video(slides_dir, audio_dir, out_path, orientation=orient, srt_path=srt_path)
        outputs.append(out_path)
    return outputs