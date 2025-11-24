"""
Cookie-based authentication for web
"""

from fastapi import Cookie, HTTPException, status
from typing import Optional


async def get_current_user_cookie(session_token: Optional[str] = Cookie(None)) -> dict:
    """
    Dependency to get user from session cookie.

    Args:
        session_token: Session token from cookie

    Returns:
        Authenticated user

    Raises:
        HTTPException: If there is no valid session
    """
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"Location": "/login"}
        )

    # TODO: Validate real token with repository/JWT
    # user = await validate_session_token(session_token)

    # Temporary
    return {
        "username": "admin",
        "token": session_token
    }


# TODO: Add more authentication functions
