"""
Celery Configuration (Ejemplo)

Configuración para tareas asíncronas con Celery.

Uso:
    from config.celery_config import celery_app

    @celery_app.task
    def my_task(param):
        # Tarea asíncrona
        pass

Ejecutar worker:
    celery -A config.celery_config worker --loglevel=info

Ejecutar beat (tareas programadas):
    celery -A config.celery_config beat --loglevel=info
"""

from celery import Celery
from celery.schedules import crontab
import os

# Configuración
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# Crear app Celery
celery_app = Celery(
    "template_api",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Configuración
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Mexico_City",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Tareas programadas (Celery Beat)
celery_app.conf.beat_schedule = {
    # Ejemplo: Tarea que se ejecuta cada hora
    "cleanup-old-data": {
        "task": "tasks.cleanup_old_data",
        "schedule": crontab(minute=0),  # Cada hora en punto
    },
    # Ejemplo: Tarea diaria a las 3 AM
    "daily-report": {
        "task": "tasks.generate_daily_report",
        "schedule": crontab(hour=3, minute=0),
    },
    # Ejemplo: Cada 5 minutos
    "health-check": {
        "task": "tasks.health_check",
        "schedule": 300.0,  # 5 minutos en segundos
    },
}


# Ejemplo de tareas
@celery_app.task(name="tasks.example_task")
def example_task(param: str):
    """
    Tarea de ejemplo.

    Invocar desde código:
        from config.celery_config import example_task
        example_task.delay("valor")  # Asíncrono
        example_task.apply_async(args=["valor"], countdown=60)  # Con delay
    """
    print(f"Ejecutando tarea con parámetro: {param}")
    # Lógica de la tarea
    return {"status": "completed", "param": param}


@celery_app.task(name="tasks.send_email")
def send_email_task(to: str, subject: str, body: str):
    """Tarea para enviar emails de forma asíncrona"""
    # TODO: Implementar envío de email
    print(f"Enviando email a {to}: {subject}")
    return {"sent": True}


@celery_app.task(name="tasks.process_file")
def process_file_task(file_path: str):
    """Tarea para procesamiento de archivos pesado"""
    # TODO: Implementar procesamiento
    print(f"Procesando archivo: {file_path}")
    return {"processed": True}


@celery_app.task(name="tasks.cleanup_old_data")
def cleanup_old_data():
    """Limpieza de datos antiguos (ejecutada periódicamente)"""
    # TODO: Implementar limpieza
    print("Limpiando datos antiguos...")
    return {"cleaned": 0}


@celery_app.task(name="tasks.generate_daily_report")
def generate_daily_report():
    """Genera reporte diario (ejecutada periódicamente)"""
    # TODO: Implementar generación de reporte
    print("Generando reporte diario...")
    return {"generated": True}


@celery_app.task(name="tasks.health_check")
def health_check_task():
    """Health check periódico"""
    # TODO: Implementar health check
    return {"healthy": True}
