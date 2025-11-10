"""Funciones de seguridad"""
from jose import jwt
from datetime import datetime, timedelta
from repositorio_lib.config.settings import jwt_settings

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Crea token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)

def verify_token(token: str) -> dict:
    """Verifica y decodifica token JWT"""
    return jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=[jwt_settings.ALGORITHM])
