"""
Consola Template - Main Entry Point

Template para servicios de consola/batch basado en asyncio.
Ejecuta procesos en segundo plano de forma continua o programada.

Uso:
    python main.py
"""

import asyncio
import signal
import logging

# Service
from service.servicio import Servicio

# TODO: Descomentar cuando tengas repositorio_lib configurado
# from repositorio_lib.core.logger import setup_logger

# Setup logger
# logger = setup_logger("consola_template", level=logging.INFO, log_to_file=True)

# Alternativa temporal sin repositorio_lib
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Función principal de la consola.

    Servicio en segundo plano que ejecuta procesos batch de forma continua:
    - Actualización automática de datos
    - Procesamiento de tareas pendientes
    - Sincronización con sistemas externos
    - Generación de reportes
    """
    logger.info("🚀 Iniciando servicio de consola...")

    # Inicializar servicio
    servicio = Servicio()
    await servicio.iniciar_servicio()

    # region Signal Handling
    # Manejar señales de terminación para shutdown graceful
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def stop():
        """Callback para detener el servicio"""
        logger.info("⚠️ Señal de detención recibida")
        stop_event.set()

    try:
        # Registrar handlers para SIGINT (Ctrl+C) y SIGTERM (docker stop)
        loop.add_signal_handler(signal.SIGINT, stop)
        loop.add_signal_handler(signal.SIGTERM, stop)
        logger.info("✅ Signal handlers registrados")
    except NotImplementedError:
        # Windows no soporta add_signal_handler
        logger.warning(
            "⚠️ Señales no soportadas en esta plataforma. "
            "Usa Ctrl+C para salir."
        )
    # endregion

    logger.info("✅ Servicio en ejecución. Presiona Ctrl+C para detener")

    try:
        # Esperar señal de detención
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("⌨️ Interrupción por teclado recibida")

    # Detener servicio de forma limpia
    await servicio.detener_servicio()
    logger.info("🛑 Servicio de consola finalizado")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por usuario")
    except Exception as e:
        logger.error(f"Error fatal en aplicación: {e}", exc_info=True)
        exit(1)
