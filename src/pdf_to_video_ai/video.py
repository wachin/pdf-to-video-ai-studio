from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


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
                   srt_path: Path | None = None) -> Path:
    """Assemble video with proper synchronization using concat demuxer."""
    audio_files = sorted(audio_dir.glob("audio_*.mp3"))
    if not audio_files:
        raise RuntimeError("No audio files found")

    slides = sorted(slides_dir.glob("slide_*.png"))
    if not slides:
        raise RuntimeError("No slides found")

    if len(audio_files) != len(slides):
        raise RuntimeError(f"Mismatch: {len(audio_files)} audio files vs {len(slides)} slides")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        slides_sorted = sorted(slides_dir.glob("slide_*.png"))
        audio_sorted = sorted(audio_dir.glob("audio_*.mp3"))
        durations = [_get_audio_duration(a) for a in audio_files]
        
        # Create concat list for videos (slides with durations)
        with open(tmpdir_path / "concat_videos.txt", "w") as f:
            for img, dur in zip(slides, durations):
                f.write(f"file '{img.resolve()}'\n")
                f.write(f"duration {dur}\n")
            # Last entry without duration for concat demuxer
            f.write(f"file '{slides[-1].resolve()}'\n")
        
        # Create concat list for audio
        with open(tmpdir_path / "concat_audio.txt", "w") as f:
            for audio in audio_files:
                f.write(f"file '{audio.resolve()}'\n")

        vf = f"scale={orientation.width}:{orientation.height}:force_original_aspect_ratio=decrease,pad={orientation.width}:{orientation.height}:(ow-iw)/2:(oh-ih)/2"
        if srt_path and srt_path.exists():
            vf = f"subtitles='{srt_path.resolve()}',{vf}"

        cmd = [
            "ffmpeg", "-y", "-nostdin",
            "-f", "concat", "-safe", "0", "-i", str(tmpdir_path / "concat_videos.txt"),
            "-f", "concat", "-safe", "0", "-i", str(tmpdir_path / "concat_audio.txt"),
            "-vf", vf,
            "-c:v", "libx264", "-r", "30", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(output_path)
        ]

        output_path.parent.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {result.stderr}")

    return output_path


def assemble_both_orientations(slides_dir: Path, audio_dir: Path,
                               base_output: Path,
                               orientations: list | None = None,
                               srt_path: Path | None = None) -> list[Path]:
    if orientations is None:
        orientations = [VERTICAL, HORIZONTAL]
    outputs = []
    for orient in orientations:
        out_path = base_output.parent / f"{base_output.stem}_{orient.name}{base_output.suffix}"
        assemble_video(slides_dir, audio_dir, out_path, orientation=orient, srt_path=srt_path)
        outputs.append(out_path)
    return outputs