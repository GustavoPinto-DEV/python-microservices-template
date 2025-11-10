"""
Prometheus Metrics

Exporta métricas de la aplicación para Prometheus.

Métricas incluidas:
- Contador de requests por endpoint y status code
- Histograma de latencia de requests
- Gauge de requests activos
- Métricas de sistema (CPU, memoria)
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import psutil


# Definir métricas
http_requests_total = Counter(
    "http_requests_total",
    "Total de HTTP requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "Duración de HTTP requests",
    ["method", "endpoint"]
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Requests HTTP en progreso",
    ["method", "endpoint"]
)

# Métricas de sistema
system_cpu_usage = Gauge(
    "system_cpu_usage_percent",
    "Uso de CPU del sistema"
)

system_memory_usage = Gauge(
    "system_memory_usage_percent",
    "Uso de memoria del sistema"
)

system_disk_usage = Gauge(
    "system_disk_usage_percent",
    "Uso de disco del sistema"
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware que registra métricas de requests"""

    async def dispatch(self, request: Request, call_next):
        # Excluir endpoint de métricas
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        endpoint = request.url.path

        # Incrementar requests en progreso
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Medir tiempo
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise
        finally:
            # Decrementar requests en progreso
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

            # Registrar duración
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Incrementar contador
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

        return response


def update_system_metrics():
    """Actualiza métricas del sistema"""
    system_cpu_usage.set(psutil.cpu_percent())
    system_memory_usage.set(psutil.virtual_memory().percent)
    system_disk_usage.set(psutil.disk_usage('/').percent)


async def metrics_endpoint():
    """
    Endpoint que expone métricas para Prometheus.

    Configurar en Prometheus:
        scrape_configs:
          - job_name: 'fastapi'
            static_configs:
              - targets: ['localhost:8000']
            metrics_path: '/metrics'
    """
    # Actualizar métricas de sistema antes de exportar
    update_system_metrics()

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
