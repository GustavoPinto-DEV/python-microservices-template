"""
CSRF Protection Middleware

Protección contra ataques Cross-Site Request Forgery.

Para APIs REST con JWT, CSRF no es tan crítico, pero puede ser
útil si se usan cookies para autenticación o en endpoints sensibles.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
import secrets
import hmac
import hashlib
from typing import Optional, List

# Logger centralizado
from config.logger import logger


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware de protección CSRF.

    Configuración:
    - secret_key: Clave para firmar tokens CSRF
    - cookie_name: Nombre de la cookie CSRF
    - header_name: Nombre del header CSRF
    - safe_methods: Métodos HTTP que no requieren CSRF
    - exclude_paths: Paths excluidos de verificación CSRF
    """

    def __init__(
        self,
        app,
        secret_key: str,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        safe_methods: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.secret_key = secret_key.encode()
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.safe_methods = safe_methods or ["GET", "HEAD", "OPTIONS"]
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]

        logger.info("CSRFMiddleware inicializado")

    def _generate_csrf_token(self) -> str:
        """
        Genera un token CSRF único.

        Returns:
            str: Token CSRF
        """
        token = secrets.token_urlsafe(32)
        return token

    def _sign_token(self, token: str) -> str:
        """
        Firma un token CSRF con HMAC.

        Args:
            token: Token a firmar

        Returns:
            str: Token firmado
        """
        signature = hmac.new(
            self.secret_key,
            token.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{token}.{signature}"

    def _verify_token(self, signed_token: str) -> bool:
        """
        Verifica la firma de un token CSRF.

        Args:
            signed_token: Token firmado a verificar

        Returns:
            bool: True si la firma es válida
        """
        try:
            token, signature = signed_token.rsplit(".", 1)
            expected_signature = hmac.new(
                self.secret_key,
                token.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)
        except ValueError:
            return False

    def _should_check_csrf(self, request: Request) -> bool:
        """
        Determina si un request requiere verificación CSRF.

        Args:
            request: Request de FastAPI

        Returns:
            bool: True si requiere verificación
        """
        # No verificar métodos seguros
        if request.method in self.safe_methods:
            return False

        # No verificar paths excluidos
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return False

        # No verificar si usa JWT (Bearer token)
        # CSRF es principalmente para auth basada en cookies
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return False

        return True

    async def dispatch(self, request: Request, call_next):
        """Verifica CSRF token en requests no seguros"""

        # Verificar si requiere CSRF check
        if not self._should_check_csrf(request):
            response = await call_next(request)

            # Para requests seguros, agregar token en cookie
            if request.method in self.safe_methods:
                csrf_token = self._generate_csrf_token()
                signed_token = self._sign_token(csrf_token)

                response.set_cookie(
                    key=self.cookie_name,
                    value=signed_token,
                    httponly=True,
                    samesite="strict",
                    secure=False  # Cambiar a True en producción con HTTPS
                )

            return response

        # Obtener token de la cookie
        cookie_token = request.cookies.get(self.cookie_name)
        if not cookie_token:
            logger.warning(f"CSRF token faltante en cookie para {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token faltante en cookie"}
            )

        # Obtener token del header
        header_token = request.headers.get(self.header_name)
        if not header_token:
            logger.warning(f"CSRF token faltante en header para {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token faltante en header"}
            )

        # Verificar firma del token
        if not self._verify_token(cookie_token):
            logger.warning(f"CSRF token inválido (firma) para {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token inválido"}
            )

        # Comparar tokens (deben coincidir)
        try:
            cookie_value = cookie_token.rsplit(".", 1)[0]
            if not hmac.compare_digest(cookie_value, header_token):
                logger.warning(f"CSRF tokens no coinciden para {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF token no coincide"}
                )
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token malformado"}
            )

        # CSRF verificado correctamente
        response = await call_next(request)

        # Rotar token en cada request
        new_token = self._generate_csrf_token()
        signed_token = self._sign_token(new_token)

        response.set_cookie(
            key=self.cookie_name,
            value=signed_token,
            httponly=True,
            samesite="strict",
            secure=False  # Cambiar a True en producción
        )

        return response
