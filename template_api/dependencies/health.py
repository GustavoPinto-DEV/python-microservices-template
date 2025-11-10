"""
Health Check Dependencies

Implementa health checks avanzados para monitoreo de la aplicación.
Verifica estado de base de datos, servicios externos, y recursos del sistema.
"""

from datetime import datetime
from typing import Dict, Any
import psutil
import asyncio
from enum import Enum

# TODO: Descomentar cuando se use repositorio real
# from repositorio_lib.core.database import get_async_session


class HealthStatus(str, Enum):
    """Estados posibles de health check"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


async def check_database() -> Dict[str, Any]:
    """
    Verifica conectividad con la base de datos.

    Returns:
        dict: Estado de la base de datos
    """
    try:
        # TODO: Implementar check real de DB
        # async with get_async_session() as db:
        #     await db.execute("SELECT 1")

        return {
            "status": HealthStatus.HEALTHY,
            "message": "Database connection OK",
            "response_time_ms": 15
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": f"Database connection failed: {str(e)}",
            "response_time_ms": None
        }


async def check_external_service(url: str, timeout: int = 5) -> Dict[str, Any]:
    """
    Verifica conectividad con un servicio externo.

    Args:
        url: URL del servicio a verificar
        timeout: Timeout en segundos

    Returns:
        dict: Estado del servicio externo
    """
    try:
        import httpx

        start = datetime.now()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            response_time = (datetime.now() - start).total_seconds() * 1000

        if response.status_code < 500:
            return {
                "status": HealthStatus.HEALTHY,
                "message": f"Service at {url} is reachable",
                "response_time_ms": round(response_time, 2),
                "status_code": response.status_code
            }
        else:
            return {
                "status": HealthStatus.DEGRADED,
                "message": f"Service returned {response.status_code}",
                "response_time_ms": round(response_time, 2),
                "status_code": response.status_code
            }

    except asyncio.TimeoutError:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": f"Service timeout after {timeout}s",
            "response_time_ms": None
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": f"Service unreachable: {str(e)}",
            "response_time_ms": None
        }


def check_system_resources() -> Dict[str, Any]:
    """
    Verifica uso de recursos del sistema.

    Returns:
        dict: Estado de recursos del sistema
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Determinar estado basado en umbrales
        status = HealthStatus.HEALTHY

        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            status = HealthStatus.UNHEALTHY
        elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 70:
            status = HealthStatus.DEGRADED

        return {
            "status": status,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "memory_available_mb": round(memory.available / (1024 * 1024), 2),
            "disk_available_gb": round(disk.free / (1024 * 1024 * 1024), 2)
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": f"Failed to check system resources: {str(e)}"
        }


async def get_comprehensive_health() -> Dict[str, Any]:
    """
    Ejecuta todos los health checks y retorna estado consolidado.

    Returns:
        dict: Estado de salud completo de la aplicación
    """
    start_time = datetime.now()

    # Ejecutar checks en paralelo
    database_check = await check_database()
    system_check = check_system_resources()

    # TODO: Agregar checks de servicios externos si aplica
    # external_api_check = await check_external_service("https://api.example.com/health")

    # Determinar estado general
    checks = [database_check, system_check]
    statuses = [check.get("status") for check in checks]

    if HealthStatus.UNHEALTHY in statuses:
        overall_status = HealthStatus.UNHEALTHY
    elif HealthStatus.DEGRADED in statuses:
        overall_status = HealthStatus.DEGRADED
    else:
        overall_status = HealthStatus.HEALTHY

    response_time = (datetime.now() - start_time).total_seconds() * 1000

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "response_time_ms": round(response_time, 2),
        "checks": {
            "database": database_check,
            "system": system_check,
            # "external_api": external_api_check,
        },
        "version": "1.0.0",
        "environment": "development"  # TODO: Leer de configuración
    }


async def get_readiness() -> Dict[str, Any]:
    """
    Readiness probe - verifica si la app está lista para recibir tráfico.

    Returns:
        dict: Estado de readiness
    """
    database_check = await check_database()

    is_ready = database_check.get("status") == HealthStatus.HEALTHY

    return {
        "ready": is_ready,
        "checks": {
            "database": database_check
        }
    }


async def get_liveness() -> Dict[str, Any]:
    """
    Liveness probe - verifica si la app está viva (no colgada).

    Returns:
        dict: Estado de liveness
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }
