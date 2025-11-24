"""
Script de prueba rápida para ver los procesos en acción.

Ejecuta los 3 procesos en diferentes modos sin necesidad de configuración completa.
Útil para entender cómo funciona la ejecución paralela vs secuencial.

Uso:
    python test_procesos.py
"""

import asyncio
import time
from datetime import datetime

# Logger centralizado
from config.logger import logger

# Importar procesos
from processes.proceso_a import ejecutar_proceso_a
from processes.proceso_b import ejecutar_proceso_b
from processes.proceso_c import ejecutar_proceso_c


async def test_secuencial():
    """Test: Ejecutar procesos en secuencia (uno después del otro)"""
    logger.info("="*70)
    logger.info("TEST 1: EJECUCIÓN SECUENCIAL")
    logger.info("="*70)

    inicio = time.time()

    logger.info("▶️ Ejecutando Proceso A...")
    await ejecutar_proceso_a()

    logger.info("▶️ Ejecutando Proceso B...")
    await ejecutar_proceso_b()

    logger.info("▶️ Ejecutando Proceso C...")
    await ejecutar_proceso_c()

    duracion = time.time() - inicio
    logger.info(f"⏱️ Tiempo total SECUENCIAL: {duracion:.2f} segundos")
    logger.info("")
    return duracion


async def test_paralelo():
    """Test: Ejecutar procesos en paralelo (todos al mismo tiempo)"""
    logger.info("="*70)
    logger.info("TEST 2: EJECUCIÓN PARALELA (asyncio.gather)")
    logger.info("="*70)

    inicio = time.time()

    # Ejecutar en paralelo
    await asyncio.gather(
        ejecutar_proceso_a(),
        ejecutar_proceso_b(),
        ejecutar_proceso_c(),
        return_exceptions=True  # Continuar si uno falla
    )

    duracion = time.time() - inicio
    logger.info(f"⏱️ Tiempo total PARALELO: {duracion:.2f} segundos")
    logger.info("")
    return duracion


async def test_combinado():
    """Test: Ejecutar un proceso crítico primero, luego otros en paralelo"""
    logger.info("="*70)
    logger.info("TEST 3: EJECUCIÓN COMBINADA (secuencial + paralelo)")
    logger.info("="*70)

    inicio = time.time()

    # Primero: Proceso crítico/prioritario (Proceso A)
    logger.info("▶️ Ejecutando Proceso A (crítico/prioritario)...")
    await ejecutar_proceso_a()

    # Luego: Procesos B y C en paralelo
    logger.info("⚡ Ejecutando Procesos B y C en paralelo...")
    await asyncio.gather(
        ejecutar_proceso_b(),
        ejecutar_proceso_c(),
        return_exceptions=True
    )

    duracion = time.time() - inicio
    logger.info(f"⏱️ Tiempo total COMBINADO: {duracion:.2f} segundos")
    logger.info("")
    return duracion


async def comparar_resultados(tiempo_sec, tiempo_par, tiempo_comb):
    """Muestra comparación de tiempos"""
    logger.info("="*70)
    logger.info("RESUMEN DE RESULTADOS")
    logger.info("="*70)

    logger.info(f"1️⃣ Secuencial:  {tiempo_sec:.2f}s")
    logger.info(f"2️⃣ Paralelo:    {tiempo_par:.2f}s  ⚡ {((tiempo_sec/tiempo_par - 1) * 100):.1f}% más rápido")
    logger.info(f"3️⃣ Combinado:   {tiempo_comb:.2f}s  ⚡ {((tiempo_sec/tiempo_comb - 1) * 100):.1f}% más rápido")

    logger.info("")
    logger.info("🎯 CONCLUSIÓN:")
    if tiempo_par < tiempo_sec * 0.4:
        logger.info("   ✅ La ejecución paralela es SIGNIFICATIVAMENTE más rápida")
    elif tiempo_par < tiempo_sec * 0.7:
        logger.info("   ✅ La ejecución paralela es más rápida")
    else:
        logger.info("   ⚠️ El beneficio de paralelización es limitado (procesos no I/O bound)")

    logger.info("")
    logger.info("📝 RECOMENDACIÓN:")
    if tiempo_par <= tiempo_comb:
        logger.info("   👉 Usar PARALELO puro (asyncio.gather con todos los procesos)")
    else:
        logger.info("   👉 Usar COMBINADO (proceso crítico primero, luego paralelo)")


async def main():
    """Función principal que ejecuta todos los tests"""
    logger.info("")
    logger.info("🚀 INICIANDO TESTS DE PROCESOS PARALELOS")
    logger.info(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    # Ejecutar tests
    tiempo_secuencial = await test_secuencial()
    await asyncio.sleep(1)  # Pausa entre tests

    tiempo_paralelo = await test_paralelo()
    await asyncio.sleep(1)  # Pausa entre tests

    tiempo_combinado = await test_combinado()

    # Comparar resultados
    await comparar_resultados(tiempo_secuencial, tiempo_paralelo, tiempo_combinado)

    logger.info("="*70)
    logger.info("✅ TESTS COMPLETADOS")
    logger.info("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Tests interrumpidos por usuario")
    except Exception as e:
        logger.error(f"❌ Error en tests: {e}", exc_info=True)
        exit(1)
