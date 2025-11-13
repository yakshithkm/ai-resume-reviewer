"""Cache module for ResumeParser to improve performance."""
from functools import lru_cache
from typing import Dict, Any, Optional
import hashlib
import json
import os
import pickle
from datetime import datetime, timedelta

class ResumeCache:
    """Cache for parsed resume results to improve performance."""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _get_cache_key(self, file_path: str, content: str) -> str:
        """Generate cache key based on file path and content hash."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{os.path.basename(file_path)}_{content_hash}"
        
    def get(self, file_path: str, content: str) -> Optional[Dict[str, Any]]:
        """Get cached parse results if available and not expired."""
        cache_key = self._get_cache_key(file_path, content)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pickle")
        
        if os.path.exists(cache_file):
            # Check if cache is still valid (less than 24 hours old)
            if datetime.fromtimestamp(os.path.getmtime(cache_file)) > datetime.now() - timedelta(hours=24):
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except:
                    return None
        return None
        
    def set(self, file_path: str, content: str, parse_results: Dict[str, Any]) -> None:
        """Cache parse results for future use."""
        cache_key = self._get_cache_key(file_path, content)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pickle")
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(parse_results, f)
        except:
            # Silently fail if caching errors - don't impact main functionality
            pass
            
    def clear(self, max_age: Optional[timedelta] = None) -> int:
        """Clear expired cache entries. Returns number of entries cleared."""
        cleared = 0
        now = datetime.now()
        
        for cache_file in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, cache_file)
            file_age = now - datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if max_age and file_age > max_age:
                try:
                    os.remove(file_path)
                    cleared += 1
                except:
                    pass
                    
        return cleared