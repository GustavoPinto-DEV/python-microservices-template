"""
Controller v1 - Lógica de negocio para web
"""

import logging

logger = logging.getLogger(__name__)


class v1Controller:
    """Controller principal de la aplicación web"""

    def __init__(self):
        # TODO: Inicializar repositorio
        pass

    async def login(self, username: str, password: str) -> dict:
        """Autentica usuario"""
        try:
            # TODO: Implementar autenticación real
            if username == "admin" and password == "admin":
                return {
                    "success": True,
                    "access_token": "temp-token-change-for-real-jwt",
                    "username": username
                }
            return {"success": False, "error": "Credenciales inválidas"}
        except Exception as e:
            logger.error(f"Error en login: {e}", exc_info=True)
            return {"success": False, "error": "Error interno"}

    # TODO: Agregar más métodos
