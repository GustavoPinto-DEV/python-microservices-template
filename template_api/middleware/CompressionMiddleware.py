"""
Compression Middleware

Comprime las respuestas de la API usando gzip para reducir el tamaño de transferencia.

Funcionalidades:
- Compresión automática de responses grandes
- Configurable por tamaño mínimo y nivel de compresión
- Solo comprime tipos de contenido apropiados (JSON, HTML, text)
- Respeta preferencias del cliente (Accept-Encoding header)
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import gzip

# Logger centralizado
from config.logger import logger


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware que comprime las respuestas HTTP usando gzip.

    Args:
        app: Aplicación ASGI
        min_size: Tamaño mínimo en bytes para aplicar compresión (default: 500)
        compression_level: Nivel de compresión gzip 1-9 (default: 6)
        exclude_paths: Lista de paths a excluir de compresión

    Example:
        app.add_middleware(
            CompressionMiddleware,
            min_size=1000,
            compression_level=6,
            exclude_paths=["/health", "/metrics"]
        )
    """

    def __init__(
        self,
        app,
        min_size: int = 500,
        compression_level: int = 6,
        exclude_paths: list = None
    ):
        super().__init__(app)
        self.min_size = min_size
        self.compression_level = max(1, min(9, compression_level))  # Validar rango 1-9
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]

        logger.info(
            f"CompressionMiddleware initialized - "
            f"min_size={min_size}B, level={self.compression_level}"
        )

    async def dispatch(self, request: Request, call_next):
        """
        Procesa cada request y comprime la respuesta si aplica.

        Args:
            request: Request entrante
            call_next: Siguiente middleware/endpoint

        Returns:
            Response (comprimida o sin comprimir)
        """
        # Excluir paths configurados
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Procesar request
        response = await call_next(request)

        # Comprimir response si aplica
        if self._should_compress(request, response):
            response = await self._compress_response(response)

        return response

    def _should_compress(self, request: Request, response: Response) -> bool:
        """
        Determina si el response debe comprimirse.

        Args:
            request: Request original
            response: Response a evaluar

        Returns:
            True si debe comprimirse, False en caso contrario
        """
        # Verificar que el cliente acepte gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding.lower():
            return False

        # Verificar que no esté ya comprimido
        if response.headers.get("Content-Encoding"):
            return False

        # Verificar tipo de contenido (solo comprimir tipos apropiados)
        content_type = response.headers.get("Content-Type", "").lower()
        compressible_types = [
            "application/json",
            "application/javascript",
            "application/xml",
            "text/html",
            "text/css",
            "text/plain",
            "text/xml"
        ]

        if not any(ct in content_type for ct in compressible_types):
            return False

        return True

    async def _compress_response(self, response: Response) -> Response:
        """
        Comprime el body del response con gzip.

        Args:
            response: Response original

        Returns:
            Response con body comprimido
        """
        try:
            # Leer body del response
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Solo comprimir si supera el tamaño mínimo
            if len(body) < self.min_size:
                # Recrear response sin comprimir
                response.body = body
                return response

            # Comprimir con gzip
            compressed_body = gzip.compress(body, compresslevel=self.compression_level)

            # Actualizar headers
            response.headers["Content-Encoding"] = "gzip"
            response.headers["Content-Length"] = str(len(compressed_body))
            response.headers["Vary"] = "Accept-Encoding"

            # Actualizar body
            response.body = compressed_body

            # Log de compresión exitosa
            compression_ratio = (len(compressed_body) / len(body)) * 100
            logger.debug(
                f"Response compressed: {len(body)}B → {len(compressed_body)}B "
                f"({compression_ratio:.1f}%)"
            )

        except Exception as e:
            logger.warning(f"Error compressing response: {e}")
            # En caso de error, devolver response original sin comprimir
            response.body = body

        return response


# Funcionalidades opcionales para extender según necesidad:
# - Soporte para otros algoritmos (brotli, deflate)
# - Caché de responses comprimidas
# - Métricas de compresión (tamaño ahorrado, tiempo de CPU)
# - Compresión diferenciada por endpoint (mayor nivel para estáticos)
