import json
import time
from typing import Optional, Dict, Any
from pathlib import Path
from collections import OrderedDict
import threading

from agent.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ModelCache:
    """
    LRU cache for loaded models with size management
    """
    
    def __init__(self, max_size_gb: int = None):
        self.max_size_gb = max_size_gb or settings.model_cache_size_gb
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.lock = threading.Lock()
        self.metadata_file = settings.model_cache_dir / "cache_metadata.json"
        self._load_metadata()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                item = self.cache[key]
                item['last_accessed'] = time.time()
                item['access_count'] += 1
                logger.info(f"📦 Cache hit: {key}")
                return item['data']
            logger.info(f"📦 Cache miss: {key}")
            return None
    
    def put(self, key: str, data: Any, size_mb: float = 0):
        """Add item to cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            
            while self._get_total_size() + size_mb > self.max_size_gb * 1024:
                if not self.cache:
                    break
                evicted_key = next(iter(self.cache))
                self._evict(evicted_key)
            
            self.cache[key] = {
                'data': data,
                'size_mb': size_mb,
                'added_at': time.time(),
                'last_accessed': time.time(),
                'access_count': 0
            }
            
            logger.info(f"📦 Cached: {key} ({size_mb:.1f} MB)")
            self._save_metadata()
    
    def remove(self, key: str):
        """Remove item from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.info(f"🗑️ Removed from cache: {key}")
                self._save_metadata()
    
    def clear(self):
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()
            logger.info("🗑️ Cache cleared")
            self._save_metadata()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'total_items': len(self.cache),
                'total_size_mb': self._get_total_size(),
                'max_size_gb': self.max_size_gb,
                'items': [
                    {
                        'key': key,
                        'size_mb': item['size_mb'],
                        'access_count': item['access_count'],
                        'age_seconds': time.time() - item['added_at']
                    }
                    for key, item in self.cache.items()
                ]
            }
    
    def _evict(self, key: str):
        """Evict item from cache"""
        item = self.cache.pop(key, None)
        if item:
            logger.info(f"⏏️ Evicted from cache: {key} ({item['size_mb']:.1f} MB)")
    
    def _get_total_size(self) -> float:
        """Get total cache size in MB"""
        return sum(item['size_mb'] for item in self.cache.values())
    
    def _load_metadata(self):
        """Load cache metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file) as f:
                    metadata = json.load(f)
                logger.info(f"📂 Loaded cache metadata: {len(metadata)} items")
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
    
    def _save_metadata(self):
        """Save cache metadata to disk"""
        try:
            metadata = {
                key: {
                    'size_mb': item['size_mb'],
                    'added_at': item['added_at'],
                    'last_accessed': item['last_accessed'],
                    'access_count': item['access_count']
                }
                for key, item in self.cache.items()
            }
            
            self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache metadata: {e}")