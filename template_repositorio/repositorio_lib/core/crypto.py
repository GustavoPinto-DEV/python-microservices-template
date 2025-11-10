"""Funciones de encriptación"""
from passlib.context import CryptContext
import base64

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash de contraseña con bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña contra hash"""
    return pwd_context.verify(plain_password, hashed_password)

def encriptar_base_64(text: str) -> str:
    """Encripta texto en base64"""
    return base64.b64encode(text.encode()).decode()

def desencriptar_base_64(encoded: str) -> str:
    """Desencripta de base64"""
    return base64.b64decode(encoded.encode()).decode()
