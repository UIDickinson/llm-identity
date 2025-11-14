"""
Test model caching system
"""
import pytest
from models.cache import ModelCache


def test_cache_basic_operations():
    """Test basic cache operations"""
    cache = ModelCache(max_size_gb=1)
    
    cache.put("key1", "value1", size_mb=10)
    assert cache.get("key1") == "value1"
    
    assert cache.get("nonexistent") == None
    
    cache.remove("key1")
    assert cache.get("key1") == None


def test_cache_eviction():
    """Test LRU eviction"""
    cache = ModelCache(max_size_gb=1)  # 1GB = 1024MB
    
    cache.put("key1", "value1", size_mb=600)
    cache.put("key2", "value2", size_mb=600)  # Should evict key1
    
    assert cache.get("key1") == None
    assert cache.get("key2") == "value2"


def test_cache_stats():
    """Test cache statistics"""
    cache = ModelCache(max_size_gb=1)
    
    cache.put("key1", "value1", size_mb=100)
    cache.put("key2", "value2", size_mb=200)
    
    stats = cache.get_stats()
    
    assert stats["total_items"] == 2
    assert stats["total_size_mb"] == 300
    assert stats["max_size_gb"] == 1