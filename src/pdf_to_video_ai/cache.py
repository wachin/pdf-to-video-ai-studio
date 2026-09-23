"""Cache management with invalidation support.

Provides a file-based cache for expensive operations:
- TTS audio (keyed by text + voice + rate + volume + backend_version)
- OCR results (keyed by page image hash + engine version)
- Extraction results (keyed by input file hash + engine versions)
- Script results (keyed by document hash + config hash)

Cache invalidation occurs when:
- Input file hash changes
- Configuration hash changes
- Engine version changes
- Model version changes
"""

from __future__ import annotations

import json
import hashlib
import pickle
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field


@dataclass
class CacheKey:
    """Composite cache key for invalidation."""

    input_hash: str
    config_hash: str
    engine_versions: dict[str, str] = field(default_factory=dict)
    operation: str = ""

    def to_string(self) -> str:
        """Serialize key to a deterministic string."""
        parts = [
            self.input_hash,
            self.config_hash,
            self.operation,
        ]
        for k, v in sorted(self.engine_versions.items()):
            parts.append(f"{k}={v}")
        return "|".join(parts)

    def hash(self) -> str:
        """Generate SHA256 hash of the cache key."""
        return hashlib.sha256(self.to_string().encode()).hexdigest()[:32]


@dataclass
class CacheEntry:
    """Cached result with metadata."""

    key: CacheKey
    value: Any
    created_at: str = ""
    expires_at: str = ""


class CacheManager:
    """Manages file-based cache with invalidation."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index: dict[str, CacheEntry] = {}
        self._load_index()

    def _index_path(self) -> Path:
        return self.cache_dir / "cache_index.json"

    def _load_index(self) -> None:
        """Load cache index from disk."""
        if self._index_path().exists():
            try:
                data = json.loads(self._index_path().read_text())
                for key_str, entry_data in data.items():
                    key = CacheKey(
                        input_hash=entry_data["input_hash"],
                        config_hash=entry_data["config_hash"],
                        engine_versions=entry_data.get("engine_versions", {}),
                        operation=entry_data.get("operation", ""),
                    )
                    self._index[key_str] = CacheEntry(
                        key=key,
                        value=entry_data.get("value"),
                        created_at=entry_data.get("created_at", ""),
                        expires_at=entry_data.get("expires_at", ""),
                    )
            except (json.JSONDecodeError, KeyError):
                self._index = {}

    def _save_index(self) -> None:
        """Save cache index to disk."""
        data = {}
        for key_str, entry in self._index.items():
            data[key_str] = {
                "input_hash": entry.key.input_hash,
                "config_hash": entry.key.config_hash,
                "engine_versions": entry.key.engine_versions,
                "operation": entry.key.operation,
                "value": entry.value,
                "created_at": entry.created_at,
                "expires_at": entry.expires_at,
            }
        self._index_path().write_text(
            json.dumps(data, indent=2, default=str), encoding="utf-8"
        )

    def compute_input_hash(self, *paths: Path) -> str:
        """Compute SHA256 hash of input file(s)."""
        hasher = hashlib.sha256()
        for path in sorted(paths):
            if path.exists():
                hasher.update(path.read_bytes())
        return hasher.hexdigest()

    def compute_config_hash(self, **kwargs: Any) -> str:
        """Compute hash of configuration parameters."""
        hasher = hashlib.sha256()
        for k, v in sorted(kwargs.items()):
            hasher.update(f"{k}={v}".encode())
        return hasher.hexdigest()[:16]

    def get(
        self, key: CacheKey, default: Any = None
    ) -> tuple[Any, bool]:
        """Get cached value. Returns (value, found)."""
        key_str = key.hash()
        entry = self._index.get(key_str)
        if entry is None:
            return default, False
        # Check expiration (optional)
        return entry.value, True

    def put(
        self, key: CacheKey, value: Any, expires_at: str = ""
    ) -> None:
        """Store value in cache."""
        key_str = key.hash()
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=_now_iso(),
            expires_at=expires_at,
        )
        self._index[key_str] = entry
        self._save_index()

    def invalidate(
        self,
        input_hash: Optional[str] = None,
        config_hash: Optional[str] = None,
        operation: Optional[str] = None,
    ) -> int:
        """Invalidate cache entries matching criteria.

        Returns number of entries removed.
        """
        to_remove = []
        for key_str, entry in self._index.items():
            match = True
            if input_hash is not None and entry.key.input_hash != input_hash:
                match = False
            if config_hash is not None and entry.key.config_hash != config_hash:
                match = False
            if operation is not None and entry.key.operation != operation:
                match = False
            if match:
                to_remove.append(key_str)

        for key_str in to_remove:
            del self._index[key_str]

        if to_remove:
            self._save_index()

        return len(to_remove)

    def invalidate_all(self) -> int:
        """Invalidate all cache entries."""
        count = len(self._index)
        self._index = {}
        self._index_path().write_text("{}", encoding="utf-8")
        return count

    def stats(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "entries": len(self._index),
            "cache_dir": str(self.cache_dir),
            "index_path": str(self._index_path()),
        }


def _now_iso() -> str:
    """Return current timestamp as ISO string."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# Global cache instance (lazy initialization)
_global_cache: Any = None


def get_cache(cache_dir: Path | None = None) -> CacheManager:
    """Get global cache manager instance."""
    global _global_cache
    if _global_cache is None:
        if cache_dir is None:
            cache_dir = Path.home() / ".pdf_to_video_ai_cache"
        _global_cache = CacheManager(cache_dir)
    return _global_cache


def invalidate_all_caches() -> int:
    """Invalidate all caches globally."""
    global _global_cache
    count = 0
    if _global_cache is not None:
        count = _global_cache.invalidate_all()
        _global_cache = None
    return count