"""
Tests para el módulo de autenticación

Tests que verifican la creación, validación y decodificación
de tokens JWT, así como las funciones de autorización.
"""

import pytest
from datetime import timedelta
from fastapi import HTTPException
from jose import jwt

from dependencies.auth import (
    create_access_token,
    decode_access_token,
    get_current_user,
    require_role,
    SECRET_KEY,
    ALGORITHM
)


class TestJWTTokens:
    """Tests para creación y validación de tokens JWT"""

    def test_create_access_token(self):
        """Test de creación de token JWT"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)

        # Verificar que se puede decodificar
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert "exp" in payload

    def test_create_token_with_custom_expiration(self):
        """Test de token con tiempo de expiración personalizado"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)

        token = create_access_token(data, expires_delta)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"

    def test_create_token_with_additional_claims(self):
        """Test de token con claims adicionales"""
        data = {
            "sub": "testuser",
            "role": "admin",
            "email": "test@example.com"
        }

        token = create_access_token(data)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert payload["email"] == "test@example.com"


class TestTokenDecoding:
    """Tests para decodificación de tokens"""

    def test_decode_valid_token(self):
        """Test de decodificar token válido"""
        token = create_access_token({"sub": "testuser"})

        payload = decode_access_token(token)

        assert payload["sub"] == "testuser"
        assert "exp" in payload

    def test_decode_invalid_token(self):
        """Test de decodificar token inválido"""
        invalid_token = "invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(invalid_token)

        assert exc_info.value.status_code == 401
        assert "inválido" in exc_info.value.detail.lower()

    def test_decode_expired_token(self):
        """Test de decodificar token expirado"""
        # Crear token con expiración en el pasado
        data = {"sub": "testuser"}
        token = create_access_token(data, timedelta(seconds=-1))

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)

        assert exc_info.value.status_code == 401

    def test_decode_token_wrong_signature(self):
        """Test de token con firma incorrecta"""
        # Crear token con otra clave
        wrong_token = jwt.encode({"sub": "testuser"}, "wrong-secret", algorithm=ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(wrong_token)

        assert exc_info.value.status_code == 401


class TestGetCurrentUser:
    """Tests para la función get_current_user"""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test de obtener usuario con token válido"""
        from fastapi.security import HTTPAuthorizationCredentials

        token = create_access_token({"sub": "testuser", "token": "abc123"})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        user = await get_current_user(credentials)

        assert user["username"] == "testuser"
        assert "payload" in user

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test con token inválido"""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token"
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub(self):
        """Test con token que no tiene 'sub' claim"""
        from fastapi.security import HTTPAuthorizationCredentials

        token = create_access_token({"no_sub": "value"})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == 401


class TestRoleBasedAccess:
    """Tests para control de acceso basado en roles"""

    @pytest.mark.asyncio
    async def test_require_role_success(self):
        """Test de acceso exitoso con rol correcto"""
        role_checker = require_role("admin")

        current_user = {
            "username": "admin",
            "role": "admin"
        }

        # No debería lanzar excepción
        result = await role_checker(current_user)
        assert result == current_user

    @pytest.mark.asyncio
    async def test_require_role_denied(self):
        """Test de acceso denegado por rol incorrecto"""
        role_checker = require_role("admin")

        current_user = {
            "username": "user",
            "role": "user"
        }

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user)

        assert exc_info.value.status_code == 403
        assert "admin" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_role_missing_role(self):
        """Test con usuario sin rol definido"""
        role_checker = require_role("admin")

        current_user = {
            "username": "user"
            # Sin campo 'role'
        }

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user)

        assert exc_info.value.status_code == 403


class TestIntegrationAuth:
    """Tests de integración del flujo completo de autenticación"""

    def test_full_auth_flow(self):
        """Test del flujo completo: crear token → decodificar → validar"""
        # 1. Crear token
        user_data = {"sub": "testuser", "role": "user"}
        token = create_access_token(user_data)

        # 2. Decodificar token
        payload = decode_access_token(token)
        assert payload["sub"] == "testuser"

        # 3. Simular get_current_user
        assert payload["sub"] == user_data["sub"]
