"""Utilidades compartidas"""
import asyncio
import logging

logger = logging.getLogger(__name__)

async def reintentar_hasta_exito(funcion, nombre: str = "Operación", max_intentos: int = 3, delay_inicial: int = 5):
    """Ejecuta función con reintentos"""
    for intento in range(1, max_intentos + 1):
        try:
            logger.info(f"Ejecutando {nombre} (intento {intento}/{max_intentos})")
            await funcion()
            logger.info(f"✅ {nombre} exitoso")
            return
        except Exception as e:
            logger.error(f"❌ Error en {nombre}: {e}")
            if intento < max_intentos:
                delay = delay_inicial * (2 ** (intento - 1))
                logger.info(f"⏳ Reintentando en {delay}s...")
                await asyncio.sleep(delay)
            else:
                raise

# TODO: Agregar más utilidades compartidas
