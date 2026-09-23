from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

try:
    import edge_tts
except Exception:
    edge_tts = None

from .cache import CacheManager, CacheKey


@dataclass
class TTSResult:
    audio_path: Path
    word_boundaries: List[dict]


def _tts_cache_key(text: str, voice: str, rate: str, volume: str) -> str:
    """Generate cache key from TTS parameters."""
    data = f"{text}|{voice}|{rate}|{volume}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


async def synthesize(
    text: str,
    output_path: Path,
    voice: str = "es-ES-ElviraNeural",
    rate: str = "+0%",
    volume: str = "+0dB",
    cache_dir: Path | None = None,
) -> TTSResult:
    if not edge_tts:
        raise RuntimeError("edge-tts not installed")

    # Check cache
    cache_key = _tts_cache_key(text, voice, rate, volume)
    cache = CacheManager(cache_dir) if cache_dir else CacheManager(
        Path.home() / ".pdf_to_video_ai_cache" / "tts"
    )

    # Use internal index lookup
    found = False
    cached_path = None
    for entry_key, entry in cache._index.items():
        if entry.key.hash() == cache_key:
            found = True
            cached_path = Path(entry.value)
            break

    if found and cached_path and cached_path.exists():
        # Return cached result
        wb_path = cache.cache_dir / f"{cache_key}_wb.json"
        word_boundaries = []
        if wb_path.exists():
            word_boundaries = json.loads(wb_path.read_text())
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path != cached_path:
            output_path.write_bytes(cached_path.read_bytes())
        return TTSResult(audio_path=output_path, word_boundaries=word_boundaries)

    # Generate TTS
    communicate = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    word_boundaries = []
    with output_path.open("wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                word_boundaries.append({
                    "text": chunk["text"],
                    "offset": chunk["offset"],
                    "duration": chunk["duration"],
                })

    # Store in cache
    cache.put(
        CacheKey(input_hash=cache_key, config_hash=cache_key, operation="tts"),
        str(output_path),
    )
    wb_path = cache.cache_dir / f"{cache_key}_wb.json"
    wb_path.write_text(json.dumps(word_boundaries, ensure_ascii=False), encoding="utf-8")

    return TTSResult(audio_path=output_path, word_boundaries=word_boundaries)