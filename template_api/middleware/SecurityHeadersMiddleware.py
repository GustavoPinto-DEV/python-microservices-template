"""
Security Headers Middleware

Agrega headers de seguridad a todas las responses para proteger
contra vulnerabilidades comunes (XSS, clickjacking, MIME sniffing, etc.).

Headers implementados:
- X-Content-Type-Options: Previene MIME type sniffing
- X-Frame-Options: Previene clickjacking
- X-XSS-Protection: Protección XSS en navegadores antiguos
- Content-Security-Policy: Política de seguridad de contenido
- Strict-Transport-Security: Fuerza HTTPS
- Referrer-Policy: Control de información de referrer
- Permissions-Policy: Control de features del navegador
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

# Logger centralizado
from config.logger import logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware que agrega headers de seguridad a las responses.

    Configuración:
    - enable_hsts: Habilitar HSTS (solo para HTTPS)
    - hsts_max_age: Duración del HSTS en segundos
    - csp_policy: Política CSP personalizada
    """

    def __init__(
        self,
        app,
        enable_hsts: bool = False,  # Solo habilitar en producción con HTTPS
        hsts_max_age: int = 31536000,  # 1 año
        csp_policy: str = None,
        frame_options: str = "DENY",  # DENY, SAMEORIGIN, ALLOW-FROM
    ):
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        self.frame_options = frame_options

        # Content Security Policy por defecto (restrictiva)
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        logger.info("SecurityHeadersMiddleware inicializado")

    async def dispatch(self, request: Request, call_next):
        """Agrega headers de seguridad a la response"""

        response = await call_next(request)

        # X-Content-Type-Options
        # Previene MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options
        # Previene clickjacking
        response.headers["X-Frame-Options"] = self.frame_options

        # X-XSS-Protection
        # Habilita filtro XSS en navegadores antiguos
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content-Security-Policy
        # Define fuentes permitidas de contenido
        response.headers["Content-Security-Policy"] = self.csp_policy

        # Strict-Transport-Security (solo si HTTPS está habilitado)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains; preload"
            )

        # Referrer-Policy
        # Control de información en header Referer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy (antes Feature-Policy)
        # Controla features del navegador
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

        # X-Permitted-Cross-Domain-Policies
        # Control de políticas cross-domain para Flash/PDF
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # X-Download-Options
        # Previene que IE ejecute descargas en el contexto del sitio
        response.headers["X-Download-Options"] = "noopen"

        # Server header (ocultar información del servidor)
        response.headers["Server"] = "API"

        return response
