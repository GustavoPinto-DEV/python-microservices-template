# API Template - FastAPI

Plantilla genérica para crear APIs REST con FastAPI, diseñada para proyectos empresariales con arquitectura estandarizada.

## Características

- ✅ FastAPI con documentación automática (Swagger/ReDoc)
- ✅ Autenticación JWT
- ✅ Middleware de compresión de responses (gzip)
- ✅ Rate limiting opcional
- ✅ Manejo centralizado de excepciones
- ✅ Logging estructurado
- ✅ Conexión asíncrona a PostgreSQL (opcional)
- ✅ Arquitectura limpia (Router → Controller → Repository)
- ✅ Docker ready
- ✅ Health check endpoints

## Estructura del Proyecto

```
template_api/
├── main.py              # Punto de entrada
├── requirements.txt     # Dependencias Python
├── .env.example         # Variables de entorno (copiar a .env)
├── Dockerfile          # Contenedor Docker
├── config/
│   └── env.py          # Variables globales de entorno
├── controller/
│   └── v1Controller.py # Lógica de negocio
├── dependencies/
│   ├── auth.py         # Autenticación JWT
│   └── util.py         # Utilidades del proyecto
├── exception/
│   └── exception_handlers.py  # Manejadores de errores
├── middleware/
│   ├── CompressionMiddleware.py   # Compresión gzip de responses
│   └── RateLimiterMiddleware.py   # Rate limiting
├── router/
│   └── v1Router.py     # Definición de rutas
└── schema/
    └── schemas.py      # Schemas Pydantic
```

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

### 4. Ejecutar en modo desarrollo

```bash
uvicorn main:app --port 8000 --reload
```

## Uso

### Documentación Interactiva

Una vez iniciado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check

```bash
curl http://localhost:8000/health
```

## Agregar Nuevo Endpoint

### 1. Definir ruta en `router/v1Router.py`

```python
@router.post("/users", response_model=UserResponse)
async def create_user(
    request: UserRequest,
    controller: v1Controller = Depends(get_controller)
):
    return await controller.create_user(request)
```

### 2. Implementar handler en `controller/v1Controller.py`

```python
async def create_user(self, request: UserRequest) -> Result:
    # Lógica de negocio
    result = await self.repository.create_user(request)
    return result
```

### 3. Definir schemas en `schema/schemas.py`

```python
class UserRequest(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
```

## Middleware

### Compression Middleware (Habilitado por defecto)

Comprime automáticamente responses grandes usando gzip:

```python
app.add_middleware(
    CompressionMiddleware,
    min_size=500,           # Tamaño mínimo en bytes para comprimir
    compression_level=6,    # Nivel de compresión (1-9)
    exclude_paths=["/health", "/docs"]
)
```

### Rate Limiter (Opcional)

Protege contra abuso y ataques DDoS:

```python
# Descomentar en main.py para habilitar
app.add_middleware(
    RateLimiterMiddleware,
    max_requests=100,
    window_seconds=60
)
```

## Docker

### Build

```bash
docker build -t api-template .
```

### Run

```bash
docker run -p 8000:8000 --env-file .env api-template
```

## Integración con Repositorio Compartido

Este template está diseñado para trabajar con una librería compartida (capa de datos).

### Instalar librería compartida

```bash
# Asumiendo que tienes un proyecto 'repositorio' en el directorio padre
pip install -e ../repositorio
```

### Usar en el código

```python
# Descomentar en main.py y controllers
from your_repo_lib.core.database import get_async_session
from your_repo_lib.core.logger import setup_logger
from your_repo_lib.service.repository import v1Repository
```

## Testing

```bash
pytest tests/ -v
```

## Producción

### Variables de entorno importantes

- `ENVIRONMENT=production`
- Configurar `DB_*` con credenciales de producción
- Cambiar `SECRET_KEY` por una clave segura
- Ajustar `RATE_LIMIT_*` según necesidad
- Configurar `ALLOWED_ORIGINS` en CORS

### Ejecutar con Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Recomendaciones de Producción

1. Usar un reverse proxy (Nginx, Traefik)
2. Habilitar HTTPS
3. Configurar CORS con orígenes específicos
4. Habilitar rate limiting
5. Configurar logging a archivos o servicio externo
6. Implementar monitoreo (Prometheus, DataDog)
7. Usar variables de entorno para secretos
8. Configurar health checks en orquestador (Kubernetes, Docker Swarm)

## Seguridad

- JWT para autenticación
- CORS configurable
- Rate limiting contra abuso
- Validación de datos con Pydantic
- Headers de seguridad (opcional con SecurityHeadersMiddleware)

## Licencia

Plantilla de código libre para uso en proyectos Python
