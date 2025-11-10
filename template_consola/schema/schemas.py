"""
Schemas Pydantic para Consola

Define modelos de datos para validación y serialización
de datos usados en procesos batch.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums

class EstadoProceso(str, Enum):
    """Estados posibles de un proceso"""
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    CANCELADO = "cancelado"


class TipoProceso(str, Enum):
    """Tipos de procesos"""
    ACTUALIZACION = "actualizacion"
    SINCRONIZACION = "sincronizacion"
    LIMPIEZA = "limpieza"
    REPORTE = "reporte"
    INTEGRACION = "integracion"


# Schemas de Proceso

class ProcesoBase(BaseModel):
    """Schema base para procesos"""
    nombre: str = Field(..., min_length=1, max_length=100)
    tipo: TipoProceso
    descripcion: Optional[str] = None


class ProcesoEjecucion(ProcesoBase):
    """Schema para registro de ejecución de proceso"""
    id: int = Field(..., description="ID de la ejecución")
    estado: EstadoProceso
    inicio: datetime
    fin: Optional[datetime] = None
    duracion_segundos: Optional[float] = None
    registros_procesados: int = Field(default=0, ge=0)
    registros_exitosos: int = Field(default=0, ge=0)
    registros_fallidos: int = Field(default=0, ge=0)
    mensaje_error: Optional[str] = None

    @validator('registros_exitosos')
    def validar_exitosos(cls, v, values):
        """Valida que exitosos no exceda procesados"""
        if 'registros_procesados' in values and v > values['registros_procesados']:
            raise ValueError('exitosos no puede exceder procesados')
        return v

    @validator('registros_fallidos')
    def validar_fallidos(cls, v, values):
        """Valida que fallidos no exceda procesados"""
        if 'registros_procesados' in values and v > values['registros_procesados']:
            raise ValueError('fallidos no puede exceder procesados')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "nombre": "Actualización de Convenios",
                "tipo": "actualizacion",
                "estado": "completado",
                "inicio": "2025-01-01T10:00:00",
                "fin": "2025-01-01T10:05:00",
                "duracion_segundos": 300,
                "registros_procesados": 100,
                "registros_exitosos": 95,
                "registros_fallidos": 5
            }
        }


# Schemas de Métricas

class Metricas(BaseModel):
    """Schema para métricas del servicio"""
    total_ejecuciones: int = Field(default=0, ge=0)
    ejecuciones_exitosas: int = Field(default=0, ge=0)
    ejecuciones_fallidas: int = Field(default=0, ge=0)
    ultima_ejecucion: Optional[datetime] = None
    tiempo_promedio_segundos: Optional[float] = Field(None, ge=0)
    tasa_exito: float = Field(default=0.0, ge=0, le=100)

    @classmethod
    def calcular(cls, ejecuciones: List[ProcesoEjecucion]):
        """Helper para calcular métricas desde lista de ejecuciones"""
        total = len(ejecuciones)
        exitosas = sum(1 for e in ejecuciones if e.estado == EstadoProceso.COMPLETADO)
        fallidas = sum(1 for e in ejecuciones if e.estado == EstadoProceso.FALLIDO)

        tiempos = [e.duracion_segundos for e in ejecuciones if e.duracion_segundos]
        tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else None

        ultima = max(ejecuciones, key=lambda e: e.inicio) if ejecuciones else None

        return cls(
            total_ejecuciones=total,
            ejecuciones_exitosas=exitosas,
            ejecuciones_fallidas=fallidas,
            ultima_ejecucion=ultima.inicio if ultima else None,
            tiempo_promedio_segundos=tiempo_promedio,
            tasa_exito=(exitosas / total * 100) if total > 0 else 0
        )


# Schemas de Registro/Item

class RegistroBase(BaseModel):
    """Schema base para registros a procesar"""
    id: int
    estado: str
    fecha_creacion: datetime


class RegistroRequest(BaseModel):
    """Request para crear/actualizar registro"""
    datos: Dict[str, Any] = Field(..., description="Datos del registro")
    prioridad: Optional[int] = Field(default=0, ge=0, le=10)


class RegistroResponse(RegistroBase):
    """Response con datos de registro procesado"""
    resultado: Optional[str] = None
    fecha_procesamiento: Optional[datetime] = None
    procesado_por: Optional[str] = None


# Schemas de Integración Externa

class APIExternaRequest(BaseModel):
    """Request para API externa"""
    endpoint: str = Field(..., description="Endpoint de la API")
    metodo: str = Field(default="GET", regex="^(GET|POST|PUT|DELETE)$")
    headers: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, Any]] = None
    timeout: int = Field(default=30, ge=1, le=300)


class APIExternaResponse(BaseModel):
    """Response de API externa"""
    status_code: int
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duracion_ms: float


# Schemas de Reporte

class ReporteEjecucion(BaseModel):
    """Reporte detallado de una ejecución"""
    proceso: str
    inicio: datetime
    fin: datetime
    duracion_formateada: str
    resultado: EstadoProceso
    metricas: Dict[str, Any]
    errores: List[Dict[str, Any]] = []
    warnings: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "proceso": "Sincronización TagNet",
                "inicio": "2025-01-01T10:00:00",
                "fin": "2025-01-01T10:05:00",
                "duracion_formateada": "5m 0s",
                "resultado": "completado",
                "metricas": {
                    "registros_procesados": 100,
                    "exitosos": 95,
                    "fallidos": 5,
                    "tasa_exito": 95.0
                },
                "errores": [],
                "warnings": ["5 registros con advertencias"]
            }
        }


# Schemas de Configuración

class ConfiguracionProceso(BaseModel):
    """Configuración de un proceso específico"""
    nombre: str
    habilitado: bool = Field(default=True)
    intervalo_minutos: int = Field(default=60, ge=1)
    max_reintentos: int = Field(default=3, ge=0, le=10)
    timeout_segundos: Optional[int] = Field(None, ge=1)
    parametros: Dict[str, Any] = Field(default_factory=dict)


class ConfiguracionServicio(BaseModel):
    """Configuración global del servicio"""
    modo_continuo: bool = Field(default=True)
    intervalo_minutos: int = Field(default=60, ge=1)
    procesos: List[ConfiguracionProceso] = []
    notificaciones_habilitadas: bool = Field(default=False)
    email_notificaciones: Optional[List[str]] = None


# Schemas de SFTP (ejemplo)

class SFTPConfig(BaseModel):
    """Configuración de conexión SFTP"""
    host: str
    port: int = Field(default=22, ge=1, le=65535)
    username: str
    password: Optional[str] = None
    private_key_path: Optional[str] = None
    remote_path: str = Field(default="/")


class ArchivoSFTP(BaseModel):
    """Información de archivo en SFTP"""
    nombre: str
    ruta: str
    tamano_bytes: int = Field(ge=0)
    fecha_modificacion: datetime
    es_directorio: bool = False


# TODO: Agregar más schemas según necesidad del proyecto
# Ejemplos:
# - Schemas para datos específicos del dominio
# - Schemas para validación de archivos
# - Schemas para notificaciones
# - Schemas para webhooks
# - Schemas para auditoría
