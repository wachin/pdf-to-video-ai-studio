import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from pdf_to_video_ai.cache import CacheManager, CacheKey, invalidate_all_caches


class TestCacheManager:
    """Tests for cache management."""

    def test_cache_put_get(self, tmp_path):
        cache = CacheManager(tmp_path)
        key = CacheKey(input_hash="abc", config_hash="cfg1", operation="tts")
        cache.put(key, "value")
        value, found = cache.get(key, default=None)
        assert found
        assert value == "value"

    def test_cache_miss(self, tmp_path):
        cache = CacheManager(tmp_path)
        key = CacheKey(input_hash="abc", config_hash="cfg1", operation="tts")
        value, found = cache.get(key, default=None)
        assert not found
        assert value is None

    def test_cache_key_hash_deterministic(self):
        key1 = CacheKey(input_hash="abc", config_hash="cfg1", operation="tts")
        key2 = CacheKey(input_hash="abc", config_hash="cfg1", operation="tts")
        assert key1.hash() == key2.hash()

    def test_cache_key_hash_different(self):
        key1 = CacheKey(input_hash="abc", config_hash="cfg1", operation="tts")
        key2 = CacheKey(input_hash="def", config_hash="cfg1", operation="tts")
        assert key1.hash() != key2.hash()

    def test_cache_invalidate_by_input_hash(self, tmp_path):
        cache = CacheManager(tmp_path)
        key1 = CacheKey(input_hash="abc", config_hash="cfg1", operation="tts")
        key2 = CacheKey(input_hash="def", config_hash="cfg2", operation="ocr")
        cache.put(key1, "data1")
        cache.put(key2, "data2")
        removed = cache.invalidate(input_hash="abc")
        assert removed == 1
        _, found = cache.get(key1, default=None)
        assert not found

    def test_cache_invalidate_by_operation(self, tmp_path):
        cache = CacheManager(tmp_path)
        key1 = CacheKey(input_hash="abc", config_hash="cfg1", operation="tts")
        key2 = CacheKey(input_hash="def", config_hash="cfg2", operation="tts")
        cache.put(key1, "data1")
        cache.put(key2, "data2")
        removed = cache.invalidate(operation="tts")
        assert removed == 2

    def test_cache_invalidate_all(self, tmp_path):
        cache = CacheManager(tmp_path)
        key = CacheKey(input_hash="abc", config_hash="cfg1", operation="tts")
        cache.put(key, "data")
        count = cache.invalidate_all()
        assert count == 1
        stats = cache.stats()
        assert stats["entries"] == 0

    def test_compute_input_hash_deterministic(self, tmp_path):
        cache = CacheManager(tmp_path)
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        h1 = cache.compute_input_hash(test_file)
        h2 = cache.compute_input_hash(test_file)
        assert h1 == h2

    def test_compute_config_hash_deterministic(self, tmp_path):
        cache = CacheManager(tmp_path)
        h1 = cache.compute_config_hash(voice="es-ES", rate="+0%")
        h2 = cache.compute_config_hash(voice="es-ES", rate="+0%")
        assert h1 == h2

    def test_stats(self, tmp_path):
        cache = CacheManager(tmp_path)
        stats = cache.stats()
        assert "entries" in stats
        assert "cache_dir" in stats
        assert stats["entries"] == 0


class TestGlobalCache:
    """Tests for global cache functions."""

    def test_invalidate_all_caches(self):
        count = invalidate_all_caches()
        assert isinstance(count, int)