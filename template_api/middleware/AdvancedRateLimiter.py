"""
Advanced Rate Limiter Middleware

Rate limiting avanzado con soporte para:
- Rate limiting por usuario autenticado (no solo IP)
- Múltiples ventanas de tiempo
- Whitelist/blacklist de IPs
- Diferentes límites por endpoint
- Redis para rate limiting distribuido (opcional)
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

# Centralized loggers
from config.logger import logger, structured_logger


class RateLimitRule:
    """Define una regla de rate limiting"""

    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        endpoint_pattern: str = ".*"
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.endpoint_pattern = re.compile(endpoint_pattern)


class AdvancedRateLimiter(BaseHTTPMiddleware):
    """
    Rate limiter con soporte para usuarios autenticados y reglas por endpoint.

    Configuración:
    - default_limit: Límite por defecto (requests por ventana)
    - window_seconds: Ventana de tiempo en segundos
    - rules: Reglas específicas por endpoint
    - whitelist_ips: IPs excluidas del rate limiting
    - use_redis: Usar Redis para rate limiting distribuido
    """

    def __init__(
        self,
        app,
        default_limit: int = 100,
        window_seconds: int = 60,
        rules: Optional[List[RateLimitRule]] = None,
        whitelist_ips: Optional[List[str]] = None,
        blacklist_ips: Optional[List[str]] = None,
        use_redis: bool = False,
        redis_url: Optional[str] = None
    ):
        super().__init__(app)
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self.rules = rules or []
        self.whitelist_ips = set(whitelist_ips or [])
        self.blacklist_ips = set(blacklist_ips or [])
        self.use_redis = use_redis

        # Storage en memoria (por IP y por usuario)
        self.ip_requests: Dict[str, List[datetime]] = defaultdict(list)
        self.user_requests: Dict[str, List[datetime]] = defaultdict(list)

        # Redis client (opcional)
        if use_redis and redis_url:
            try:
                import redis.asyncio as redis
                self.redis = redis.from_url(redis_url, decode_responses=True)
                logger.info("Rate limiter usando Redis")
            except ImportError:
                logger.warning("Redis no disponible, usando storage en memoria")
                self.redis = None
        else:
            self.redis = None

        logger.info(f"AdvancedRateLimiter inicializado: {default_limit} req/{window_seconds}s")

    def _get_client_ip(self, request: Request) -> str:
        """Obtiene la IP real del cliente"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _get_user_id(self, request: Request) -> Optional[str]:
        """
        Extrae el ID de usuario del request (si está autenticado).

        TODO: Implementar según el sistema de auth usado.
        Puede leer del JWT, session, etc.
        """
        # Intentar leer del header Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from jose import jwt
                from dependencies.auth import SECRET_KEY, ALGORITHM

                token = auth_header.replace("Bearer ", "")
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                return payload.get("sub")  # Username como identificador
            except Exception:
                pass

        return None

    def _get_rate_limit_for_endpoint(self, path: str) -> tuple:
        """
        Retorna el límite aplicable para un endpoint.

        Returns:
            tuple: (max_requests, window_seconds)
        """
        for rule in self.rules:
            if rule.endpoint_pattern.match(path):
                return (rule.max_requests, rule.window_seconds)

        return (self.default_limit, self.window_seconds)

    def _check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple:
        """
        Verifica si se excedió el rate limit.

        Returns:
            tuple: (is_allowed, remaining_requests)
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)

        # Limpiar requests antiguos
        self.ip_requests[key] = [
            ts for ts in self.ip_requests[key]
            if ts > window_start
        ]

        request_count = len(self.ip_requests[key])

        if request_count >= max_requests:
            return False, 0

        # Agregar este request
        self.ip_requests[key].append(now)
        remaining = max_requests - request_count - 1

        return True, remaining

    async def _check_rate_limit_redis(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple:
        """Rate limiting usando Redis (para sistemas distribuidos)"""
        if not self.redis:
            return await self._check_rate_limit(key, max_requests, window_seconds)

        try:
            pipe = self.redis.pipeline()
            now = datetime.now().timestamp()

            # Usar sorted set en Redis con timestamps
            pipe.zremrangebyscore(key, 0, now - window_seconds)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window_seconds)

            results = await pipe.execute()
            request_count = results[2]

            if request_count > max_requests:
                return False, 0

            remaining = max_requests - request_count
            return True, remaining

        except Exception as e:
            logger.error(f"Error en rate limiting con Redis: {e}")
            # Fallback a storage en memoria
            return self._check_rate_limit(key, max_requests, window_seconds)

    async def dispatch(self, request: Request, call_next):
        """Aplica rate limiting"""

        path = request.url.path
        client_ip = self._get_client_ip(request)

        # Excluir paths de health/docs
        if any(path.startswith(p) for p in ["/health", "/docs", "/redoc", "/openapi.json"]):
            return await call_next(request)

        # Verificar blacklist
        if client_ip in self.blacklist_ips:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "IP bloqueada"},
                headers={"Retry-After": "3600"}
            )

        # Verificar whitelist
        if client_ip in self.whitelist_ips:
            return await call_next(request)

        # Obtener límites para este endpoint
        max_requests, window_seconds = self._get_rate_limit_for_endpoint(path)

        # Rate limiting por usuario (si está autenticado)
        user_id = self._get_user_id(request)
        if user_id:
            rate_key = f"user:{user_id}:{path}"
        else:
            rate_key = f"ip:{client_ip}:{path}"

        # Verificar límite
        if self.use_redis and self.redis:
            is_allowed, remaining = await self._check_rate_limit_redis(
                rate_key, max_requests, window_seconds
            )
        else:
            is_allowed, remaining = self._check_rate_limit(
                rate_key, max_requests, window_seconds
            )

        # Si excedió el límite, retornar 429
        if not is_allowed:
            # Use structured logger for rate limit events
            structured_logger.warning(
                "Rate limit exceeded (advanced)",
                rate_key=rate_key,
                path=str(request.url.path),
                method=request.method,
                max_requests=max_requests,
                window_seconds=window_seconds,
                event_type="rate_limit_exceeded"
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Límite de requests excedido",
                    "limit": max_requests,
                    "window_seconds": window_seconds
                },
                headers={
                    "Retry-After": str(window_seconds),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(window_seconds)
                }
            )

        # Procesar request
        response = await call_next(request)

        # Agregar headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(window_seconds)

        return response
