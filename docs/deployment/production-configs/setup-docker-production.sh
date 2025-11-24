#!/bin/bash
# ============================================================================
# Setup Script - Docker Production Environment
# ============================================================================
#
# Este script automatiza la configuración inicial del entorno Docker
# para producción.
#
# Uso:
#   chmod +x setup-docker-production.sh
#   ./setup-docker-production.sh
#
# ============================================================================

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones helper
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Banner
echo "============================================================================"
echo "   Docker Production Setup"
echo "   Configuración automatizada del entorno Docker"
echo "============================================================================"
echo ""

# ----------------------------------------------------------------------------
# Verificar requisitos
# ----------------------------------------------------------------------------
log_info "Verificando requisitos..."

if ! command -v docker &> /dev/null; then
    log_error "Docker no está instalado. Instalar desde https://docs.docker.com/get-docker/"
    exit 1
fi
log_success "Docker instalado"

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose no está instalado."
    exit 1
fi
log_success "Docker Compose instalado"

# ----------------------------------------------------------------------------
# Crear estructura de directorios
# ----------------------------------------------------------------------------
log_info "Creando estructura de directorios..."

mkdir -p docker/{api,web,consola,nginx/{conf.d,ssl},prometheus,grafana/{dashboards,datasources}}
mkdir -p data_layer/repositorio_lib/config
mkdir -p backups

log_success "Directorios creados"

# ----------------------------------------------------------------------------
# Copiar archivos de configuración
# ----------------------------------------------------------------------------
log_info "Copiando archivos de configuración..."

# Docker Compose
if [ ! -f "docker-compose.production.yml" ]; then
    if [ -f "templates/docker-compose.production.yml" ]; then
        cp templates/docker-compose.production.yml ./
        log_success "docker-compose.production.yml copiado"
    else
        log_warning "docker-compose.production.yml no encontrado en templates/"
    fi
else
    log_warning "docker-compose.production.yml ya existe, saltando..."
fi

# Variables de entorno
if [ ! -f ".env" ]; then
    if [ -f "templates/.env.production.example" ]; then
        cp templates/.env.production.example ./.env
        log_success ".env creado desde template"
        log_warning "⚠ IMPORTANTE: Editar .env con valores de producción"
    else
        log_warning ".env.production.example no encontrado"
    fi
else
    log_warning ".env ya existe, saltando..."
fi

# Dockerignore
if [ ! -f ".dockerignore" ]; then
    if [ -f "templates/.dockerignore.production" ]; then
        cp templates/.dockerignore.production ./.dockerignore
        log_success ".dockerignore copiado"
    fi
else
    log_warning ".dockerignore ya existe, saltando..."
fi

# Nginx config
if [ ! -f "docker/nginx/conf.d/default.conf" ]; then
    if [ -f "templates/nginx.production.conf" ]; then
        cp templates/nginx.production.conf docker/nginx/conf.d/default.conf
        log_success "Configuración de Nginx copiada"
    fi
else
    log_warning "Configuración de Nginx ya existe, saltando..."
fi

# Dockerfiles
for service in api web consola; do
    if [ ! -f "docker/${service}/Dockerfile.production" ]; then
        if [ -f "templates/Dockerfile.production.template" ]; then
            cp templates/Dockerfile.production.template docker/${service}/Dockerfile.production
            log_success "Dockerfile para ${service} copiado"
        fi
    else
        log_warning "Dockerfile para ${service} ya existe, saltando..."
    fi
done

# ----------------------------------------------------------------------------
# Generar secrets
# ----------------------------------------------------------------------------
log_info "Generando secrets seguros..."

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
REDIS_PASS=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))" 2>/dev/null || openssl rand -base64 16)

log_success "Secrets generados"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECRETS GENERADOS (Agregar a .env):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "SECRET_KEY=${SECRET_KEY}"
echo "JWT_SECRET_KEY=${JWT_SECRET}"
echo "REDIS_PASSWORD=${REDIS_PASS}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Preguntar si agregar automáticamente
read -p "¿Agregar estos secrets automáticamente a .env? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sed -i.bak "s|SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|g" .env
    sed -i.bak "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT_SECRET}|g" .env
    sed -i.bak "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASS}|g" .env
    rm .env.bak
    log_success "Secrets agregados a .env"
