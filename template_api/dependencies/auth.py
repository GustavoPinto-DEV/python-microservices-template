"""
Authentication Dependencies

Handles authentication and authorization using JWT.
Provides FastAPI dependencies to protect endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# Security scheme
security = HTTPBearer()

# JWT configuration (must match .env)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time

    Returns:
        Encoded JWT token
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
    Decodes and validates a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current user from JWT token.

    Used as a dependency in endpoints requiring authentication:

    @router.get("/protected", dependencies=[Depends(get_current_user)])
    async def protected_endpoint():
        ...

    Args:
        credentials: HTTP Bearer credentials (token)

    Returns:
        Dictionary with user data from token

    Raises:
        HTTPException 401: If token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        token = credentials.credentials
        payload = decode_access_token(token)

        # Validate that token has required fields
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user information",
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
            detail="Error validating token",
            headers={"WWW-Authenticate": "Bearer"}
        ) from e


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to get current user and validate they are active.

    Extends get_current_user with additional status validation.

    Args:
        current_user: User from token (injected)

    Returns:
        User if active

    Raises:
        HTTPException 403: If user is inactive
    """
    # TODO: Verify in database if user is active
    # user_db = await repository.get_user(current_user["username"])
    # if not user_db.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Inactive user"
    #     )

    return current_user


def require_role(required_role: str):
    """
    Factory to create dependency that validates user role.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
        async def admin_endpoint():
            ...

    Args:
        required_role: Required role

    Returns:
        Dependency function
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        # TODO: Implement role verification from DB
        # user_role = await repository.get_user_role(current_user["username"])
        # if user_role != required_role:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail=f"Required role: {required_role}"
        #     )

        user_role = current_user.get("role", "user")
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )

        return current_user

    return role_checker


# TODO: Add more authorization dependencies as needed
# Examples:
# - Validate specific permissions
# - Validate resource ownership
# - Rate limiting per user
# - Validate active subscription
