"""
Ejemplo de Proceso Batch

Este módulo muestra cómo implementar un proceso batch típico.
Puedes usar este archivo como base para crear tus propios procesos.
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# TODO: Descomentar cuando tengas repositorio_lib
# from repositorio_lib.core.database import get_async_session
# from repositorio_lib.service.repository import v1Repositorio

logger = logging.getLogger(__name__)


async def ejecutar_proceso_ejemplo():
    """
    Proceso ejemplo que muestra estructura típica de un proceso batch.

    Este proceso:
    1. Consulta datos de la base de datos
    2. Procesa los registros
    3. Actualiza resultados en la base de datos
    4. Registra métricas
    """
    logger.info("📊 Iniciando proceso ejemplo...")

    try:
        # Métricas del proceso
        inicio = datetime.now()
        procesados = 0
        exitosos = 0
        fallidos = 0

        # Paso 1: Obtener datos a procesar
        logger.info("1️⃣ Obteniendo datos a procesar...")
        registros = await obtener_registros_pendientes()
        logger.info(f"   Encontrados {len(registros)} registros pendientes")

        if not registros:
            logger.info("   No hay registros pendientes. Finalizando.")
            return

        # Paso 2: Procesar registros
        logger.info("2️⃣ Procesando registros...")
        for registro in registros:
            try:
                await procesar_registro(registro)
                exitosos += 1
            except Exception as e:
                logger.error(f"   Error procesando registro {registro.get('id')}: {e}")
                fallidos += 1
            finally:
                procesados += 1

            # Progress log cada 10 registros
            if procesados % 10 == 0:
                logger.info(f"   Progreso: {procesados}/{len(registros)}")

        # Paso 3: Registrar resultados
        duracion = (datetime.now() - inicio).total_seconds()
        logger.info("3️⃣ Proceso completado:")
        logger.info(f"   Total procesados: {procesados}")
        logger.info(f"   Exitosos: {exitosos}")
        logger.info(f"   Fallidos: {fallidos}")
        logger.info(f"   Duración: {duracion:.2f}s")

        # TODO: Guardar métricas en BD si es necesario
        # await guardar_metricas_proceso(procesados, exitosos, fallidos, duracion)

    except Exception as e:
        logger.error(f"❌ Error en proceso ejemplo: {e}", exc_info=True)
        raise


async def obtener_registros_pendientes() -> List[Dict[str, Any]]:
    """
    Obtiene registros pendientes de procesar desde la base de datos.

    Returns:
        Lista de registros pendientes
    """
    # TODO: Implementar consulta real a base de datos
    # async with get_async_session() as db:
    #     repositorio = v1Repositorio()
    #     resultado = await repositorio.get_registros_pendientes(db)
    #     return resultado.data

    # Datos de ejemplo
    await asyncio.sleep(0.5)  # Simular consulta DB
    return [
        {"id": 1, "nombre": "Registro 1", "valor": 100},
        {"id": 2, "nombre": "Registro 2", "valor": 200},
        {"id": 3, "nombre": "Registro 3", "valor": 300},
    ]


async def procesar_registro(registro: Dict[str, Any]):
    """
    Procesa un registro individual.

    Args:
        registro: Datos del registro a procesar
    """
    logger.debug(f"   Procesando registro {registro['id']}: {registro['nombre']}")

    # TODO: Implementar lógica de procesamiento
    # Ejemplos:
    # - Validar datos
    # - Calcular valores
    # - Llamar APIs externas
    # - Actualizar base de datos

    # Simular procesamiento
    await asyncio.sleep(0.1)

    # Ejemplo: Actualizar en BD
    # async with get_async_session() as db:
    #     await repositorio.actualizar_registro(
    #         db,
    #         registro['id'],
    #         {"procesado": True, "fecha_proceso": datetime.now()}
    #     )
    #     await db.commit()

    logger.debug(f"   ✓ Registro {registro['id']} procesado exitosamente")


# Ejemplos de otros tipos de procesos comunes

async def proceso_integracion_api():
    """
    Ejemplo de integración con API externa.
    """
    import httpx

    logger.info("🌐 Iniciando integración con API externa...")

    try:
        async with httpx.AsyncClient() as client:
            # Llamar API externa
            response = await client.get("https://api.example.com/data")
            response.raise_for_status()
            datos = response.json()

            # Procesar datos
            logger.info(f"Recibidos {len(datos)} registros de API")

            # Guardar en BD
            # async with get_async_session() as db:
            #     for item in datos:
            #         await repositorio.crear_o_actualizar(db, item)
            #     await db.commit()

            logger.info("✅ Integración API completada")

    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP en API externa: {e.response.status_code}")
        raise
    except Exception as e:
        logger.error(f"Error en integración API: {e}", exc_info=True)
        raise


async def proceso_limpieza_datos():
    """
    Ejemplo de proceso de limpieza/mantenimiento de datos.
    """
    logger.info("🧹 Iniciando limpieza de datos...")

    try:
        # Ejemplo: Eliminar registros antiguos
        dias_retencion = 90

        # async with get_async_session() as db:
        #     fecha_limite = datetime.now() - timedelta(days=dias_retencion)
        #
        #     # Eliminar registros antiguos
        #     resultado = await repositorio.eliminar_registros_antiguos(
        #         db,
        #         fecha_limite
        #     )
        #
        #     await db.commit()
        #     logger.info(f"Eliminados {resultado.count} registros antiguos")

        # Ejemplo: Limpiar duplicados
        # await limpiar_duplicados(db)

        logger.info("✅ Limpieza completada")

    except Exception as e:
        logger.error(f"Error en limpieza de datos: {e}", exc_info=True)
        raise


async def proceso_generacion_reporte():
    """
    Ejemplo de generación de reporte.
    """
    logger.info("📋 Generando reporte...")

    try:
        # Recopilar datos
        # async with get_async_session() as db:
        #     datos = await repositorio.obtener_datos_reporte(db)

        # Generar reporte (CSV, PDF, Excel, etc.)
        # import pandas as pd
        # df = pd.DataFrame(datos)
        # df.to_csv(f"reporte_{datetime.now().strftime('%Y%m%d')}.csv")

        # Enviar por email
        # await enviar_email_con_reporte(archivo_reporte)

        logger.info("✅ Reporte generado y enviado")

    except Exception as e:
        logger.error(f"Error generando reporte: {e}", exc_info=True)
        raise


async def proceso_batch_paralelo():
    """
    Ejemplo de procesamiento batch en paralelo.
    """
    logger.info("⚡ Iniciando procesamiento paralelo...")

    try:
        # Obtener registros a procesar
        registros = await obtener_registros_pendientes()

        # Procesar en lotes paralelos
        batch_size = 10
        for i in range(0, len(registros), batch_size):
            lote = registros[i:i + batch_size]

            # Procesar lote en paralelo
            tareas = [procesar_registro(reg) for reg in lote]
            resultados = await asyncio.gather(*tareas, return_exceptions=True)

            # Contar éxitos y errores
            exitosos = sum(1 for r in resultados if not isinstance(r, Exception))
            errores = len(resultados) - exitosos

            logger.info(f"Lote {i//batch_size + 1}: {exitosos} ok, {errores} errores")

        logger.info("✅ Procesamiento paralelo completado")

    except Exception as e:
        logger.error(f"Error en procesamiento paralelo: {e}", exc_info=True)
        raise


# TODO: Agregar tus propios procesos aquí
# Ejemplos adicionales:
# - Sincronización SFTP
# - Envío de notificaciones
# - Cálculos estadísticos
# - Detección de anomalías
# - Actualización de caché
