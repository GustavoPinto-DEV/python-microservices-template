"""Security functions"""

from jose import jwt
from datetime import datetime, timedelta, timezone
from repositorio_lib.config import jwt_settings


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM
    )


def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    return jwt.decode(
        token, jwt_settings.SECRET_KEY, algorithms=[jwt_settings.ALGORITHM]
    )
