"""
Simple in-memory caching for frequently accessed static data.
Uses TTL (Time To Live) to automatically expire cached entries.

Features:
- Thread-safe operations with Lock
- Automatic expiration on access
- Manual cleanup of expired entries
- Statistics tracking
"""

from typing import Any, Optional
from datetime import datetime, timedelta
from threading import Lock
from dataclasses import dataclass


@dataclass
class CacheStats:
    """Statistics for cache performance monitoring."""

    hits: int = 0
    misses: int = 0
    expirations: int = 0
    total_entries: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0


class CacheEntry:
    """Individual cache entry with value and expiration time."""

    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        self.created_at = datetime.now()

    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        return datetime.now() > self.expires_at


class SimpleCache:
    """
    Thread-safe in-memory cache with TTL support and statistics.

    Best practices:
    - Use caching for static/reference data (estados, parámetros, endpoints)
    - Set appropriate TTL based on data volatility
    - Call cleanup_expired() periodically to free memory
    """

    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of entries (None = unlimited)
        """
        self._cache: dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._stats = CacheStats()
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if exists and not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._stats.misses += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._stats.expirations += 1
                self._stats.misses += 1
                return None

            self._stats.hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """
        Set value in cache with TTL (default 5 minutes).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        with self._lock:
            if self._max_size and len(self._cache) >= self._max_size:
                if key not in self._cache:
                    oldest_key = min(
                        self._cache.keys(), key=lambda k: self._cache[k].created_at
                    )
                    del self._cache[oldest_key]

            self._cache[key] = CacheEntry(value, ttl_seconds)
            self._stats.total_entries = len(self._cache)

    def delete(self, key: str) -> None:
        """Delete specific key from cache."""
        with self._lock:
            self._cache.pop(key, None)
            self._stats.total_entries = len(self._cache)

    def clear(self) -> None:
        """Clear all cache entries and reset stats."""
        with self._lock:
            self._cache.clear()
            self._stats = CacheStats()

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries and return count removed.

        Returns:
            Number of expired entries removed
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]

            self._stats.expirations += len(expired_keys)
            self._stats.total_entries = len(self._cache)
            return len(expired_keys)

    def get_stats(self) -> CacheStats:
        """Get current cache statistics."""
        with self._lock:
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                expirations=self._stats.expirations,
                total_entries=len(self._cache),
            )

    def size(self) -> int:
        """Get current number of cached entries."""
        with self._lock:
            return len(self._cache)


cache = SimpleCache()
