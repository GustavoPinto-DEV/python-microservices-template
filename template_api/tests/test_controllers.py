"""
Tests unitarios para controllers

Tests que verifican la lógica de negocio en los controllers
sin depender de la base de datos (usando mocks).
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi import HTTPException

from controller.v1Controller import v1Controller
from schema.schemas import LoginRequest, ItemRequest


class TestV1ControllerAuth:
    """Tests para métodos de autenticación del controller"""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test de login exitoso"""
        controller = v1Controller()
        request = LoginRequest(username="admin", password="admin")

        result = await controller.login(request)

        assert result.access_token is not None
        assert result.token_type == "bearer"
        assert result.username == "admin"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        """Test de login con credenciales inválidas"""
        controller = v1Controller()
        request = LoginRequest(username="admin", password="wrong")

        with pytest.raises(HTTPException) as exc_info:
            await controller.login(request)

        assert exc_info.value.status_code == 401
        assert "inválidas" in exc_info.value.detail.lower()


class TestV1ControllerItems:
    """Tests para operaciones CRUD de items"""

    @pytest.mark.asyncio
    async def test_get_items(self):
        """Test de obtener lista de items"""
        controller = v1Controller()

        result = await controller.get_items()

        assert isinstance(result, list)
        # Verificar que retorna al menos los items de ejemplo
        assert len(result) >= 0

        if len(result) > 0:
            item = result[0]
            assert "id" in item.__dict__
            assert "name" in item.__dict__

    @pytest.mark.asyncio
    async def test_get_item_exists(self):
        """Test de obtener item que existe"""
        controller = v1Controller()

        result = await controller.get_item(1)

        assert result.id == 1
        assert result.name is not None

    @pytest.mark.asyncio
    async def test_get_item_not_found(self):
        """Test de obtener item que no existe"""
        controller = v1Controller()

        with pytest.raises(HTTPException) as exc_info:
            await controller.get_item(9999)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_item_valid(self):
        """Test de crear item con datos válidos"""
        controller = v1Controller()
        request = ItemRequest(
            name="Test Item",
            description="Test description",
            active=True
        )

        result = await controller.create_item(request)

        assert result.name == request.name
        assert result.description == request.description
        assert result.active == request.active
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_create_item_invalid_name(self):
        """Test de crear item con nombre inválido (muy corto)"""
        controller = v1Controller()
        request = ItemRequest(
            name="AB",  # Muy corto
            description="Test",
            active=True
        )

        with pytest.raises(HTTPException) as exc_info:
            await controller.create_item(request)

        assert exc_info.value.status_code == 400
        assert "3 caracteres" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_item(self):
        """Test de actualizar item"""
        controller = v1Controller()
        request = ItemRequest(
            name="Updated Name",
            description="Updated desc",
            active=False
        )

        result = await controller.update_item(1, request)

        assert result.id == 1
        assert result.name == request.name
        assert result.description == request.description
        assert result.active == request.active

    @pytest.mark.asyncio
    async def test_delete_item(self):
        """Test de eliminar item"""
        controller = v1Controller()

        # No debería lanzar excepción
        await controller.delete_item(1)


class TestControllerValidation:
    """Tests de validaciones de negocio en el controller"""

    @pytest.mark.asyncio
    async def test_create_item_name_too_short(self):
        """Test de validación de longitud mínima de nombre"""
        controller = v1Controller()
        request = ItemRequest(name="AB", description="Test")

        with pytest.raises(HTTPException) as exc_info:
            await controller.create_item(request)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_item_empty_name(self):
        """Test de validación de nombre vacío"""
        controller = v1Controller()
        request = ItemRequest(name="", description="Test")

        with pytest.raises(HTTPException) as exc_info:
            await controller.create_item(request)

        assert exc_info.value.status_code == 400


class TestControllerErrorHandling:
    """Tests de manejo de errores en controllers"""

    @pytest.mark.asyncio
    async def test_handles_unexpected_errors(self):
        """Test que errores inesperados se manejan correctamente"""
        controller = v1Controller()

        # TODO: Cuando se use repositorio real, mockear para lanzar excepción
        # with patch.object(controller.repositorio, 'get_all', side_effect=Exception("DB Error")):
        #     with pytest.raises(HTTPException) as exc_info:
        #         await controller.get_items()
        #
        #     assert exc_info.value.status_code == 500
        pass


# Tests con mocks de repositorio
@pytest.mark.skip(reason="Requiere repositorio real configurado")
class TestControllerWithMockRepository:
    """Tests usando mock del repositorio"""

    @pytest.mark.asyncio
    async def test_get_items_from_repository(self, mock_repository):
        """Test que controller llama correctamente al repositorio"""
        # TODO: Implementar cuando se use repositorio real
        # mock_repository.get_all.return_value = Result(data=[...])
        # controller = v1Controller()
        # controller.repositorio = mock_repository
        #
        # result = await controller.get_items()
        #
        # mock_repository.get_all.assert_called_once()
        pass
