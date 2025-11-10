"""
Manejadores de excepciones para Consola

Define excepciones personalizadas y helpers para manejo de errores
en procesos batch.
"""

import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# Excepciones personalizadas

class ProcesoError(Exception):
    """Excepción base para errores de procesos batch"""
    def __init__(self, proceso: str, message: str, detail: Optional[str] = None):
        self.proceso = proceso
        self.message = message
        self.detail = detail
        self.timestamp = datetime.now()
        super().__init__(self.message)


class DataValidationError(ProcesoError):
    """Error de validación de datos"""
    def __init__(self, proceso: str, campo: str, valor: any, razon: str):
        self.campo = campo
        self.valor = valor
        message = f"Validación fallida en campo '{campo}': {razon}"
        super().__init__(proceso, message, detail=f"Valor: {valor}")


class ExternalServiceError(ProcesoError):
    """Error al comunicarse con servicio externo"""
    def __init__(self, proceso: str, servicio: str, detail: Optional[str] = None):
        self.servicio = servicio
        message = f"Error comunicándose con servicio externo: {servicio}"
        super().__init__(proceso, message, detail)


class DatabaseError(ProcesoError):
    """Error de base de datos"""
    def __init__(self, proceso: str, operacion: str, detail: Optional[str] = None):
        self.operacion = operacion
        message = f"Error en operación de base de datos: {operacion}"
        super().__init__(proceso, message, detail)


class ConfigurationError(Exception):
    """Error de configuración del servicio"""
    def __init__(self, parametro: str, razon: str):
        self.parametro = parametro
        self.razon = razon
        message = f"Error de configuración en '{parametro}': {razon}"
        super().__init__(message)


class ProcessTimeoutError(ProcesoError):
    """Timeout en ejecución de proceso"""
    def __init__(self, proceso: str, timeout_segundos: int):
        self.timeout_segundos = timeout_segundos
        message = f"Proceso excedió timeout de {timeout_segundos} segundos"
        super().__init__(proceso, message)


# Helpers para manejo de errores

def log_error(error: Exception, contexto: Optional[dict] = None):
    """
    Registra un error con contexto adicional.

    Args:
        error: Excepción a registrar
        contexto: Información adicional de contexto
    """
    error_info = {
        "tipo": type(error).__name__,
        "mensaje": str(error),
        "timestamp": datetime.now().isoformat()
    }

    if contexto:
        error_info["contexto"] = contexto

    if isinstance(error, ProcesoError):
        error_info["proceso"] = error.proceso
        error_info["detalle"] = error.detail

    logger.error(f"Error registrado: {error_info}", exc_info=True)

    return error_info


async def manejar_error_proceso(
    error: Exception,
    proceso: str,
    continuar_en_error: bool = False
) -> bool:
    """
    Maneja un error de proceso decidiendo si continuar o abortar.

    Args:
        error: Excepción ocurrida
        proceso: Nombre del proceso
        continuar_en_error: Si debe continuar ejecutando después del error

    Returns:
        True si debe continuar, False si debe abortar
    """
    log_error(error, {"proceso": proceso})

    # Errores críticos que siempre abortan
    errores_criticos = (
        ConfigurationError,
        DatabaseError,
        ProcessTimeoutError
    )

    if isinstance(error, errores_criticos):
        logger.error(f"❌ Error crítico en {proceso}. Abortando.")
        return False

    # Errores recuperables
    if continuar_en_error:
        logger.warning(f"⚠️ Error en {proceso}. Continuando ejecución.")
        return True

    return False


def crear_reporte_errores(errores: list) -> dict:
    """
    Crea un reporte consolidado de errores.

    Args:
        errores: Lista de errores ocurridos

    Returns:
        Diccionario con reporte de errores
    """
    if not errores:
        return {
            "total_errores": 0,
            "errores_por_tipo": {},
            "errores_criticos": 0,
            "detalles": []
        }

    # Contar por tipo
    errores_por_tipo = {}
    errores_criticos = 0

    for error in errores:
        tipo = type(error).__name__
        errores_por_tipo[tipo] = errores_por_tipo.get(tipo, 0) + 1

        if isinstance(error, (ConfigurationError, DatabaseError, ProcessTimeoutError)):
            errores_criticos += 1

    return {
        "total_errores": len(errores),
        "errores_por_tipo": errores_por_tipo,
        "errores_criticos": errores_criticos,
        "detalles": [
            {
                "tipo": type(e).__name__,
                "mensaje": str(e),
                "timestamp": getattr(e, 'timestamp', None)
            }
            for e in errores[:10]  # Limitar a 10 errores en detalle
        ]
    }


class ErrorAcumulador:
    """
    Acumulador de errores para procesos batch.

    Útil para recolectar errores durante procesamiento y
    generar reporte al final.
    """

    def __init__(self):
        self.errores = []
        self.errores_por_tipo = {}

    def agregar(self, error: Exception, contexto: Optional[dict] = None):
        """Agrega un error al acumulador"""
        error_info = log_error(error, contexto)
        self.errores.append(error_info)

        tipo = type(error).__name__
        self.errores_por_tipo[tipo] = self.errores_por_tipo.get(tipo, 0) + 1

    def tiene_errores(self) -> bool:
        """Verifica si hay errores acumulados"""
        return len(self.errores) > 0

    def tiene_errores_criticos(self) -> bool:
        """Verifica si hay errores críticos"""
        return any(
            e.get("tipo") in ["ConfigurationError", "DatabaseError", "ProcessTimeoutError"]
            for e in self.errores
        )

    def get_reporte(self) -> dict:
        """Genera reporte de errores"""
        return {
            "total": len(self.errores),
            "por_tipo": self.errores_por_tipo,
            "criticos": self.tiene_errores_criticos(),
            "detalles": self.errores[:10]  # Primeros 10
        }

    def clear(self):
        """Limpia errores acumulados"""
        self.errores = []
        self.errores_por_tipo = {}


# TODO: Agregar más excepciones según necesidad
# Ejemplos:
# - FileProcessingError
# - SFTPError
# - NotificationError
# - RetryExhaustedError
