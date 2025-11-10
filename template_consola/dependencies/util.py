"""
Utilidades específicas del proyecto Consola

Funciones helper y utilities que son específicas de este servicio de consola.
Para utilidades compartidas entre proyectos, usar repositorio_lib/utils/
"""

import logging
import asyncio
from typing import Optional, Callable, Any
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


async def reintentar_operacion(
    funcion: Callable,
    max_intentos: int = 3,
    delay_inicial: int = 5,
    nombre: str = "Operación"
) -> Any:
    """
    Ejecuta una función con reintentos automáticos y backoff exponencial.

    Args:
        funcion: Función async a ejecutar
        max_intentos: Número máximo de intentos
        delay_inicial: Delay inicial en segundos
        nombre: Nombre descriptivo para logging

    Returns:
        Resultado de la función

    Raises:
        Exception: Si todos los intentos fallan
    """
    for intento in range(1, max_intentos + 1):
        try:
            logger.info(f"Ejecutando {nombre} (intento {intento}/{max_intentos})")
            resultado = await funcion()
            logger.info(f"✅ {nombre} exitoso")
            return resultado

        except Exception as e:
            logger.error(f"❌ Error en {nombre} (intento {intento}): {e}")

            if intento < max_intentos:
                # Backoff exponencial
                delay = delay_inicial * (2 ** (intento - 1))
                logger.info(f"⏳ Reintentando en {delay} segundos...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"❌ {nombre} falló después de {max_intentos} intentos")
                raise


async def llamar_api_externa(
    url: str,
    method: str = "GET",
    headers: Optional[dict] = None,
    data: Optional[dict] = None,
    timeout: int = 30,
    reintentar: bool = True
) -> Optional[dict]:
    """
    Realiza llamada a API externa con manejo de errores y reintentos.

    Args:
        url: URL de la API
        method: Método HTTP
        headers: Headers HTTP
        data: Datos para POST/PUT
        timeout: Timeout en segundos
        reintentar: Si debe reintentar en caso de error

    Returns:
        Response JSON o None si hay error
    """
    async def _hacer_llamada():
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=data)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")

            response.raise_for_status()
            return response.json()

    try:
        if reintentar:
            return await reintentar_operacion(
                _hacer_llamada,
                max_intentos=3,
                nombre=f"API {method} {url}"
            )
        else:
            return await _hacer_llamada()

    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP {e.response.status_code}: {url}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Error de conexión: {url} - {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado llamando API: {e}", exc_info=True)
        return None


def formatear_duracion(segundos: float) -> str:
    """
    Formatea duración en formato legible.

    Args:
        segundos: Duración en segundos

    Returns:
        String formateado (ej: "2h 30m 15s")
    """
    if segundos < 60:
        return f"{segundos:.1f}s"

    minutos = int(segundos // 60)
    segundos_restantes = segundos % 60

    if minutos < 60:
        return f"{minutos}m {segundos_restantes:.0f}s"

    horas = int(minutos // 60)
    minutos_restantes = minutos % 60

    return f"{horas}h {minutos_restantes}m"


def calcular_siguiente_ejecucion(intervalo_minutos: int) -> datetime:
    """
    Calcula la hora de la próxima ejecución.

    Args:
        intervalo_minutos: Intervalo en minutos

    Returns:
        Datetime de la próxima ejecución
    """
    from datetime import timedelta
    return datetime.now() + timedelta(minutes=intervalo_minutos)


async def procesar_en_lotes(
    items: list,
    funcion_procesamiento: Callable,
    batch_size: int = 10,
    paralelo: bool = False
) -> tuple[int, int]:
    """
    Procesa una lista de items en lotes.

    Args:
        items: Lista de items a procesar
        funcion_procesamiento: Función async que procesa cada item
        batch_size: Tamaño del lote
        paralelo: Si True, procesa items en paralelo dentro de cada lote

    Returns:
        Tupla (exitosos, fallidos)
    """
    exitosos = 0
    fallidos = 0
    total = len(items)

    for i in range(0, total, batch_size):
        lote = items[i:i + batch_size]
        logger.info(f"Procesando lote {i//batch_size + 1} ({len(lote)} items)")

        if paralelo:
            # Procesar en paralelo
            tareas = [funcion_procesamiento(item) for item in lote]
            resultados = await asyncio.gather(*tareas, return_exceptions=True)

            for resultado in resultados:
                if isinstance(resultado, Exception):
                    fallidos += 1
                else:
                    exitosos += 1
        else:
            # Procesar secuencialmente
            for item in lote:
                try:
                    await funcion_procesamiento(item)
                    exitosos += 1
                except Exception as e:
                    logger.error(f"Error procesando item: {e}")
                    fallidos += 1

        logger.info(f"Lote completado: {exitosos} ok, {fallidos} errores")

    return exitosos, fallidos


def crear_reporte_ejecucion(
    inicio: datetime,
    fin: datetime,
    registros_procesados: int,
    exitosos: int,
    fallidos: int,
    errores: list = None
) -> dict:
    """
    Crea un reporte estructurado de una ejecución.

    Args:
        inicio: Timestamp de inicio
        fin: Timestamp de fin
        registros_procesados: Total de registros procesados
        exitosos: Cantidad de exitosos
        fallidos: Cantidad de fallidos
        errores: Lista de errores ocurridos

    Returns:
        Diccionario con reporte
    """
    duracion = (fin - inicio).total_seconds()

    return {
        "inicio": inicio.isoformat(),
        "fin": fin.isoformat(),
        "duracion_segundos": duracion,
        "duracion_formateada": formatear_duracion(duracion),
        "registros_procesados": registros_procesados,
        "exitosos": exitosos,
        "fallidos": fallidos,
        "tasa_exito": (exitosos / registros_procesados * 100) if registros_procesados > 0 else 0,
        "errores": errores or []
    }


async def enviar_notificacion(
    titulo: str,
    mensaje: str,
    nivel: str = "info",
    destinos: list = None
):
    """
    Envía notificaciones por diferentes canales.

    Args:
        titulo: Título de la notificación
        mensaje: Contenido del mensaje
        nivel: Nivel de severidad (info, warning, error)
        destinos: Lista de destinos (email, slack, etc.)

    TODO: Implementar canales de notificación reales
    """
    logger.info(f"📧 Notificación [{nivel}]: {titulo} - {mensaje}")

    # TODO: Implementar envío real
    # if "email" in destinos:
    #     await enviar_email(titulo, mensaje)
    # if "slack" in destinos:
    #     await enviar_slack(titulo, mensaje)


# TODO: Agregar más utilidades según necesidad del proyecto
# Ejemplos:
# - Validaciones específicas
# - Parsers de datos
# - Helpers de SFTP
# - Generadores de archivos (CSV, Excel, PDF)
# - Compresión/descompresión
