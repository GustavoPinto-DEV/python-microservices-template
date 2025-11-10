"""
Schemas Pydantic

Define los modelos de datos para request/response de la API.
Proporciona validación automática y documentación de OpenAPI.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# region Schemas de Autenticación

class LoginRequest(BaseModel):
    """Request para login de usuario"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "secretpassword"
            }
        }


class LoginResponse(BaseModel):
    """Response de login exitoso con token JWT"""
    access_token: str = Field(..., description="Token JWT para autenticación")
    token_type: str = Field(default="bearer", description="Tipo de token")
    username: str = Field(..., description="Nombre del usuario autenticado")
    expires_in: Optional[int] = Field(None, description="Tiempo de expiración en segundos")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "username": "admin",
                "expires_in": 7200
            }
        }

# endregion


# region Schemas de Items (ejemplo)

class ItemRequest(BaseModel):
    """Request para crear/actualizar item"""
    name: str = Field(..., min_length=3, max_length=100, description="Nombre del item")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del item")
    active: bool = Field(default=True, description="Estado activo/inactivo")
    price: Optional[float] = Field(None, gt=0, description="Precio del item")
    tags: Optional[List[str]] = Field(default=[], description="Etiquetas del item")

    @validator('name')
    def name_must_not_be_empty(cls, v):
        """Valida que el nombre no esté vacío"""
        if not v or not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()

    @validator('price')
    def price_must_be_positive(cls, v):
        """Valida que el precio sea positivo"""
        if v is not None and v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Producto Ejemplo",
                "description": "Descripción detallada del producto",
                "active": True,
                "price": 99.99,
                "tags": ["nuevo", "destacado"]
            }
        }


class ItemResponse(BaseModel):
    """Response con datos de un item"""
    id: int = Field(..., description="ID único del item")
    name: str = Field(..., description="Nombre del item")
    description: Optional[str] = Field(None, description="Descripción del item")
    active: bool = Field(..., description="Estado activo/inactivo")
    price: Optional[float] = Field(None, description="Precio del item")
    tags: Optional[List[str]] = Field(default=[], description="Etiquetas del item")
    created_at: Optional[datetime] = Field(None, description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Producto Ejemplo",
                "description": "Descripción detallada del producto",
                "active": True,
                "price": 99.99,
                "tags": ["nuevo", "destacado"],
                "created_at": "2025-01-01T10:00:00",
                "updated_at": "2025-01-01T10:00:00"
            }
        }

# endregion


# region Schemas de Error

class ErrorResponse(BaseModel):
    """Response estándar para errores"""
    error: str = Field(..., description="Código o tipo de error")
    message: str = Field(..., description="Mensaje descriptivo del error")
    detail: Optional[str] = Field(None, description="Detalle adicional del error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Error de validación en los datos enviados",
                "detail": "El campo 'name' es requerido",
                "timestamp": "2025-01-01T10:00:00"
            }
        }


class ValidationErrorDetail(BaseModel):
    """Detalle de error de validación"""
    loc: List[str] = Field(..., description="Ubicación del error")
    msg: str = Field(..., description="Mensaje del error")
    type: str = Field(..., description="Tipo de error")


class ValidationErrorResponse(BaseModel):
    """Response para errores de validación"""
    detail: List[ValidationErrorDetail] = Field(..., description="Lista de errores de validación")

# endregion


# region Schemas de Paginación

class PaginationParams(BaseModel):
    """Parámetros de paginación"""
    page: int = Field(default=1, ge=1, description="Número de página")
    page_size: int = Field(default=10, ge=1, le=100, description="Tamaño de página")


class PaginatedResponse(BaseModel):
    """Response paginado genérico"""
    data: List[dict] = Field(..., description="Datos de la página actual")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    total_pages: int = Field(..., description="Total de páginas")

    @classmethod
    def create(cls, data: List[dict], total: int, page: int, page_size: int):
        """Helper para crear response paginado"""
        import math
        return cls(
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if page_size > 0 else 0
        )

# endregion


# region Schemas de Usuario (ejemplo adicional)

class UserBase(BaseModel):
    """Base para schemas de usuario"""
    email: EmailStr = Field(..., description="Email del usuario")
    full_name: str = Field(..., min_length=1, max_length=100, description="Nombre completo")
    is_active: bool = Field(default=True, description="Usuario activo")


class UserCreate(UserBase):
    """Request para crear usuario"""
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")


class UserUpdate(BaseModel):
    """Request para actualizar usuario (todos los campos opcionales)"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """Response con datos de usuario"""
    id: int = Field(..., description="ID del usuario")
    created_at: datetime = Field(..., description="Fecha de creación")

    class Config:
        from_attributes = True  # Permite crear desde ORM models

# endregion


# TODO: Agregar más schemas según necesidad del proyecto
# Ejemplos:
# - Schemas para diferentes entidades del dominio
# - Schemas para filtros y búsquedas
# - Schemas para operaciones batch
# - Schemas para webhooks
# - Schemas para reportes
