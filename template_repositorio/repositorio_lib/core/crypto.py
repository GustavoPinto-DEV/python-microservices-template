"""Encryption functions"""

from passlib.context import CryptContext
import base64

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def base64_encrypt(text: str) -> str:
    """Encrypt text to base64"""
    return base64.b64encode(text.encode()).decode()


def base64_decrypt(encoded: str) -> str:
    """Decrypt from base64"""
    return base64.b64decode(encoded.encode()).decode()
