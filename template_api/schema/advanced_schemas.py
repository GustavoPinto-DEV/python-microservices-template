"""
Schemas Avanzados

Schemas Pydantic para casos de uso comunes:
- Paginación
- Filtros y búsquedas
- File uploads
- Responses estandarizados
"""

from pydantic import BaseModel, Field, validator
from typing import Generic, TypeVar, Optional, List, Any
from datetime import datetime
from enum import Enum


# ==========================================
# Paginación
# ==========================================

T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    Parámetros de paginación para queries.

    Uso:
        @router.get("/items")
        async def get_items(pagination: PaginationParams = Depends()):
            ...
    """
    page: int = Field(1, ge=1, description="Número de página (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items por página (max 100)")

    @property
    def offset(self) -> int:
        """Calcula el offset para SQL LIMIT/OFFSET"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Alias para page_size"""
        return self.page_size


class PaginationMeta(BaseModel):
    """Metadatos de paginación en responses"""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Response paginado genérico.

    Uso:
        return PaginatedResponse(
            data=[...],
            meta=PaginationMeta(page=1, page_size=20, total_items=100, ...)
        )
    """
    data: List[T]
    meta: PaginationMeta

    class Config:
        json_schema_extra = {
            "example": {
                "data": [...],
                "meta": {
                    "page": 1,
                    "page_size": 20,
                    "total_items": 100,
                    "total_pages": 5,
                    "has_next": True,
                    "has_previous": False
                }
            }
        }


# ==========================================
# Filtros y Búsquedas
# ==========================================

class SortOrder(str, Enum):
    """Orden de clasificación"""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(str, Enum):
    """Operadores de filtro"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_EQUAL = "lte"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"


class SearchParams(BaseModel):
    """
    Parámetros de búsqueda.

    Uso:
        @router.get("/items/search")
        async def search_items(search: SearchParams = Depends()):
            ...
    """
    q: Optional[str] = Field(None, description="Término de búsqueda")
    fields: Optional[List[str]] = Field(None, description="Campos donde buscar")
    sort_by: Optional[str] = Field(None, description="Campo para ordenar")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Orden de clasificación")

    @validator('q')
    def validate_query(cls, v):
        """Validar que la búsqueda tenga al menos 2 caracteres"""
        if v and len(v) < 2:
            raise ValueError('La búsqueda debe tener al menos 2 caracteres')
        return v


class DateRangeFilter(BaseModel):
    """Filtro por rango de fechas"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validar que end_date sea mayor que start_date"""
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError('end_date debe ser mayor que start_date')
        return v


# ==========================================
# File Upload
# ==========================================

class FileUploadResponse(BaseModel):
    """Response para uploads de archivos"""
    filename: str
    file_size: int
    content_type: str
    file_path: str
    uploaded_at: datetime = Field(default_factory=datetime.now)
    url: Optional[str] = None  # URL pública si aplica

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "document.pdf",
                "file_size": 1024000,
                "content_type": "application/pdf",
                "file_path": "/uploads/2025/01/document.pdf",
                "uploaded_at": "2025-01-06T10:00:00",
                "url": "https://example.com/files/document.pdf"
            }
        }


class FileMetadata(BaseModel):
    """Metadatos de archivos"""
    mime_type: str
    size_bytes: int
    extension: str
    is_image: bool = False
    is_document: bool = False
    dimensions: Optional[dict] = None  # Para imágenes: {"width": 1920, "height": 1080}


# ==========================================
# Responses Estandarizados
# ==========================================

class SuccessResponse(BaseModel):
    """Response exitoso genérico"""
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorDetail(BaseModel):
    """Detalle de un error específico"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Response de error estandarizado"""
    success: bool = False
    error: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    path: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Error de validación",
                "details": [
                    {
                        "field": "email",
                        "message": "Email inválido",
                        "code": "INVALID_EMAIL"
                    }
                ],
                "timestamp": "2025-01-06T10:00:00",
                "path": "/api/v1/users"
            }
        }


class BatchOperationResult(BaseModel):
    """Resultado de operación batch"""
    total: int
    successful: int
    failed: int
    errors: Optional[List[ErrorDetail]] = None


# ==========================================
# Bulk Operations
# ==========================================

class BulkCreateRequest(BaseModel, Generic[T]):
    """Request para crear múltiples items"""
    items: List[T] = Field(..., min_items=1, max_items=100)


class BulkUpdateRequest(BaseModel):
    """Request para actualizar múltiples items"""
    ids: List[int] = Field(..., min_items=1)
    data: dict


class BulkDeleteRequest(BaseModel):
    """Request para eliminar múltiples items"""
    ids: List[int] = Field(..., min_items=1, max_items=100)


# ==========================================
# Health Check
# ==========================================

class HealthCheckResponse(BaseModel):
    """Response de health check"""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    response_time_ms: float
    checks: dict
    version: str
    environment: str


# ==========================================
# Webhook
# ==========================================

class WebhookPayload(BaseModel):
    """Payload genérico de webhook"""
    event: str
    timestamp: datetime = Field(default_factory=datetime.now)
    data: dict
    signature: Optional[str] = None  # Para verificar autenticidad


# ==========================================
# Export/Import
# ==========================================

class ExportFormat(str, Enum):
    """Formatos de exportación"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PDF = "pdf"


class ExportRequest(BaseModel):
    """Request para exportar datos"""
    format: ExportFormat
    filters: Optional[dict] = None
    fields: Optional[List[str]] = None  # Campos a incluir


class ImportResult(BaseModel):
    """Resultado de importación"""
    total_rows: int
    imported: int
    skipped: int
    errors: List[ErrorDetail] = []
