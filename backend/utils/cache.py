"""Simple in-memory caching for frequently accessed data."""
from typing import Any, Optional
from datetime import datetime, timedelta
import json

class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None
        
        # Check if expired
        if key in self._expiry and datetime.now() > self._expiry[key]:
            del self._cache[key]
            del self._expiry[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache with TTL (default 5 minutes)."""
        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def delete(self, key: str):
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry:
            del self._expiry[key]
    
    def clear(self):
        """Clear all cache."""
        self._cache.clear()
        self._expiry.clear()
    
    def has(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None


# Global cache instance
cache = SimpleCache()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
    return ":".join(key_parts)
