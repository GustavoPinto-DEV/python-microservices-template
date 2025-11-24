# Guía de Despliegue Docker - Producción

Esta guía explica cómo integrar y usar el sistema Docker profesional para desplegar el proyecto completo en producción.

## 📋 Índice

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Estructura de Archivos](#estructura-de-archivos)
3. [Integración Paso a Paso](#integración-paso-a-paso)
4. [Configuración](#configuración)
5. [Despliegue](#despliegue)
6. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura del Sistema

### Capas de Red

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERNET                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │  NGINX  │ (Reverse Proxy)
                    │  :80    │
                    │  :443   │
                    └────┬────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐     ┌────▼────┐    ┌────▼────┐
    │   API   │     │   WEB   │    │ Grafana │
    │  :8000  │     │  :8000  │    │  :3000  │
    └────┬────┘     └────┬────┘    └────┬────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐     ┌────▼────┐    ┌────▼────┐
    │ WORKER  │     │  Redis  │    │  Prom.  │
    │         │     │  :6379  │    │  :9090  │
    └────┬────┘     └─────────┘    └─────────┘
         │
    ┌────▼────────┐
    │  PostgreSQL │
    │    :5432    │
    └─────────────┘
```

### Componentes

| Servicio    | Puerto | Red       | Propósito                           |
|-------------|--------|-----------|-------------------------------------|
| Nginx       | 80/443 | frontend  | Reverse proxy, SSL, load balancing  |
| API         | 8000   | frontend+backend | REST API con FastAPI          |
| Web         | 8000   | frontend+backend | Aplicación web con Jinja2     |
| Worker      | -      | backend   | Procesos batch en background        |
| PostgreSQL  | 5432   | backend   | Base de datos principal             |
| Redis       | 6379   | cache     | Cache y sesiones                    |
| Prometheus  | 9090   | frontend  | Métricas (opcional)                 |
| Grafana     | 3000   | frontend  | Dashboards (opcional)               |

---

## 📁 Estructura de Archivos

### Estructura Actual vs Estructura Objetivo

```
# ANTES (templates/)
templates/
├── docker-compose.yml              # Simple, dev-oriented
├── template_api/
│   └── Dockerfile                  # Basic Dockerfile
├── template_web/
│   └── Dockerfile
└── template_consola/
    └── Dockerfile

# DESPUÉS (proyecto real)
my_project/
├── docker-compose.production.yml   # ⭐ NUEVO - Compose completo
├── .env.production.example         # ⭐ NUEVO - Template de variables
├── .dockerignore                   # ⭐ NUEVO - Excluir archivos
│
├── docker/                         # ⭐ NUEVO - Configuraciones Docker
│   ├── api/
│   │   └── Dockerfile.production   # Multi-stage optimizado
│   ├── web/
│   │   └── Dockerfile.production
│   ├── consola/
│   │   └── Dockerfile.production
│   ├── nginx/
│   │   ├── nginx.conf              # Config principal
│   │   ├── conf.d/
│   │   │   └── default.conf        # Virtual hosts
│   │   └── ssl/                    # Certificados SSL
│   │       ├── fullchain.pem
│   │       └── privkey.pem
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       ├── dashboards/
│       └── datasources/
│
├── data_layer/                     # Repositorio compartido
│   └── repositorio_lib/
│       └── config/
│           └── .env                # ⚠️ NO commitear
│
├── api/                            # Servicio API
│   ├── main.py
│   ├── config/
│   ├── controller/
│   └── ...
│
├── web/                            # Servicio Web
│   ├── main.py
│   └── ...
│
└── worker/                         # Servicio Worker
    ├── main.py
    └── ...
```

---

## 🔧 Integración Paso a Paso

### Paso 1: Preparar la Estructura

```bash
# 1. Crear estructura de directorios Docker
mkdir -p docker/{api,web,consola,nginx/{conf.d,ssl},prometheus,grafana/{dashboards,datasources}}

# 2. Copiar archivos base de templates/
cp templates/docker-compose.production.yml ./
cp templates/.env.production.example ./.env
cp templates/.dockerignore.production ./.dockerignore

# 3. Copiar Dockerfiles
cp templates/Dockerfile.production.template docker/api/Dockerfile.production
cp templates/Dockerfile.production.template docker/web/Dockerfile.production
cp templates/Dockerfile.production.template docker/consola/Dockerfile.production

# 4. Copiar configuración de Nginx
cp templates/nginx.production.conf docker/nginx/conf.d/default.conf
```

### Paso 2: Adaptar los Dockerfiles

Cada servicio necesita ajustes específicos. Ejemplo para **API**:

```dockerfile
# docker/api/Dockerfile.production

# ============ STAGE 1: Builder ============
FROM python:3.12-slim as builder

WORKDIR /build

# Copiar requirements
COPY data_layer/requirements.txt ./repo_requirements.txt
COPY api/requirements.txt ./api_requirements.txt

# Instalar dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar repositorio_lib
COPY data_layer/ /build/data_layer/
RUN pip install -e /build/data_layer/

# Instalar dependencias de API
RUN pip install -r api_requirements.txt

# ============ STAGE 2: Runtime ============
FROM python:3.12-slim as runtime

ENV PATH="/opt/venv/bin:$PATH"

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser -u 1001 appuser

# Crear directorios
RUN mkdir -p /app /var/log/app/logs && \
    chown -R appuser:appuser /app /var/log/app

# Copiar virtualenv
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
COPY --from=builder --chown=appuser:appuser /build/data_layer /app/data_layer

WORKDIR /app

# Copiar código API
COPY --chown=appuser:appuser api/ ./

USER appuser

EXPOSE 8000

# Comando específico para API
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4"]
```

**Para Web**: Igual pero copiar `web/` y posiblemente servir static files.

**Para Consola**:
```dockerfile
CMD ["python", "main.py"]
# O con scheduler:
# CMD ["python", "main_scheduler.py"]
```

### Paso 3: Configurar Variables de Entorno

```bash
# Editar .env con valores de producción
nano .env

# IMPORTANTE: Generar secrets seguros
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(16))"
```

Archivo `.env` mínimo:

```bash
PROJECT_NAME=myproject
ENVIRONMENT=production

# Database
DB_NAME=myapp_db
DB_USER=myapp_user
DB_PASSWORD=tu_password_seguro_aqui

# Redis
REDIS_PASSWORD=tu_password_redis_aqui

# JWT
SECRET_KEY=tu_secret_key_generado_aqui
JWT_SECRET_KEY=tu_jwt_secret_generado_aqui

# Nginx
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# API
API_WORKERS=4
```

### Paso 4: Configurar Nginx

Editar `docker/nginx/conf.d/default.conf`:

1. **Cambiar server_name**:
```nginx
server_name tudominio.com www.tudominio.com;
```

2. **Configurar SSL** (ver sección SSL más abajo)

3. **Ajustar upstreams** si tienes múltiples instancias:
```nginx
upstream api_backend {
    server api:8000;
    server api2:8000;  # Si escalaras horizontalmente
    server api3:8000;
}
```

### Paso 5: SSL/TLS (Producción)

#### Opción A: Let's Encrypt (Recomendado)

```bash
# 1. Instalar certbot
sudo apt-get update
sudo apt-get install certbot

# 2. Obtener certificado
sudo certbot certonly --standalone -d tudominio.com -d www.tudominio.com

# 3. Copiar certificados a docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/tudominio.com/fullchain.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/tudominio.com/privkey.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/tudominio.com/chain.pem docker/nginx/ssl/

# 4. Configurar renovación automática
sudo crontab -e
# Agregar: 0 0 1 * * certbot renew --quiet && docker-compose restart nginx
```

#### Opción B: Certificado autofirmado (Solo desarrollo/testing)

```bash
cd docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem -out fullchain.pem \
  -subj "/CN=localhost"
```

---

## 🚀 Despliegue

### Build de Imágenes

```bash
# Build todas las imágenes
docker-compose -f docker-compose.production.yml build

# Build imagen específica
docker-compose -f docker-compose.production.yml build api

# Build sin cache (si hay problemas)
docker-compose -f docker-compose.production.yml build --no-cache
```

### Iniciar Servicios

```bash
# Iniciar todos los servicios
docker-compose -f docker-compose.production.yml up -d

# Ver logs en tiempo real
docker-compose -f docker-compose.production.yml logs -f

# Ver logs de servicio específico
docker-compose -f docker-compose.production.yml logs -f api

# Ver estado de servicios
docker-compose -f docker-compose.production.yml ps
```

### Detener Servicios

```bash
# Detener todos los servicios (mantiene volúmenes)
docker-compose -f docker-compose.production.yml down

# Detener y eliminar volúmenes (⚠️ DESTRUYE DATOS)
docker-compose -f docker-compose.production.yml down -v

# Restart de servicio específico
docker-compose -f docker-compose.production.yml restart api
```

### Escalar Servicios

```bash
# Escalar API a 3 instancias
docker-compose -f docker-compose.production.yml up -d --scale api=3

# Escalar workers
docker-compose -f docker-compose.production.yml up -d --scale worker=2
```

---

## 📊 Monitoreo y Mantenimiento

### Health Checks

```bash
# Check de todos los servicios
docker-compose -f docker-compose.production.yml ps

# Health check manual
curl http://localhost/health
curl http://localhost/api/health
```

### Logs

```bash
# Logs centralizados en volumen app_logs
docker volume inspect myproject_app_logs

# Ver logs dentro del contenedor
docker exec myproject_api tail -f /var/log/app/logs/$(date +%Y-%m-%d)/template_api.log

# Exportar logs
docker cp myproject_api:/var/log/app/logs ./backup_logs/
```

### Backups

#### Base de Datos

```bash
# Backup manual
docker exec myproject_postgres pg_dump -U myapp_user myapp_db > backup_$(date +%Y%m%d).sql

# Backup automático (agregar a crontab)
0 2 * * * docker exec myproject_postgres pg_dump -U myapp_user myapp_db | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz

# Restaurar backup
docker exec -i myproject_postgres psql -U myapp_user myapp_db < backup_20250121.sql
```

#### Volúmenes

```bash
# Backup de volumen
docker run --rm -v myproject_postgres_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/postgres_data_backup.tar.gz -C /data .

# Restaurar volumen
docker run --rm -v myproject_postgres_data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/postgres_data_backup.tar.gz -C /data
```

### Actualizaciones

```bash
# 1. Pull cambios de código
git pull

# 2. Rebuild imágenes
docker-compose -f docker-compose.production.yml build

# 3. Recrear contenedores (zero-downtime con replicas)
docker-compose -f docker-compose.production.yml up -d --no-deps --build api

# 4. Verificar
docker-compose -f docker-compose.production.yml ps
curl http://localhost/health
```

### Limpieza

```bash
# Eliminar imágenes sin usar
docker image prune -a

# Eliminar contenedores detenidos
docker container prune

# Eliminar volúmenes sin usar
docker volume prune

# Limpieza completa (⚠️ cuidado)
docker system prune -a --volumes
```

---

## 🔍 Troubleshooting

### Problema: Contenedor no inicia

```bash
# Ver logs detallados
docker-compose -f docker-compose.production.yml logs api

# Verificar configuración
docker-compose -f docker-compose.production.yml config

# Entrar al contenedor (si está corriendo)
docker exec -it myproject_api /bin/bash

# Ver proceso dentro del contenedor
docker exec myproject_api ps aux
```

### Problema: No se puede conectar a la base de datos

```bash
# Verificar que postgres esté healthy
docker-compose -f docker-compose.production.yml ps postgres

# Ver logs de postgres
docker-compose -f docker-compose.production.yml logs postgres

# Test de conexión desde API
docker exec myproject_api pg_isready -h postgres -U myapp_user

# Test manual de conexión
docker exec -it myproject_postgres psql -U myapp_user -d myapp_db
```

### Problema: Nginx devuelve 502 Bad Gateway

```bash
# Verificar upstreams
docker-compose -f docker-compose.production.yml logs nginx

# Verificar que backend esté corriendo
docker-compose -f docker-compose.production.yml ps api web

# Test desde nginx hacia backend
docker exec myproject_nginx wget -O- http://api:8000/health
```

### Problema: Variables de entorno no se cargan

```bash
# Verificar que el archivo .env existe
ls -la .env

# Ver variables cargadas en el contenedor
docker exec myproject_api env | grep DB_

# Recrear contenedor con nuevas variables
docker-compose -f docker-compose.production.yml up -d --force-recreate api
```

### Problema: Volúmenes con permisos incorrectos

```bash
# Ver permisos dentro del contenedor
docker exec myproject_api ls -la /var/log/app/logs

# Corregir permisos
docker exec -u root myproject_api chown -R appuser:appuser /var/log/app/logs

# Recrear volumen (⚠️ pierde datos)
docker-compose -f docker-compose.production.yml down -v
docker-compose -f docker-compose.production.yml up -d
```

---

## 🎯 Checklist de Producción

Antes de desplegar a producción, verificar:

### Seguridad
- [ ] Variables de entorno con secrets fuertes
- [ ] SSL/TLS configurado con certificados válidos
- [ ] Usuarios no-root en contenedores
- [ ] Firewall configurado (solo puertos 80/443 expuestos)
- [ ] Base de datos NO expuesta públicamente
- [ ] Rate limiting configurado en Nginx
- [ ] Security headers configurados
- [ ] Secrets NO commiteados en Git (.env en .gitignore)

### Performance
- [ ] Workers de API ajustados según CPUs
- [ ] Pool de conexiones de BD optimizado
- [ ] Cache configurado (Redis)
- [ ] Gzip compression habilitado
- [ ] Static files con cache largo
- [ ] Health checks configurados

### Monitoreo
- [ ] Logs centralizados configurados
- [ ] Prometheus + Grafana (opcional pero recomendado)
- [ ] Health checks funcionando
- [ ] Alertas configuradas (email, Slack, etc.)

### Backup
- [ ] Backup automático de BD configurado
- [ ] Backup de volúmenes configurado
- [ ] Procedimiento de restauración probado
- [ ] Backups almacenados fuera del servidor

### Alta Disponibilidad
- [ ] Múltiples replicas de servicios críticos
- [ ] Load balancing configurado en Nginx
- [ ] Restart policies configuradas
- [ ] Health checks con reinicio automático

---

## 📚 Referencias

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Let's Encrypt](https://letsencrypt.org/)

---

## 🆘 Soporte

Para problemas o dudas:
1. Revisar logs: `docker-compose logs -f`
2. Verificar health checks: `curl http://localhost/health`
3. Consultar esta guía
4. Contactar al equipo de DevOps

---

**Última actualización**: 2025-01-21
**Versión**: 1.0.0
