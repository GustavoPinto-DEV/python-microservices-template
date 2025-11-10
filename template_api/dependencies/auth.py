"""
Dependencies de Autenticación

Maneja la autenticación y autorización usando JWT.
Proporciona dependencies de FastAPI para proteger endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# Security scheme
security = HTTPBearer()

# Configuración JWT (debe coincidir con .env)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT.

    Args:
        data: Datos a codificar en el token
        expires_delta: Tiempo de expiración opcional

    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT.

    Args:
        token: Token JWT a decodificar

    Returns:
        Payload del token

    Raises:
        JWTError: Si el token es inválido o expiró
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency para obtener el usuario actual desde el token JWT.

    Se usa como dependency en endpoints que requieren autenticación:

    @router.get("/protected", dependencies=[Depends(get_current_user)])
    async def protected_endpoint():
        ...

    Args:
        credentials: Credenciales HTTP Bearer (token)

    Returns:
        Diccionario con datos del usuario del token

    Raises:
        HTTPException 401: Si el token es inválido o falta
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        token = credentials.credentials
        payload = decode_access_token(token)

        # Validar que el token tenga los campos requeridos
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta información de usuario",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return {
            "username": username,
            "token": payload.get("token"),
            "payload": payload
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error al validar token",
            headers={"WWW-Authenticate": "Bearer"}
        ) from e


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency para obtener usuario actual y validar que esté activo.

    Extiende get_current_user con validación adicional de estado.

    Args:
        current_user: Usuario del token (inyectado)

    Returns:
        Usuario si está activo

    Raises:
        HTTPException 403: Si el usuario está inactivo
    """
    # TODO: Verificar en base de datos si el usuario está activo
    # user_db = await repository.get_user(current_user["username"])
    # if not user_db.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Usuario inactivo"
    #     )

    return current_user


def require_role(required_role: str):
    """
    Factory para crear dependency que valida rol del usuario.

    Uso:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
        async def admin_endpoint():
            ...

    Args:
        required_role: Rol requerido

    Returns:
        Dependency function
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        # TODO: Implementar verificación de rol desde DB
        # user_role = await repository.get_user_role(current_user["username"])
        # if user_role != required_role:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail=f"Se requiere rol: {required_role}"
        #     )

        user_role = current_user.get("role", "user")
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere rol: {required_role}"
            )

        return current_user

    return role_checker


# TODO: Agregar más dependencies de autorización según necesidad
# Ejemplos:
# - Validar permisos específicos
# - Validar propiedad de recursos
# - Rate limiting por usuario
# - Validar subscripción activa