fi

# ----------------------------------------------------------------------------
# SSL/TLS Setup
# ----------------------------------------------------------------------------
log_info "Configuración SSL/TLS"
echo ""
echo "Opciones:"
echo "  1) Usar Let's Encrypt (Producción - Recomendado)"
echo "  2) Generar certificado autofirmado (Desarrollo/Testing)"
echo "  3) Saltar (Configurar manualmente después)"
echo ""
read -p "Seleccionar opción [1-3]: " ssl_option

case $ssl_option in
    1)
        log_info "Configuración Let's Encrypt"
        read -p "Dominio principal (ej: ejemplo.com): " domain
        read -p "Email para notificaciones: " email

        log_warning "Asegúrate de que el dominio ${domain} apunte a esta IP antes de continuar"
        read -p "Presiona Enter para continuar..."

        if command -v certbot &> /dev/null; then
            sudo certbot certonly --standalone -d $domain -d www.$domain --email $email --agree-tos
            sudo cp /etc/letsencrypt/live/$domain/fullchain.pem docker/nginx/ssl/
            sudo cp /etc/letsencrypt/live/$domain/privkey.pem docker/nginx/ssl/
            sudo cp /etc/letsencrypt/live/$domain/chain.pem docker/nginx/ssl/
            log_success "Certificados SSL configurados"
        else
            log_warning "Certbot no instalado. Instalar con: sudo apt-get install certbot"
        fi
        ;;
    2)
        log_info "Generando certificado autofirmado..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout docker/nginx/ssl/privkey.pem \
            -out docker/nginx/ssl/fullchain.pem \
            -subj "/CN=localhost"
        cp docker/nginx/ssl/fullchain.pem docker/nginx/ssl/chain.pem
        log_success "Certificado autofirmado generado"
        log_warning "⚠ Solo para desarrollo. Usar Let's Encrypt en producción."
        ;;
    3)
        log_warning "Configuración SSL saltada. Configurar manualmente en docker/nginx/ssl/"
        ;;
esac

# ----------------------------------------------------------------------------
# Configuración de Nginx
# ----------------------------------------------------------------------------
log_info "¿Configurar dominio en Nginx?"
read -p "Dominio (Enter para saltar): " nginx_domain

if [ ! -z "$nginx_domain" ]; then
    sed -i.bak "s|server_name yourdomain.com www.yourdomain.com;|server_name ${nginx_domain} www.${nginx_domain};|g" docker/nginx/conf.d/default.conf
    rm docker/nginx/conf.d/default.conf.bak
    log_success "Dominio configurado en Nginx: ${nginx_domain}"
fi

# ----------------------------------------------------------------------------
# Verificar configuración
# ----------------------------------------------------------------------------
log_info "Verificando configuración de Docker Compose..."

if docker-compose -f docker-compose.production.yml config > /dev/null 2>&1; then
    log_success "Configuración válida"
else
    log_error "Configuración inválida. Revisar docker-compose.production.yml"
    exit 1
fi

# ----------------------------------------------------------------------------
# Resumen
# ----------------------------------------------------------------------------
echo ""
echo "============================================================================"
echo "   Setup Completado"
echo "============================================================================"
echo ""
log_success "Estructura de directorios creada"
log_success "Archivos de configuración copiados"
log_success "Secrets generados"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PRÓXIMOS PASOS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Editar .env con configuración de producción:"
echo "   nano .env"
echo ""
echo "2. Revisar y ajustar Dockerfiles en docker/api/, docker/web/, docker/consola/"
echo ""
echo "3. Configurar dominio en docker/nginx/conf.d/default.conf"
echo ""
echo "4. Build de imágenes:"
echo "   docker-compose -f docker-compose.production.yml build"
echo ""
echo "5. Iniciar servicios:"
echo "   docker-compose -f docker-compose.production.yml up -d"
echo ""
echo "6. Verificar:"
echo "   docker-compose -f docker-compose.production.yml ps"
echo "   curl http://localhost/health"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 Documentación completa: DOCKER_DEPLOYMENT_GUIDE.md"
echo ""
echo "============================================================================"
