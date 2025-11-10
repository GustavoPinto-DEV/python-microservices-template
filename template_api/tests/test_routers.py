"""
Tests para los routers de la API

Tests de integración que verifican que los endpoints
funcionen correctamente end-to-end.
"""

import pytest
from fastapi import status


class TestAuthEndpoints:
    """Tests para endpoints de autenticación"""

    def test_login_success(self, client):
        """Test de login exitoso con credenciales válidas"""
        response = client.post(
            "/api/v1/login",
            json={"username": "admin", "password": "admin"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "admin"

    def test_login_invalid_credentials(self, client):
        """Test de login con credenciales inválidas"""
        response = client.post(
            "/api/v1/login",
            json={"username": "admin", "password": "wrong"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()

    def test_login_missing_fields(self, client):
        """Test de login sin campos requeridos"""
        response = client.post(
            "/api/v1/login",
            json={"username": "admin"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestItemEndpoints:
    """Tests para endpoints de items (CRUD)"""

    def test_get_items_without_auth(self, client):
        """Test que endpoints protegidos requieren autenticación"""
        response = client.get("/api/v1/items")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_items_with_auth(self, client, auth_headers):
        """Test de obtener lista de items con autenticación"""
        response = client.get("/api/v1/items", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Verificar estructura de items
        if len(data) > 0:
            item = data[0]
            assert "id" in item
            assert "name" in item
            assert "description" in item
            assert "active" in item

    def test_get_item_by_id(self, client, auth_headers):
        """Test de obtener item específico por ID"""
        response = client.get("/api/v1/items/1", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        item = response.json()
        assert item["id"] == 1
        assert "name" in item

    def test_get_item_not_found(self, client, auth_headers):
        """Test de obtener item inexistente"""
        response = client.get("/api/v1/items/9999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_item(self, client, auth_headers, sample_item_data):
        """Test de crear nuevo item"""
        response = client.post(
            "/api/v1/items",
            json=sample_item_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        item = response.json()
        assert item["name"] == sample_item_data["name"]
        assert item["description"] == sample_item_data["description"]
        assert "id" in item

    def test_create_item_invalid_data(self, client, auth_headers):
        """Test de crear item con datos inválidos"""
        response = client.post(
            "/api/v1/items",
            json={"name": "AB"},  # Muy corto (< 3 caracteres)
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_item(self, client, auth_headers):
        """Test de actualizar item existente"""
        updated_data = {
            "name": "Updated Item",
            "description": "Updated description",
            "active": False
        }

        response = client.put(
            "/api/v1/items/1",
            json=updated_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        item = response.json()
        assert item["name"] == updated_data["name"]
        assert item["description"] == updated_data["description"]

    def test_delete_item(self, client, auth_headers):
        """Test de eliminar item"""
        response = client.delete("/api/v1/items/1", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestPublicEndpoints:
    """Tests para endpoints públicos (sin autenticación)"""

    def test_status_endpoint(self, client):
        """Test del endpoint de status/health check"""
        response = client.get("/api/v1/status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "operational"
        assert "version" in data

    def test_root_endpoint(self, client):
        """Test del endpoint raíz"""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data


class TestValidation:
    """Tests de validación de entrada"""

    def test_invalid_json(self, client, auth_headers):
        """Test con JSON inválido"""
        response = client.post(
            "/api/v1/items",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_required_fields(self, client, auth_headers):
        """Test con campos requeridos faltantes"""
        response = client.post(
            "/api/v1/items",
            json={},  # Sin campos requeridos
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_field_types(self, client, auth_headers):
        """Test con tipos de datos incorrectos"""
        response = client.post(
            "/api/v1/items",
            json={
                "name": 123,  # Debería ser string
                "active": "not a boolean"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Markers para tests
pytestmark = pytest.mark.asyncio
