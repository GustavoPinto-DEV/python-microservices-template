# Repositorio Template - Librería Compartida

Plantilla genérica para crear una librería compartida que centraliza acceso a datos, configuración y utilidades comunes.

## Características

- ✅ Conexión asíncrona a PostgreSQL
- ✅ Pool de conexiones optimizado
- ✅ Logger centralizado con rotación
- ✅ Modelos auto-generados desde DB
- ✅ Schemas Pydantic auto-generados
- ✅ CRUD helpers
- ✅ Settings centralizados
- ✅ Utilidades compartidas

## Estructura

```
your_data_layer/
├── config/         # Configuración (settings, cache)
├── core/           # Funcionalidad core (db, logger, security)
├── utils/          # Utilidades compartidas
├── model/          # Modelos SQLAlchemy (auto-generados)
├── schema/         # Schemas Pydantic (auto-generados)
└── service/        # Repository (capa de acceso a datos)
```

## Instalación

### Entorno principal (desarrollo)

```bash
cd your_data_layer
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .  # Instalar en modo editable
```

### Entorno de generación de modelos

```bash
py -3.12 -m venv env
env\Scripts\activate
pip install -r model_gen.txt
```

## Uso en Otros Proyectos

En `requirements.txt` del proyecto:
```
-e ../data_layer
```

En código:
```python
from your_data_layer.core.database import get_async_session
from your_data_layer.core.logger import setup_logger
from your_data_layer.service.repository import v1Repository
from your_data_layer.utils import retry_with_backoff
```

## Regenerar Modelos

```bash
env\Scripts\activate
sqlacodegen postgresql+psycopg2://user:pass@host:port/db > your_data_layer/model/models.py

# Limpiar null bytes (Windows)
(Get-Content your_data_layer/model/models.py -Raw) -replace [char]0, '' | Set-Content your_data_layer/model/models.py

# Generar schemas
python schema_generator.py
```

## Licencia

Plantilla de código libre para uso en proyectos Python
