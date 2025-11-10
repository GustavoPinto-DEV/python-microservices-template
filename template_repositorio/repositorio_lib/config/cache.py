"""Sistema de caché simple con TTL"""
from datetime import datetime, timedelta
from typing import Any, Optional

class SimpleCache:
    def __init__(self):
        self.cache = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            data, expiry = self.cache[key]
            if datetime.now() < expiry:
                return data
            del self.cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self.cache[key] = (value, expiry)

cache = SimpleCache()
