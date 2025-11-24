# Guía de Despliegue con Artefactos Compilados

## 📋 Índice

1. [Introducción](#introducción)
2. [Preparación de Artefactos](#preparación-de-artefactos)
3. [Modalidad A - Servicio Windows](#modalidad-a---servicio-windows)
4. [Modalidad B - Docker con Artefactos](#modalidad-b---docker-con-artefactos)
5. [Modalidad C - Systemd en Linux](#modalidad-c---systemd-en-linux)
6. [Comparativa de Modalidades](#comparativa-de-modalidades)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

Este documento describe cómo desplegar el proyecto Python usando **artefactos compilados** en lugar de código fuente sin compilar, siguiendo mejores prácticas para entornos de producción.

### ¿Qué son "Artefactos Compilados"?

En el contexto de Python, los artefactos compilados son:

1. **Bytecode (.pyc)**: Código Python compilado a bytecode
2. **Wheels (.whl)**: Paquetes binarios precompilados
3. **Ejecutables standalone**: Binarios independientes (PyInstaller, Nuitka)
4. **Virtualenv empaquetado**: Entorno completo con dependencias instaladas

### ¿Por qué Artefactos Compilados?

✅ **Seguridad**: Ofusca el código fuente
✅ **Performance**: Bytecode pre-compilado se ejecuta más rápido
✅ **Portabilidad**: Binarios autocontenidos
✅ **Versionamiento**: Artefactos versionados y testeados
✅ **Rollback fácil**: Versiones anteriores disponibles
✅ **Protección IP**: El código fuente no es visible

---

## 📦 Preparación de Artefactos

Antes de desplegar en cualquier modalidad, necesitamos compilar el proyecto.

### Método 1: Wheel Distribution (Recomendado para Producción)

Este método crea un paquete .whl que puede ser instalado en cualquier entorno.

#### Paso 1: Configurar setup.py

Crear `setup.py` en cada servicio:

```python
# setup.py para API/Web/Consola
from setuptools import setup, find_packages

setup(
    name="myproject-api",  # Cambiar según servicio
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Leer de requirements.txt
        line.strip()
        for line in open('requirements.txt')
        if line.strip() and not line.startswith('#')
    ],
    python_requires='>=3.12',
    entry_points={
        'console_scripts': [
            'myproject-api=main:main',  # Para API/Web
            # 'myproject-worker=main:main',  # Para Consola
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.12',
    ],
)
```

#### Paso 2: Compilar Wheels

```bash
# Para cada servicio (api, web, worker)
cd api/

# Instalar herramientas de build
pip install build wheel

# Compilar wheel
python -m build --wheel

# Resultado: dist/myproject_api-1.0.0-py3-none-any.whl
```

#### Paso 3: Compilar Bytecode (Adicional)

```bash
# Compilar todo el código a .pyc
python -m compileall -b .

# Eliminar archivos .py (opcional - solo en producción extrema)
# find . -name "*.py" -not -path "./venv/*" -delete
```

### Método 2: PyInstaller (Ejecutable Standalone)

Crear un ejecutable autocontenido (ideal para Windows Service).

#### Configuración

Crear `build.spec` para cada servicio:

```python
# api.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Incluir archivos estáticos si los hay
        # ('static', 'static'),
        # ('templates', 'templates'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'asyncpg',
        'pydantic',
        # Agregar todos los imports dinámicos
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='myproject-api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # False para GUI
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

#### Build con PyInstaller

```bash
# Instalar PyInstaller
pip install pyinstaller

# Build
pyinstaller api.spec

# Resultado: dist/myproject-api.exe (Windows) o myproject-api (Linux)
```

### Método 3: Nuitka (Compilación a C)

Para máximo rendimiento y protección.

```bash
# Instalar Nuitka
pip install nuitka

# Compilar (más lento pero mejor performance)
python -m nuitka --standalone --onefile \
    --enable-plugin=anti-bloat \
    --output-dir=dist \
    main.py

# Resultado: dist/main.exe (altamente optimizado)
```

---

## 🪟 Modalidad A - Servicio Windows

Desplegar como servicio Windows usando NSSM (Non-Sucking Service Manager).

### Prerrequisitos

- Windows Server 2016+ o Windows 10+
- Python 3.12 instalado (o usar PyInstaller para no requerirlo)
- NSSM descargado: https://nssm.cc/download

### Opción A1: Con Wheels (Recomendado)

#### Paso 1: Preparar Directorio de Producción

```powershell
# Crear estructura
New-Item -ItemType Directory -Path "C:\MyProject\Production" -Force
New-Item -ItemType Directory -Path "C:\MyProject\Production\api" -Force
New-Item -ItemType Directory -Path "C:\MyProject\Production\web" -Force
New-Item -ItemType Directory -Path "C:\MyProject\Production\worker" -Force
New-Item -ItemType Directory -Path "C:\MyProject\Logs" -Force
New-Item -ItemType Directory -Path "C:\MyProject\Backups" -Force
```

#### Paso 2: Instalar Artefactos

```powershell
# Para cada servicio (ejemplo: API)
cd C:\MyProject\Production\api

# Crear virtualenv
python -m venv venv

# Activar
.\venv\Scripts\Activate.ps1

# Instalar wheel compilado
pip install C:\path\to\build\dist\myproject_api-1.0.0-py3-none-any.whl

# Instalar repositorio compartido
pip install C:\path\to\build\dist\myproject_repositorio-1.0.0-py3-none-any.whl

# Copiar archivo de configuración
Copy-Item "C:\path\to\data_layer\repositorio_lib\config\.env" -Destination ".\config\.env"

# Verificar instalación
python -c "import main; print('OK')"
```

#### Paso 3: Configurar NSSM

```powershell
# Descargar NSSM
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "nssm.zip"
Expand-Archive -Path "nssm.zip" -DestinationPath "C:\MyProject\nssm"

# Usar nssm según arquitectura
$nssm = "C:\MyProject\nssm\nssm-2.24\win64\nssm.exe"

# Instalar servicio API
& $nssm install MyProject-API "C:\MyProject\Production\api\venv\Scripts\python.exe" `
    "-m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"

# Configurar directorio de trabajo
& $nssm set MyProject-API AppDirectory "C:\MyProject\Production\api"

# Configurar usuario (opcional - usar cuenta de servicio)
# & $nssm set MyProject-API ObjectName ".\ServiceAccount" "password"

# Configurar variables de entorno
& $nssm set MyProject-API AppEnvironmentExtra `
    "ENVIRONMENT=production" `
    "LOG_DIR_PRD=C:\MyProject\Logs" `
    "PYTHONUNBUFFERED=1"

# Configurar logging
& $nssm set MyProject-API AppStdout "C:\MyProject\Logs\api-stdout.log"
& $nssm set MyProject-API AppStderr "C:\MyProject\Logs\api-stderr.log"

# Configurar restart automático
& $nssm set MyProject-API AppExit Default Restart
& $nssm set MyProject-API AppRestartDelay 5000

# Configurar startup
& $nssm set MyProject-API Start SERVICE_AUTO_START

# Iniciar servicio
Start-Service MyProject-API

# Verificar estado
Get-Service MyProject-API
```

#### Paso 4: Configurar Servicios Adicionales

```powershell
# Servicio Web
& $nssm install MyProject-Web "C:\MyProject\Production\web\venv\Scripts\python.exe" `
    "-m uvicorn main:app --host 0.0.0.0 --port 8001 --workers 2"

& $nssm set MyProject-Web AppDirectory "C:\MyProject\Production\web"
& $nssm set MyProject-Web AppStdout "C:\MyProject\Logs\web-stdout.log"
& $nssm set MyProject-Web AppStderr "C:\MyProject\Logs\web-stderr.log"
& $nssm set MyProject-Web Start SERVICE_AUTO_START

# Servicio Worker
& $nssm install MyProject-Worker "C:\MyProject\Production\worker\venv\Scripts\python.exe" `
    "main.py"

& $nssm set MyProject-Worker AppDirectory "C:\MyProject\Production\worker"
& $nssm set MyProject-Worker AppStdout "C:\MyProject\Logs\worker-stdout.log"
& $nssm set MyProject-Worker AppStderr "C:\MyProject\Logs\worker-stderr.log"
& $nssm set MyProject-Worker Start SERVICE_AUTO_START

# Iniciar todos
Start-Service MyProject-Web
Start-Service MyProject-Worker
```

### Opción A2: Con PyInstaller (Ejecutable Standalone)

#### Paso 1: Build Ejecutable

```powershell
# Build con PyInstaller (ver sección anterior)
cd api
pyinstaller api.spec

# Resultado: dist/myproject-api.exe
```

#### Paso 2: Copiar a Producción

```powershell
# Copiar ejecutable
Copy-Item "dist\myproject-api.exe" -Destination "C:\MyProject\Production\api\"

# Copiar dependencias (si las hay)
Copy-Item "config\.env" -Destination "C:\MyProject\Production\api\config\"
```

#### Paso 3: Configurar NSSM con Ejecutable

```powershell
# Instalar servicio con ejecutable
& $nssm install MyProject-API "C:\MyProject\Production\api\myproject-api.exe"

& $nssm set MyProject-API AppDirectory "C:\MyProject\Production\api"
& $nssm set MyProject-API AppStdout "C:\MyProject\Logs\api-stdout.log"
& $nssm set MyProject-API AppStderr "C:\MyProject\Logs\api-stderr.log"
& $nssm set MyProject-API Start SERVICE_AUTO_START

Start-Service MyProject-API
```

### Actualizar Servicios Windows

#### Script de Actualización

Crear `update-service.ps1`:

```powershell
# update-service.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$ServiceName,

    [Parameter(Mandatory=$true)]
    [string]$WheelPath
)

Write-Host "Actualizando servicio: $ServiceName" -ForegroundColor Blue

# Detener servicio
Write-Host "Deteniendo servicio..."
Stop-Service $ServiceName -Force
Start-Sleep -Seconds 5

# Determinar directorio del servicio
$serviceDir = switch ($ServiceName) {
    "MyProject-API" { "C:\MyProject\Production\api" }
    "MyProject-Web" { "C:\MyProject\Production\web" }
    "MyProject-Worker" { "C:\MyProject\Production\worker" }
}

# Activar virtualenv
& "$serviceDir\venv\Scripts\Activate.ps1"

# Backup de versión actual
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\MyProject\Backups\$ServiceName-$timestamp"
New-Item -ItemType Directory -Path $backupDir -Force
Copy-Item "$serviceDir\venv\Lib\site-packages\*" -Destination $backupDir -Recurse

Write-Host "Backup creado en: $backupDir" -ForegroundColor Green

# Instalar nueva versión
Write-Host "Instalando nueva versión..."
pip install --upgrade --force-reinstall $WheelPath

# Verificar instalación
$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host "Instalación exitosa" -ForegroundColor Green

    # Iniciar servicio
    Write-Host "Iniciando servicio..."
    Start-Service $ServiceName

    # Verificar estado
    Start-Sleep -Seconds 10
    $status = Get-Service $ServiceName

    if ($status.Status -eq "Running") {
        Write-Host "Servicio actualizado correctamente" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Servicio no inició correctamente" -ForegroundColor Red
        Write-Host "Realizando rollback..." -ForegroundColor Yellow

        # Rollback
        Stop-Service $ServiceName -Force
        Remove-Item "$serviceDir\venv\Lib\site-packages\*" -Recurse -Force
        Copy-Item "$backupDir\*" -Destination "$serviceDir\venv\Lib\site-packages\" -Recurse
        Start-Service $ServiceName

        Write-Host "Rollback completado" -ForegroundColor Yellow
    }
} else {
    Write-Host "ERROR: Instalación falló" -ForegroundColor Red
    Start-Service $ServiceName
}
```

#### Uso del Script de Actualización

```powershell
# Actualizar API
.\update-service.ps1 -ServiceName "MyProject-API" `
    -WheelPath "C:\path\to\myproject_api-1.1.0-py3-none-any.whl"

# Actualizar Web
.\update-service.ps1 -ServiceName "MyProject-Web" `
    -WheelPath "C:\path\to\myproject_web-1.1.0-py3-none-any.whl"

# Actualizar Worker
.\update-service.ps1 -ServiceName "MyProject-Worker" `
    -WheelPath "C:\path\to\myproject_worker-1.1.0-py3-none-any.whl"
```

### Comandos de Gestión Windows

```powershell
# Ver servicios
Get-Service MyProject-*

# Iniciar/Detener
Start-Service MyProject-API
Stop-Service MyProject-API
Restart-Service MyProject-API

# Ver logs
Get-Content "C:\MyProject\Logs\api-stdout.log" -Tail 50 -Wait

# Ver configuración del servicio
& $nssm dump MyProject-API

# Eliminar servicio (si es necesario)
& $nssm remove MyProject-API confirm
```

### Task Scheduler para Monitoreo

Crear tarea programada para verificar servicios:

```powershell
# monitor-services.ps1
$services = @("MyProject-API", "MyProject-Web", "MyProject-Worker")

foreach ($service in $services) {
    $status = Get-Service $service -ErrorAction SilentlyContinue

    if ($status.Status -ne "Running") {
        Write-Host "WARNING: $service no está corriendo. Reiniciando..." -ForegroundColor Yellow
        Start-Service $service

        # Enviar alerta (email, webhook, etc.)
        # Send-MailMessage -To "admin@example.com" -Subject "Servicio $service reiniciado" ...
    }
}
```

Programar tarea:

```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\MyProject\Scripts\monitor-services.ps1"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::MaxValue)

Register-ScheduledTask -TaskName "MyProject-Monitor" `
    -Action $action -Trigger $trigger -RunLevel Highest
```

---

## 🐳 Modalidad B - Docker con Artefactos

Desplegar usando Docker con imágenes que contienen artefactos compilados.

### Estrategia: Multi-stage Build con Wheels

Esta estrategia compila wheels en el builder y los instala en runtime.

#### Paso 1: Dockerfile Optimizado

Crear `docker/api/Dockerfile.production`:

```dockerfile
# ============================================================================
# STAGE 1: Builder - Compilación de artefactos
# ============================================================================
FROM python:3.12-slim as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instalar herramientas de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copiar código fuente
COPY data_layer/ ./data_layer/
COPY api/ ./api/

# Crear setup.py para repositorio_lib si no existe
RUN cd data_layer && \
    if [ ! -f setup.py ]; then \
        cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="myproject-repositorio",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open('requirements.txt')
        if line.strip() and not line.startswith('#')
    ],
)
EOF
    fi

# Crear setup.py para API si no existe
RUN cd api && \
    if [ ! -f setup.py ]; then \
        cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="myproject-api",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open('requirements.txt')
        if line.strip() and not line.startswith('#')
    ],
    entry_points={
        'console_scripts': [
            'myproject-api=main:main',
        ],
    },
)
EOF
    fi

