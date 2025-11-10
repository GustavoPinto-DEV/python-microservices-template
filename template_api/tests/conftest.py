"""
Pytest Configuration and Fixtures

Este archivo contiene fixtures compartidos para todos los tests.
Fixtures disponibles:
- client: TestClient de FastAPI
- db_session: Sesión de base de datos para tests
- auth_headers: Headers con JWT para endpoints protegidos
- mock_user: Usuario de prueba
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio

# Import main app
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from dependencies.auth import create_access_token


# ==========================================
# Fixtures de FastAPI Client
# ==========================================

@pytest.fixture(scope="module")
def client():
    """
    TestClient de FastAPI para testing.

    Uso:
        def test_endpoint(client):
            response = client.get("/api/v1/status")
            assert response.status_code == 200
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def sync_client():
    """
    TestClient sincrónico para tests que no requieren async.
    """
    return TestClient(app)


# ==========================================
# Fixtures de Base de Datos
# ==========================================

@pytest.fixture(scope="module")
def event_loop():
    """
    Fixture para event loop de asyncio.
    Necesario para tests async con pytest.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """
    Fixture de sesión de base de datos para tests.

    Usa SQLite in-memory para tests rápidos.
    Cada test obtiene una sesión limpia.

    Uso:
        async def test_create_user(db_session):
            user = User(name="Test")
            db_session.add(user)
            await db_session.commit()
    """
    # Crear engine in-memory para tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Crear sesión
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        # TODO: Crear tablas si es necesario
        # from repositorio_lib.model.models import Base
        # async with engine.begin() as conn:
        #     await conn.run_sync(Base.metadata.create_all)

        yield session

        # Rollback después de cada test
        await session.rollback()


# ==========================================
# Fixtures de Autenticación
# ==========================================

@pytest.fixture(scope="module")
def mock_user():
    """
    Usuario de prueba para tests.

    Returns:
        dict: Datos del usuario de prueba
    """
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "role": "user"
    }


@pytest.fixture(scope="module")
def mock_admin_user():
    """
    Usuario administrador de prueba.
    """
    return {
        "id": 999,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin"
    }


@pytest.fixture(scope="module")
def auth_token(mock_user):
    """
    Token JWT válido para tests.

    Uso:
        def test_protected_endpoint(client, auth_token):
            response = client.get(
                "/api/v1/items",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
    """
    token = create_access_token({"sub": mock_user["username"]})
    return token


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """
    Headers con autenticación JWT.

    Uso:
        def test_protected(client, auth_headers):
            response = client.get("/api/v1/items", headers=auth_headers)
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="module")
def admin_token(mock_admin_user):
    """Token JWT para usuario administrador."""
    token = create_access_token({"sub": mock_admin_user["username"], "role": "admin"})
    return token


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Headers con autenticación de administrador."""
    return {"Authorization": f"Bearer {admin_token}"}


# ==========================================
# Fixtures de Datos de Prueba
# ==========================================

@pytest.fixture(scope="function")
def sample_item_data():
    """
    Datos de ejemplo para crear un item.
    """
    return {
        "name": "Test Item",
        "description": "This is a test item",
        "active": True
    }


@pytest.fixture(scope="function")
def sample_items_list():
    """
    Lista de items de ejemplo para tests.
    """
    return [
        {"id": 1, "name": "Item 1", "description": "Desc 1", "active": True},
        {"id": 2, "name": "Item 2", "description": "Desc 2", "active": True},
        {"id": 3, "name": "Item 3", "description": "Desc 3", "active": False},
    ]


# ==========================================
# Fixtures de Mocking
# ==========================================

@pytest.fixture(scope="function")
def mock_repository(mocker):
    """
    Mock del repositorio para tests unitarios.

    Uso:
        def test_controller(mock_repository):
            mock_repository.get_all.return_value = [...]
            controller = v1Controller()
            result = await controller.get_items()
    """
    # TODO: Implementar cuando se use repositorio real
    # from repositorio_lib.service.repository import v1Repositorio
    # return mocker.Mock(spec=v1Repositorio)
    pass


# ==========================================
# Fixtures de Configuración
# ==========================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Configuración global para el ambiente de testing.
    Se ejecuta una vez al inicio de la suite de tests.
    """
    import os

    # Forzar ambiente de testing
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DB_NAME"] = ":memory:"

    yield

    # Cleanup si es necesario


# ==========================================
# Markers y Helpers
# ==========================================

@pytest.fixture
def anyio_backend():
    """Backend para anyio (usado por algunos tests async)."""
    return "asyncio"
