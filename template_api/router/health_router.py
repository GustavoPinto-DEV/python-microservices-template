"""
Health Check Router

Endpoints para monitoreo y health checks de la aplicación.
Compatible con Kubernetes probes y herramientas de monitoreo.
"""

from fastapi import APIRouter, status
from schema.advanced_schemas import HealthCheckResponse
from dependencies.health import (
    get_comprehensive_health,
    get_readiness,
    get_liveness
)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Comprehensive health check",
    description="Retorna estado detallado de la aplicación y sus dependencias"
)
async def health_check():
    """
    Health check completo de la aplicación.

    Verifica:
    - Conectividad con base de datos
    - Recursos del sistema (CPU, memoria, disco)
    - Servicios externos (opcional)

    Returns:
        HealthCheckResponse: Estado de salud completo
    """
    return await get_comprehensive_health()


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Verifica si la app está lista para recibir tráfico (Kubernetes readiness)"
)
async def readiness_probe():
    """
    Readiness probe para Kubernetes.

    Verifica que todos los servicios críticos estén disponibles.
    Si retorna 200, el pod puede recibir tráfico.

    Returns:
        dict: Estado de readiness
    """
    result = await get_readiness()

    if not result["ready"]:
        # Retornar 503 si no está ready
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=result
        )

    return result


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Verifica si la app está viva (Kubernetes liveness)"
)
async def liveness_probe():
    """
    Liveness probe para Kubernetes.

    Verifica que la aplicación no esté colgada.
    Si retorna 200, el pod está vivo.

    Returns:
        dict: Estado de liveness
    """
    return await get_liveness()


@router.get(
    "/health/startup",
    status_code=status.HTTP_200_OK,
    summary="Startup probe",
    description="Verifica si la app ha terminado de iniciar (Kubernetes startup)"
)
async def startup_probe():
    """
    Startup probe para Kubernetes.

    Usado durante el inicio para dar más tiempo antes de
    aplicar liveness/readiness probes.

    Returns:
        dict: Estado de startup
    """
    # Similar a readiness pero con criterios más relajados
    return {"started": True}
