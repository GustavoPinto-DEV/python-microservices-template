"""
Autenticación basada en cookies para web
"""

from fastapi import Cookie, HTTPException, status
from typing import Optional


async def get_current_user_cookie(session_token: Optional[str] = Cookie(None)) -> dict:
    """
    Dependency para obtener usuario desde cookie de sesión.

    Args:
        session_token: Token de sesión desde cookie

    Returns:
        Usuario autenticado

    Raises:
        HTTPException: Si no hay sesión válida
    """
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"Location": "/login"}
        )

    # TODO: Validar token real con repositorio/JWT
    # user = await validate_session_token(session_token)

    # Temporal
    return {
        "username": "admin",
        "token": session_token
    }


# TODO: Agregar más funciones de autenticación