# Instalar herramientas de build
RUN pip install --upgrade pip setuptools wheel build

# Compilar wheels
RUN cd data_layer && python -m build --wheel
RUN cd api && python -m build --wheel

# Compilar todo el código Python a bytecode
RUN python -m compileall -b data_layer/
RUN python -m compileall -b api/

# ============================================================================
# STAGE 2: Runtime - Imagen final con solo artefactos
# ============================================================================
FROM python:3.12-slim as runtime

LABEL maintainer="devops@myproject.com"
LABEL description="Production API with compiled artifacts"
LABEL version="1.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

# Instalar solo dependencias de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1001 -m -s /sbin/nologin appuser

# Crear directorios
RUN mkdir -p /app /var/log/app/logs /artifacts && \
    chown -R appuser:appuser /app /var/log/app /artifacts

WORKDIR /artifacts

# Copiar SOLO los wheels compilados (NO código fuente)
COPY --from=builder --chown=appuser:appuser \
    /build/data_layer/dist/*.whl ./
COPY --from=builder --chown=appuser:appuser \
    /build/api/dist/*.whl ./

# Crear virtualenv e instalar wheels
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install *.whl && \
    rm -rf /artifacts

# Cambiar a usuario no-root
USER appuser

WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--loop", "uvloop"]
```

#### Paso 2: docker-compose con Build de Artefactos

Modificar `docker-compose.production.yml` para compilar:

```yaml
version: '3.9'

services:
  api:
    build:
      context: .
      dockerfile: docker/api/Dockerfile.production
      args:
        VERSION: "${VERSION:-1.0.0}"
        BUILD_DATE: "${BUILD_DATE}"

    image: myproject/api:${VERSION:-latest}

    container_name: myproject_api
    restart: unless-stopped

    environment:
      ENVIRONMENT: production
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      SECRET_KEY: ${SECRET_KEY}

    volumes:
      - app_logs:/var/log/app/logs:rw

    networks:
      - frontend
      - backend

    depends_on:
      postgres:
        condition: service_healthy

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G

    expose:
      - "8000"
```

#### Paso 3: Build y Push de Imágenes

Crear script `build-images.sh`:

```bash
#!/bin/bash
# build-images.sh

set -e

VERSION=${1:-latest}
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

echo "Building images version: $VERSION"

# Build todas las imágenes
docker-compose -f docker-compose.production.yml build \
    --build-arg VERSION=$VERSION \
    --build-arg BUILD_DATE=$BUILD_DATE

# Tag imágenes
docker tag myproject/api:latest myproject/api:$VERSION
docker tag myproject/web:latest myproject/web:$VERSION
docker tag myproject/worker:latest myproject/worker:$VERSION

# Push a registry (opcional)
# docker push myproject/api:$VERSION
# docker push myproject/web:$VERSION
# docker push myproject/worker:$VERSION

echo "Build completado: version $VERSION"
```

Uso:

```bash
chmod +x build-images.sh
./build-images.sh 1.0.0
```

#### Paso 4: Despliegue

```bash
# Pull de imágenes (si están en registry)
docker-compose -f docker-compose.production.yml pull

# Iniciar servicios
docker-compose -f docker-compose.production.yml up -d

# Verificar
docker-compose -f docker-compose.production.yml ps
docker-compose -f docker-compose.production.yml logs -f api
```

#### Paso 5: Actualización Sin Downtime

Crear script `update-services.sh`:

```bash
#!/bin/bash
# update-services.sh

set -e

SERVICE=${1:-all}
VERSION=${2:-latest}

echo "Actualizando servicio(s): $SERVICE a versión: $VERSION"

# Función para actualizar un servicio
update_service() {
    local service=$1
    local version=$2

    echo "Actualizando $service..."

    # Pull nueva imagen
    docker pull myproject/$service:$version

    # Recrear contenedor sin downtime
    docker-compose -f docker-compose.production.yml up -d --no-deps --build $service

    # Esperar health check
    echo "Esperando health check de $service..."
    sleep 10

    # Verificar
    if docker-compose -f docker-compose.production.yml ps $service | grep -q "Up"; then
        echo "✓ $service actualizado exitosamente"

        # Limpiar imágenes antiguas
        docker image prune -f
    else
        echo "✗ ERROR: $service no inició correctamente"

        # Rollback
        echo "Realizando rollback..."
        docker-compose -f docker-compose.production.yml up -d --no-deps $service
        exit 1
    fi
}

# Actualizar servicios
if [ "$SERVICE" = "all" ]; then
    for svc in api web worker; do
        update_service $svc $VERSION
    done
else
    update_service $SERVICE $VERSION
fi

echo "Actualización completada"
```

Uso:

```bash
# Actualizar todos los servicios
./update-services.sh all 1.1.0

# Actualizar solo API
./update-services.sh api 1.1.0
```

### Verificar Artefactos Compilados en Docker

```bash
# Entrar al contenedor
docker exec -it myproject_api /bin/bash

# Verificar que NO hay archivos .py (solo .pyc)
find /opt/venv/lib -name "*.py" -type f | head -10

# Verificar wheels instalados
pip list

# Verificar bytecode
find /opt/venv/lib -name "*.pyc" -type f | head -10

# Salir
exit
```

---

## 🐧 Modalidad C - Systemd en Linux

Desplegar como servicios systemd en Ubuntu/Debian/RHEL con artefactos compilados.

### Prerrequisitos

- Ubuntu 20.04+ / Debian 11+ / RHEL 8+
- Python 3.12 instalado
- Usuario con sudo

### Paso 1: Preparar Estructura

```bash
# Crear directorios
sudo mkdir -p /opt/myproject/{production,logs,backups}
sudo mkdir -p /opt/myproject/production/{api,web,worker}

# Crear usuario de servicio
sudo useradd -r -s /bin/false -d /opt/myproject myproject

# Ajustar permisos
sudo chown -R myproject:myproject /opt/myproject
```

### Paso 2: Instalar Artefactos

Para cada servicio:

```bash
# Ejemplo: API
cd /opt/myproject/production/api

# Crear virtualenv
sudo -u myproject python3.12 -m venv venv

# Activar virtualenv
sudo -u myproject bash -c "source venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install /path/to/myproject_repositorio-1.0.0-py3-none-any.whl && \
    pip install /path/to/myproject_api-1.0.0-py3-none-any.whl"

# Copiar configuración
sudo cp /path/to/data_layer/repositorio_lib/config/.env \
    /opt/myproject/production/api/config/.env

# Ajustar permisos
sudo chown -R myproject:myproject /opt/myproject/production/api
```

### Paso 3: Crear Archivos Systemd

#### API Service

Crear `/etc/systemd/system/myproject-api.service`:

```ini
[Unit]
Description=MyProject API Service
Documentation=https://github.com/myorg/myproject
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=notify
User=myproject
Group=myproject
WorkingDirectory=/opt/myproject/production/api

# Variables de entorno
Environment="ENVIRONMENT=production"
Environment="LOG_DIR_PRD=/opt/myproject/logs"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/myproject/production/api/config/.env

# Comando de inicio
ExecStart=/opt/myproject/production/api/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --loop uvloop \
    --log-level info

# Restart automático
Restart=always
RestartSec=10s
StartLimitInterval=200s
StartLimitBurst=5

# Timeouts
TimeoutStartSec=30s
TimeoutStopSec=30s

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/myproject/logs
ReadOnlyPaths=/opt/myproject/production/api

# Resource limits
LimitNOFILE=65536
CPUQuota=200%
MemoryLimit=1G

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myproject-api

[Install]
WantedBy=multi-user.target
```

#### Web Service

Crear `/etc/systemd/system/myproject-web.service`:

```ini
[Unit]
Description=MyProject Web Service
After=network.target postgresql.service redis.service myproject-api.service
Wants=postgresql.service redis.service

[Service]
Type=notify
User=myproject
Group=myproject
WorkingDirectory=/opt/myproject/production/web

Environment="ENVIRONMENT=production"
Environment="LOG_DIR_PRD=/opt/myproject/logs"
EnvironmentFile=/opt/myproject/production/web/config/.env

ExecStart=/opt/myproject/production/web/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 2 \
    --loop uvloop

Restart=always
RestartSec=10s
TimeoutStartSec=30s
TimeoutStopSec=30s

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/myproject/logs

CPUQuota=100%
MemoryLimit=512M

StandardOutput=journal
StandardError=journal
SyslogIdentifier=myproject-web

[Install]
WantedBy=multi-user.target
```

#### Worker Service

Crear `/etc/systemd/system/myproject-worker.service`:

```ini
[Unit]
Description=MyProject Worker Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=myproject
Group=myproject
WorkingDirectory=/opt/myproject/production/worker

Environment="ENVIRONMENT=production"
Environment="LOG_DIR_PRD=/opt/myproject/logs"
EnvironmentFile=/opt/myproject/production/worker/config/.env

ExecStart=/opt/myproject/production/worker/venv/bin/python main.py

Restart=always
RestartSec=10s
TimeoutStartSec=30s
TimeoutStopSec=30s

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/myproject/logs

CPUQuota=100%
MemoryLimit=512M

StandardOutput=journal
StandardError=journal
SyslogIdentifier=myproject-worker

[Install]
WantedBy=multi-user.target
```

### Paso 4: Habilitar e Iniciar Servicios

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable myproject-api
sudo systemctl enable myproject-web
sudo systemctl enable myproject-worker

# Iniciar servicios
sudo systemctl start myproject-api
sudo systemctl start myproject-web
sudo systemctl start myproject-worker

# Verificar estado
sudo systemctl status myproject-api
sudo systemctl status myproject-web
sudo systemctl status myproject-worker
```

### Paso 5: Actualización

Crear script `/opt/myproject/scripts/update-service.sh`:

```bash
#!/bin/bash
# update-service.sh

set -e

SERVICE_NAME=$1
WHEEL_PATH=$2

if [ -z "$SERVICE_NAME" ] || [ -z "$WHEEL_PATH" ]; then
    echo "Uso: $0 <service-name> <wheel-path>"
    echo "Ejemplo: $0 api /path/to/myproject_api-1.1.0-py3-none-any.whl"
    exit 1
fi

# Determinar directorio del servicio
case $SERVICE_NAME in
    api)
        SERVICE_DIR="/opt/myproject/production/api"
        SYSTEMD_SERVICE="myproject-api"
        ;;
    web)
        SERVICE_DIR="/opt/myproject/production/web"
        SYSTEMD_SERVICE="myproject-web"
        ;;
    worker)
        SERVICE_DIR="/opt/myproject/production/worker"
        SYSTEMD_SERVICE="myproject-worker"
        ;;
    *)
        echo "Servicio desconocido: $SERVICE_NAME"
        exit 1
        ;;
esac

echo "Actualizando servicio: $SYSTEMD_SERVICE"

# Detener servicio
echo "Deteniendo servicio..."
sudo systemctl stop $SYSTEMD_SERVICE

# Backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/myproject/backups/${SERVICE_NAME}-${TIMESTAMP}"
echo "Creando backup en: $BACKUP_DIR"
sudo mkdir -p $BACKUP_DIR
sudo cp -r $SERVICE_DIR/venv $BACKUP_DIR/

# Activar virtualenv e instalar nueva versión
echo "Instalando nueva versión..."
sudo -u myproject bash -c "
    source $SERVICE_DIR/venv/bin/activate && \
    pip install --upgrade --force-reinstall $WHEEL_PATH
"

# Verificar instalación
if [ $? -eq 0 ]; then
    echo "Instalación exitosa"

    # Iniciar servicio
    echo "Iniciando servicio..."
    sudo systemctl start $SYSTEMD_SERVICE

    # Esperar y verificar
    sleep 5

    if sudo systemctl is-active --quiet $SYSTEMD_SERVICE; then
        echo "✓ Servicio actualizado correctamente"
        sudo systemctl status $SYSTEMD_SERVICE

        # Limpiar backups antiguos (mantener últimos 5)
        cd /opt/myproject/backups
        ls -t | grep "^${SERVICE_NAME}-" | tail -n +6 | xargs -r sudo rm -rf

        echo "Actualización completada exitosamente"
    else
        echo "✗ ERROR: Servicio no inició correctamente"
        echo "Realizando rollback..."

        # Rollback
        sudo systemctl stop $SYSTEMD_SERVICE
        sudo rm -rf $SERVICE_DIR/venv
        sudo cp -r $BACKUP_DIR/venv $SERVICE_DIR/
        sudo chown -R myproject:myproject $SERVICE_DIR/venv
        sudo systemctl start $SYSTEMD_SERVICE

        echo "Rollback completado"
        exit 1
    fi
else
    echo "✗ ERROR: Instalación falló"
    sudo systemctl start $SYSTEMD_SERVICE
    exit 1
fi
```

Dar permisos:

```bash
sudo chmod +x /opt/myproject/scripts/update-service.sh
```

Uso:

```bash
# Actualizar API
sudo /opt/myproject/scripts/update-service.sh api \
    /path/to/myproject_api-1.1.0-py3-none-any.whl

# Actualizar Web
sudo /opt/myproject/scripts/update-service.sh web \
    /path/to/myproject_web-1.1.0-py3-none-any.whl

# Actualizar Worker
sudo /opt/myproject/scripts/update-service.sh worker \
    /path/to/myproject_worker-1.1.0-py3-none-any.whl
```

### Comandos de Gestión Systemd

```bash
# Ver estado de todos los servicios
sudo systemctl status myproject-*

# Iniciar/Detener/Reiniciar
sudo systemctl start myproject-api
sudo systemctl stop myproject-api
sudo systemctl restart myproject-api

# Ver logs
sudo journalctl -u myproject-api -f
sudo journalctl -u myproject-api --since "1 hour ago"
sudo journalctl -u myproject-api -n 100

# Habilitar/Deshabilitar inicio automático
sudo systemctl enable myproject-api
sudo systemctl disable myproject-api

# Recargar configuración si modificas el .service
sudo systemctl daemon-reload
sudo systemctl restart myproject-api
```

### Monitoreo con Systemd Timer

Crear timer para verificar servicios:

`/etc/systemd/system/myproject-healthcheck.service`:

```ini
[Unit]
Description=MyProject Health Check
After=network.target

[Service]
Type=oneshot
User=root
ExecStart=/opt/myproject/scripts/healthcheck.sh

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/myproject-healthcheck.timer`:

```ini
[Unit]
Description=Run MyProject Health Check every 5 minutes
Requires=myproject-healthcheck.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Unit=myproject-healthcheck.service

[Install]
WantedBy=timers.target
```

Script de health check `/opt/myproject/scripts/healthcheck.sh`:

```bash
#!/bin/bash

SERVICES=("myproject-api" "myproject-web" "myproject-worker")

for SERVICE in "${SERVICES[@]}"; do
    if ! systemctl is-active --quiet $SERVICE; then
        echo "WARNING: $SERVICE is not running. Restarting..."
        systemctl restart $SERVICE

        # Enviar alerta (email, webhook, etc.)
        # curl -X POST https://your-webhook.com/alert -d "service=$SERVICE"
    fi
done
```

Habilitar timer:

```bash
sudo chmod +x /opt/myproject/scripts/healthcheck.sh
sudo systemctl enable myproject-healthcheck.timer
sudo systemctl start myproject-healthcheck.timer
sudo systemctl list-timers
```

---

## 📊 Comparativa de Modalidades

| Aspecto | Windows Service (NSSM) | Docker | Systemd (Linux) |
|---------|------------------------|--------|-----------------|
| **Plataforma** | Windows Server/10+ | Cualquiera con Docker | Linux (Ubuntu, Debian, RHEL) |
| **Complejidad Setup** | Media | Alta | Media |
| **Gestión** | Services.msc / PowerShell | docker-compose / CLI | systemctl / journalctl |
| **Aislamiento** | Proceso | Contenedor completo | Proceso |
| **Portabilidad** | ❌ Solo Windows | ✅ Multiplataforma | ❌ Solo Linux |
| **Resource Limits** | ✅ Via NSSM | ✅ Nativo | ✅ Nativo |
| **Health Checks** | ✅ Via custom script | ✅ Integrado | ✅ Via timer |
| **Logs** | Archivos + Event Viewer | stdout/stderr + volumes | journald |
| **Backup/Restore** | Manual | Volúmenes + registry | Manual |
| **Escalabilidad** | Manual (múltiples instancias) | ✅ docker-compose scale | Manual (múltiples services) |
| **CI/CD Integration** | Media | ✅ Excelente | Buena |
| **Rollback** | Script custom | ✅ Rápido (imágenes previas) | Script custom |
| **Performance** | ✅ Nativo | Overhead mínimo (~2%) | ✅ Nativo |
| **Seguridad** | Usuario de servicio | ✅ No-root + redes internas | ✅ Sandboxing avanzado |
| **Monitoreo** | Task Scheduler | Prometheus + Grafana | systemd timers |

### Recomendaciones por Escenario

| Escenario | Modalidad Recomendada | Razón |
|-----------|----------------------|-------|
| Infraestructura 100% Windows | **A (NSSM)** | Nativo, mejor integración |
| Infraestructura heterogénea | **B (Docker)** | Portabilidad completa |
| Infraestructura Linux pura | **C (Systemd)** | Nativo, sin overhead |
| Múltiples entornos (dev/stage/prod) | **B (Docker)** | Consistencia entre entornos |
| Escalabilidad horizontal | **B (Docker)** | Orquestación fácil |
| Recursos limitados | **C (Systemd)** | Menor overhead |
| Equipo con experiencia Docker | **B (Docker)** | Aprovechar conocimiento |
| Aplicación legacy en Windows | **A (NSSM)** | Menor cambio en infraestructura |
| Cloud-native deployment | **B (Docker)** | Compatible con Kubernetes |

---

## 🔍 Troubleshooting

### Problemas Comunes - Windows

#### Servicio no inicia

```powershell
# Ver logs
Get-Content "C:\MyProject\Logs\api-stderr.log" -Tail 50

# Verificar permisos
icacls "C:\MyProject\Production\api"

# Probar comando manualmente
cd C:\MyProject\Production\api
.\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Error de permisos

```powershell
# Dar permisos al usuario de servicio
icacls "C:\MyProject" /grant "NT AUTHORITY\NetworkService:(OI)(CI)F" /T

# O configurar usuario específico en NSSM
& $nssm set MyProject-API ObjectName ".\ServiceUser" "password"
```

### Problemas Comunes - Docker

#### Contenedor no inicia

```bash
# Ver logs detallados
docker-compose -f docker-compose.production.yml logs api

# Inspeccionar contenedor
docker inspect myproject_api

# Probar comando manualmente
docker run -it --rm myproject/api:latest /bin/bash
```

#### No encuentra módulos

```bash
# Verificar que wheels se instalaron
docker exec myproject_api pip list

# Verificar PYTHONPATH
docker exec myproject_api python -c "import sys; print(sys.path)"

# Reconstruir sin cache
docker-compose -f docker-compose.production.yml build --no-cache api
```

### Problemas Comunes - Systemd

#### Servicio falla al iniciar

```bash
# Ver logs detallados
sudo journalctl -u myproject-api -n 100 --no-pager

# Verificar configuración
sudo systemctl status myproject-api

# Probar comando manualmente
sudo -u myproject bash -c "
    cd /opt/myproject/production/api && \
    source venv/bin/activate && \
    uvicorn main:app --host 0.0.0.0 --port 8000
"
```

#### Error de permisos

```bash
# Verificar ownership
sudo ls -la /opt/myproject/production/api

# Corregir permisos
sudo chown -R myproject:myproject /opt/myproject

# Verificar SELinux (RHEL/CentOS)
sudo getenforce
sudo setenforce 0  # Solo para testing
```

---

## 📋 Checklist de Despliegue

### Pre-Despliegue

- [ ] Código testeado en desarrollo
- [ ] Wheels compilados y verificados
- [ ] Variables de entorno configuradas
- [ ] Secrets generados de forma segura
- [ ] Base de datos migrada/actualizada
- [ ] Backups del sistema actual
- [ ] Plan de rollback definido

### Durante Despliegue

- [ ] Servicios detenidos correctamente
- [ ] Artefactos instalados sin errores
- [ ] Configuración actualizada
- [ ] Servicios iniciados
- [ ] Health checks pasando
- [ ] Logs sin errores críticos

### Post-Despliegue

- [ ] Endpoints respondiendo correctamente
- [ ] Tests de integración pasando
- [ ] Monitoreo funcionando
- [ ] Alertas configuradas
- [ ] Documentación actualizada
- [ ] Equipo notificado

---

## 📚 Referencias Adicionales

- [NSSM Documentation](https://nssm.cc/)
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Systemd Service Units](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Python Wheel Distribution](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [PyInstaller Documentation](https://pyinstaller.org/)

---

**Última actualización**: 2025-01-21
**Versión**: 1.0.0
**Autor**: DevOps Team
