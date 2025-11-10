# Consola Template - Asyncio Batch Service

Plantilla genérica para servicios de consola/batch basados en asyncio para procesamiento en segundo plano.

## Características

- ✅ Ejecución asíncrona con asyncio
- ✅ Procesamiento batch continuo o programado
- ✅ Manejo graceful de señales (SIGINT, SIGTERM)
- ✅ Logging estructurado con rotación
- ✅ Conexión asíncrona a PostgreSQL
- ✅ Reintentos automáticos con backoff exponencial
- ✅ Integración con servicios externos (APIs, SFTP)
- ✅ Docker ready

## Estructura del Proyecto

```
template_consola/
├── main.py              # Punto de entrada
├── requirements.txt     # Dependencias Python
├── .env.example         # Variables de entorno (copiar a .env)
├── Dockerfile          # Contenedor Docker
├── config/
│   └── env.py          # Variables globales de entorno
├── dependencies/
│   └── util.py         # Utilidades del proyecto
├── exception/
│   └── exception_handlers.py  # Manejadores de errores
├── processes/
│   └── ejemplo_proceso.py  # Procesos batch específicos
├── service/
│   └── servicio.py     # Orquestación del servicio
└── schema/
    └── schemas.py      # Schemas Pydantic
```

## Casos de Uso

Esta plantilla es ideal para:

- **Procesamiento batch**: Actualización masiva de datos, cálculos periódicos
- **Sincronización**: Integración con sistemas externos (APIs, SFTP, FTP)
- **Monitoreo**: Detección de anomalías, alertas automáticas
- **Limpieza de datos**: Purga de registros antiguos, mantenimiento de BD
- **Generación de reportes**: Reportes programados, envío de emails
- **Workers**: Procesamiento de colas de tareas

## Instalación

### 1. Crear entorno virtual

```bash
py -3.12 -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
```

### 4. Ejecutar

```bash
python main.py
```

## Configuración

### Intervalo de Ejecución

Configurar en `.env`:

```bash
MINUTOS_CONSOLA=60  # Ejecutar cada 60 minutos
```

### Modo de Ejecución

```bash
# Ejecución continua (loop infinito)
ENABLE_CONTINUOUS_MODE=true

# Ejecución única (termina después de 1 ciclo)
ENABLE_CONTINUOUS_MODE=false
```

## Agregar Nuevo Proceso

### 1. Crear archivo en `processes/`

```python
# processes/mi_proceso.py

import logging

logger = logging.getLogger(__name__)

async def ejecutar_mi_proceso():
    """
    Ejecuta lógica del proceso batch.
    """
    logger.info("Iniciando mi proceso...")

    # Tu lógica aquí
    # - Consultar base de datos
    # - Procesar registros
    # - Llamar APIs externas
    # - Etc.

    logger.info("Proceso completado exitosamente")
```

### 2. Registrar en `service/servicio.py`

```python
from processes.mi_proceso import ejecutar_mi_proceso

async def ejecutar_ciclo(self):
    # Agregar tu proceso al ciclo
    await ejecutar_mi_proceso()
```

## Manejo de Errores

El servicio incluye reintentos automáticos:

```python
from your_data_layer.utils import retry_with_backoff

await retry_with_backoff(
    my_function,
    name="My Process",
    max_attempts=3,
    initial_delay=5
)
```

## Detener el Servicio

### Modo interactivo

```bash
Ctrl+C
```

### Docker

```bash
docker stop <container-id>
```

El servicio siempre realiza un shutdown graceful, completando la tarea actual antes de detenerse.

## Docker

### Build

```bash
docker build -t consola-template .
```

### Run

```bash
docker run --env-file .env consola-template
```

### Con Docker Compose

```yaml
services:
  consola:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    env_file:
      - .env
    volumes:
      - ${LOG_HOST_PATH}:${LOG_DIR_EXTERNAL}
```

## Integración con Repositorio Compartido

Este template está diseñado para trabajar con una librería compartida (`repositorio_lib`).

### Instalar librería compartida

```bash
# Asumiendo que tienes un proyecto 'data_layer' en el directorio padre
pip install -e ../data_layer
```

### Usar en el código

```python
from your_data_layer.core.database import get_async_session
from your_data_layer.core.logger import setup_logger
from your_data_layer.service.repository import v1Repository
from your_data_layer.utils import retry_with_backoff
```

## Ejemplos de Procesos

### Actualización de datos desde API externa

```python
async def actualizar_datos_externos():
    async with get_async_session() as db:
        # Obtener datos de API
        datos = await llamar_api_externa()

        # Actualizar en base de datos
        for item in datos:
            await repositorio.actualizar_registro(db, item)

        await db.commit()
```

### Procesamiento batch con SFTP

```python
async def procesar_archivos_sftp():
    # Conectar a SFTP
    async with conectar_sftp() as sftp:
        # Descargar archivos
        archivos = await sftp.listar_archivos()

        for archivo in archivos:
            # Procesar archivo
            contenido = await sftp.descargar(archivo)
            await procesar_contenido(contenido)

            # Mover a carpeta procesados
            await sftp.mover(archivo, "/procesados/")
```

## Monitoreo

### Logs

Los logs se guardan en:
- Desarrollo: `./logs/`
- Producción: `/var/log/app/logs/`

### Health Check

Para verificar que el servicio está corriendo:

```bash
# Ver logs en Docker
docker logs <container-id>

# Ver procesos
ps aux | grep python
```

## Licencia

Plantilla de código libre para uso en proyectos Python
