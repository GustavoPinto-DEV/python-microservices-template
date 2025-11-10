"""
Router v1 - Definición de rutas y endpoints

Este módulo define todas las rutas de la API versión 1.
Sigue el patrón: Router → Controller → Repository → Database

Estructura:
- Cada endpoint delega la lógica al controller
- El router solo se encarga de routing y validación de entrada
- La documentación se genera automáticamente desde docstrings y type hints
"""

from fastapi import APIRouter, Depends, status
from typing import List

# Controller
from controller.v1Controller import v1Controller

# Schemas
from schema.schemas import (
    LoginRequest,
    LoginResponse,
    ItemRequest,
    ItemResponse,
    ErrorResponse
)

# Dependencies
from dependencies.auth import get_current_user

# Crear router
router = APIRouter()


# Dependency para obtener instancia del controller
def get_controller() -> v1Controller:
    """Dependency para inyectar controller en endpoints"""
    return v1Controller()


# region Endpoints de Autenticación

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un token JWT",
    responses={
        401: {"model": ErrorResponse, "description": "Credenciales inválidas"},
        500: {"model": ErrorResponse, "description": "Error del servidor"}
    }
)
async def login(
    request: LoginRequest,
    controller: v1Controller = Depends(get_controller)
):
    """
    Endpoint de login que autentica usuario y genera JWT.

    Args:
        request: Credenciales de usuario (username, password)
        controller: Instancia del controller (inyectada)

    Returns:
        LoginResponse con token de acceso

    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    return await controller.login(request)

# endregion


# region Endpoints de Ejemplo (protegidos por autenticación)

@router.get(
    "/items",
    response_model=List[ItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar items",
    description="Obtiene lista de todos los items (requiere autenticación)",
    dependencies=[Depends(get_current_user)]  # Proteger endpoint
)
async def get_items(
    controller: v1Controller = Depends(get_controller)
):
    """
    Obtiene lista de items.

    Este endpoint requiere autenticación JWT.

    Returns:
        Lista de items
    """
    return await controller.get_items()


@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener item por ID",
    dependencies=[Depends(get_current_user)]
)
async def get_item(
    item_id: int,
    controller: v1Controller = Depends(get_controller)
):
    """
    Obtiene un item específico por ID.

    Args:
        item_id: ID del item a buscar

    Returns:
        Datos del item

    Raises:
        HTTPException 404: Si el item no existe
    """
    return await controller.get_item(item_id)


@router.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo item",
    dependencies=[Depends(get_current_user)]
)
async def create_item(
    request: ItemRequest,
    controller: v1Controller = Depends(get_controller)
):
    """
    Crea un nuevo item.

    Args:
        request: Datos del item a crear

    Returns:
        Item creado con ID asignado
    """
    return await controller.create_item(request)


@router.put(
    "/items/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar item",
    dependencies=[Depends(get_current_user)]
)
async def update_item(
    item_id: int,
    request: ItemRequest,
    controller: v1Controller = Depends(get_controller)
):
    """
    Actualiza un item existente.

    Args:
        item_id: ID del item a actualizar
        request: Nuevos datos del item

    Returns:
        Item actualizado
    """
    return await controller.update_item(item_id, request)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar item",
    dependencies=[Depends(get_current_user)]
)
async def delete_item(
    item_id: int,
    controller: v1Controller = Depends(get_controller)
):
    """
    Elimina un item.

    Args:
        item_id: ID del item a eliminar

    Returns:
        No content
    """
    await controller.delete_item(item_id)
    return None

# endregion


# region Endpoints públicos (sin autenticación)

@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Estado del servicio",
    description="Endpoint público para health check"
)
async def get_status():
    """
    Health check endpoint - no requiere autenticación.

    Returns:
        Estado del servicio
    """
    return {
        "status": "operational",
        "version": "1.0.0",
        "message": "API funcionando correctamente"
    }

# endregion


# TODO: Agregar más endpoints según necesidad del proyecto
# Ejemplos:
# - Búsquedas con filtros
# - Paginación
# - Operaciones batch
# - Webhooks
# - File uploads
