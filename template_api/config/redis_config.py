"""
Redis Configuration

Configuración y utilidades para Redis (cache, rate limiting, sessions).

Uso:
    from config.redis_config import get_redis, cache_set, cache_get

    # Obtener cliente Redis
    redis = await get_redis()

    # Cache simple
    await cache_set("key", {"data": "value"}, ttl=300)
    data = await cache_get("key")
"""

import redis.asyncio as redis
from typing import Any, Optional
import json
import os
from contextlib import asynccontextmanager

# Configuración
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))

# Pool de conexiones global
_redis_pool: Optional[redis.ConnectionPool] = None


def get_redis_pool() -> redis.ConnectionPool:
    """Obtiene o crea el pool de conexiones Redis"""
    global _redis_pool

    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool.from_url(
            REDIS_URL,
            max_connections=REDIS_MAX_CONNECTIONS,
            decode_responses=True
        )

    return _redis_pool


async def get_redis() -> redis.Redis:
    """
    Obtiene cliente Redis del pool.

    Returns:
        redis.Redis: Cliente Redis
    """
    pool = get_redis_pool()
    return redis.Redis(connection_pool=pool)


@asynccontextmanager
async def redis_context():
    """
    Context manager para Redis con manejo automático de conexiones.

    Uso:
        async with redis_context() as r:
            await r.set("key", "value")
    """
    client = await get_redis()
    try:
        yield client
    finally:
        await client.close()


async def cache_set(
    key: str,
    value: Any,
    ttl: int = 300,
    prefix: str = "cache:"
) -> bool:
    """
    Guarda valor en cache con TTL.

    Args:
        key: Clave del cache
        value: Valor a guardar (será serializado a JSON)
        ttl: Tiempo de vida en segundos
        prefix: Prefijo para la clave

    Returns:
        bool: True si se guardó correctamente
    """
    try:
        async with redis_context() as r:
            serialized = json.dumps(value)
            return await r.setex(f"{prefix}{key}", ttl, serialized)
    except Exception as e:
        print(f"Error en cache_set: {e}")
        return False


async def cache_get(key: str, prefix: str = "cache:") -> Optional[Any]:
    """
    Obtiene valor del cache.

    Args:
        key: Clave del cache
        prefix: Prefijo de la clave

    Returns:
        Any: Valor deserializado o None si no existe
    """
    try:
        async with redis_context() as r:
            value = await r.get(f"{prefix}{key}")
            if value:
                return json.loads(value)
            return None
    except Exception as e:
        print(f"Error en cache_get: {e}")
        return None


async def cache_delete(key: str, prefix: str = "cache:") -> bool:
    """Elimina clave del cache"""
    try:
        async with redis_context() as r:
            return await r.delete(f"{prefix}{key}") > 0
    except Exception as e:
        print(f"Error en cache_delete: {e}")
        return False


async def cache_exists(key: str, prefix: str = "cache:") -> bool:
    """Verifica si existe una clave en cache"""
    try:
        async with redis_context() as r:
            return await r.exists(f"{prefix}{key}") > 0
    except Exception as e:
        return False
