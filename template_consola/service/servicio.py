"""
Servicio Principal

Orquesta la ejecución de los procesos batch de la consola.
Maneja el ciclo de vida del servicio y coordina las tareas.
"""

import asyncio
import logging
from datetime import datetime
import os

# Processes
from processes.ejemplo_proceso import ejecutar_proceso_ejemplo

# TODO: Descomentar cuando tengas repositorio_lib
# from repositorio_lib.utils import reintentar_hasta_exito

logger = logging.getLogger(__name__)


class Servicio:
    """
    Servicio principal de la consola.

    Maneja:
    - Inicio y detención del servicio
    - Ejecución periódica de procesos
    - Manejo de errores y reintentos
    """

    def __init__(self):
        """Inicializa el servicio"""
        self.running = False
        self.task = None

        # Configuración desde env
        self.intervalo_minutos = int(os.getenv("MINUTOS_CONSOLA", "60"))
        self.modo_continuo = os.getenv("ENABLE_CONTINUOUS_MODE", "true").lower() == "true"
        self.max_reintentos = int(os.getenv("MAX_RETRIES", "3"))

        logger.info(f"Servicio configurado:")
        logger.info(f"  - Intervalo: {self.intervalo_minutos} minutos")
        logger.info(f"  - Modo continuo: {self.modo_continuo}")
        logger.info(f"  - Max reintentos: {self.max_reintentos}")

    async def iniciar_servicio(self):
        """
        Inicia el servicio y comienza la ejecución de procesos.
        """
        logger.info("🟢 Iniciando servicio...")

        self.running = True

        # Iniciar tarea principal en background
        self.task = asyncio.create_task(self._run_loop())

        logger.info("✅ Servicio iniciado exitosamente")

    async def detener_servicio(self):
        """
        Detiene el servicio de forma graceful.
        """
        logger.info("🔴 Deteniendo servicio...")

        self.running = False

        # Esperar a que termine la tarea actual
        if self.task:
            try:
                await asyncio.wait_for(self.task, timeout=60)
                logger.info("✅ Tarea actual completada")
            except asyncio.TimeoutError:
                logger.warning("⚠️ Timeout esperando tarea, cancelando...")
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass

        logger.info("✅ Servicio detenido")

    async def _run_loop(self):
        """
        Loop principal del servicio.

        Ejecuta los procesos batch periódicamente según configuración.
        """
        ciclo = 1

        while self.running:
            try:
                logger.info(f"{'='*60}")
                logger.info(f"Iniciando ciclo #{ciclo} - {datetime.now()}")
                logger.info(f"{'='*60}")

                # Ejecutar ciclo de procesos
                await self.ejecutar_ciclo()

                logger.info(f"✅ Ciclo #{ciclo} completado exitosamente")

                # Si no es modo continuo, salir después del primer ciclo
                if not self.modo_continuo:
                    logger.info("Modo de ejecución única - finalizando")
                    self.running = False
                    break

                # Esperar antes del siguiente ciclo
                if self.running:
                    logger.info(
                        f"⏳ Esperando {self.intervalo_minutos} minutos "
                        f"hasta el siguiente ciclo..."
                    )
                    await asyncio.sleep(self.intervalo_minutos * 60)

                ciclo += 1

            except asyncio.CancelledError:
                logger.info("⚠️ Tarea cancelada")
                break
            except Exception as e:
                logger.error(
                    f"❌ Error en ciclo #{ciclo}: {e}",
                    exc_info=True
                )

                # Esperar antes de reintentar
                if self.running:
                    logger.info("⏳ Esperando 5 minutos antes de reintentar...")
                    await asyncio.sleep(300)  # 5 minutos

    async def ejecutar_ciclo(self):
        """
        Ejecuta un ciclo completo de procesos batch.

        Personaliza este método para agregar tus procesos específicos.
        """
        logger.info("🔄 Ejecutando procesos del ciclo...")

        try:
            # TODO: Agregar tus procesos aquí

            # Ejemplo 1: Proceso simple
            await self._ejecutar_con_reintentos(
                ejecutar_proceso_ejemplo,
                "Proceso Ejemplo"
            )

            # Ejemplo 2: Múltiples procesos en secuencia
            # await self._ejecutar_con_reintentos(proceso_1, "Proceso 1")
            # await self._ejecutar_con_reintentos(proceso_2, "Proceso 2")
            # await self._ejecutar_con_reintentos(proceso_3, "Proceso 3")

            # Ejemplo 3: Procesos en paralelo
            # await asyncio.gather(
            #     self._ejecutar_con_reintentos(proceso_a, "Proceso A"),
            #     self._ejecutar_con_reintentos(proceso_b, "Proceso B"),
            #     return_exceptions=True
            # )

            logger.info("✅ Todos los procesos completados")

        except Exception as e:
            logger.error(f"❌ Error ejecutando ciclo: {e}", exc_info=True)
            raise

    async def _ejecutar_con_reintentos(self, funcion, nombre: str):
        """
        Ejecuta una función con reintentos automáticos en caso de error.

        Args:
            funcion: Función async a ejecutar
            nombre: Nombre descriptivo del proceso
        """
        for intento in range(1, self.max_reintentos + 1):
            try:
                logger.info(f"▶️ Ejecutando: {nombre} (intento {intento}/{self.max_reintentos})")
                await funcion()
                logger.info(f"✅ {nombre} completado exitosamente")
                return

            except Exception as e:
                logger.error(
                    f"❌ Error en {nombre} (intento {intento}/{self.max_reintentos}): {e}",
                    exc_info=True
                )

                if intento < self.max_reintentos:
                    # Backoff exponencial: 5s, 10s, 20s
                    delay = 5 * (2 ** (intento - 1))
                    logger.info(f"⏳ Reintentando en {delay} segundos...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"❌ {nombre} falló después de {self.max_reintentos} intentos")
                    raise


# TODO: Agregar funcionalidades adicionales según necesidad
# Ejemplos:
# - Health check endpoint (HTTP server simple)
# - Métricas de ejecución
# - Notificaciones por email/slack en caso de error
# - Pausar/reanudar servicio dinámicamente
# - Ajustar intervalo dinámicamente
