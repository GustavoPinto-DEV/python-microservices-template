"""
Rate Limiter Middleware

Protege la API contra abuso limitando el número de requests por IP.
Implementa un sistema de ventana deslizante simple en memoria.

Para producción, considerar usar Redis para rate limiting distribuido.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict

# Logger centralizado
from config.logger import logger


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware de rate limiting por IP.

    Configuración:
    - max_requests: Número máximo de requests permitidos
    - window_seconds: Ventana de tiempo en segundos

    Ejemplo:
        max_requests=100, window_seconds=60 -> 100 requests por minuto
    """

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60,
        exclude_paths: list = None
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.exclude_paths = exclude_paths or ["/", "/health", "/docs", "/redoc", "/openapi.json"]

        # Almacenamiento en memoria: {ip: [(timestamp1, ), (timestamp2, ), ...]}
        self.requests_store = defaultdict(list)

        # Última limpieza del store
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(minutes=5)

        logger.info(
            f"Rate Limiter configurado: {max_requests} requests "
            f"cada {window_seconds} segundos"
        )

    async def dispatch(self, request: Request, call_next):
        """
        Procesa cada request verificando rate limits.
        """

        # Excluir paths que no necesitan rate limiting
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Obtener IP del cliente
        client_ip = self._get_client_ip(request)

        # Verificar rate limit
        is_allowed, remaining = self._check_rate_limit(client_ip)

        if not is_allowed:
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "Demasiadas solicitudes. Por favor, intenta más tarde.",
                    "retry_after": self.window_seconds
                },
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(datetime.now().timestamp() + self.window_seconds)),
                    "Retry-After": str(self.window_seconds)
                }
            )

        # Procesar request
        response = await call_next(request)

        # Agregar headers de rate limit a la respuesta
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        # Limpieza periódica del store
        await self._periodic_cleanup()

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Obtiene la IP real del cliente considerando proxies.

        Args:
            request: Request de FastAPI

        Returns:
            IP del cliente
        """
        # Verificar headers de proxy (orden de prioridad)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For puede contener múltiples IPs
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback a la IP de la conexión
        return request.client.host if request.client else "unknown"

    def _check_rate_limit(self, client_ip: str) -> tuple[bool, int]:
        """
        Verifica si el cliente ha excedido el rate limit.

        Args:
            client_ip: IP del cliente

        Returns:
            Tupla (is_allowed, remaining_requests)
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)

        # Obtener requests del cliente en la ventana actual
        client_requests = self.requests_store[client_ip]

        # Filtrar solo requests dentro de la ventana
        valid_requests = [
            req_time for req_time in client_requests
            if req_time > window_start
        ]

        # Actualizar store con requests válidos
        self.requests_store[client_ip] = valid_requests

        # Verificar límite
        if len(valid_requests) >= self.max_requests:
            return False, 0

        # Agregar request actual
        self.requests_store[client_ip].append(now)

        remaining = self.max_requests - len(valid_requests) - 1
        return True, max(0, remaining)

    async def _periodic_cleanup(self) -> None:
        """
        Limpia entries antiguas del store periódicamente.
        """
        now = datetime.now()

        if now - self.last_cleanup < self.cleanup_interval:
            return

        logger.info("Ejecutando limpieza periódica de rate limiter store")

        # Eliminar IPs sin requests recientes
        window_start = now - timedelta(seconds=self.window_seconds)
        ips_to_remove = []

        for ip, requests in self.requests_store.items():
            # Filtrar requests válidos
            valid_requests = [req for req in requests if req > window_start]

            if not valid_requests:
                ips_to_remove.append(ip)
            else:
                self.requests_store[ip] = valid_requests

        # Eliminar IPs inactivos
        for ip in ips_to_remove:
            del self.requests_store[ip]

        self.last_cleanup = now
        logger.info(f"Limpieza completada. IPs eliminadas: {len(ips_to_remove)}")


# TODO: Para producción, considerar implementar rate limiting con Redis
# Ejemplo con Redis:
# - Usar Redis INCR con TTL para contar requests
# - Permite rate limiting distribuido en múltiples instancias
# - Mejor performance y persistencia

"""
Ejemplo de uso con Redis (pseudocódigo):

import redis.asyncio as redis

class RedisRateLimiter:
    def __init__(self, redis_client, max_requests, window_seconds):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window_seconds

    async def check_rate_limit(self, key: str) -> bool:
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window)
        results = await pipe.execute()

        current_count = results[0]
        return current_count <= self.max_requests
"""
