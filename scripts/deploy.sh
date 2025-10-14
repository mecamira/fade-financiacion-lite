#!/bin/bash
#
# DEPLOY - Despliegue de la aplicación FADE Financiación
# Este script despliega la aplicación en el VPS con Docker
#
# Uso: bash deploy.sh
#

set -e  # Detener si hay error

echo "=================================="
echo "🚀 FADE Financiación - Deploy"
echo "=================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Directorio del proyecto (donde está este script)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

log_info "Directorio del proyecto: $PROJECT_DIR"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "$PROJECT_DIR/docker-compose.yml" ]; then
    log_error "No se encuentra docker-compose.yml"
    log_error "Asegúrate de ejecutar este script desde el directorio del proyecto"
    exit 1
fi

cd "$PROJECT_DIR"

# 1. VERIFICAR ARCHIVO .env
log_step "Paso 1/9: Verificando configuración..."

if [ ! -f ".env" ]; then
    log_error "Archivo .env no encontrado"
    log_info "Copia .env.example y configúralo con tus valores:"
    log_info "  cp .env.example .env"
    log_info "  nano .env"
    exit 1
fi

# Verificar que las variables críticas están configuradas
check_env_var() {
    if ! grep -q "^$1=" .env || grep -q "^$1=.*TU_.*AQUI" .env || grep -q "^$1=$" .env; then
        log_error "Variable $1 no está configurada en .env"
        return 1
    fi
    return 0
}

log_info "Verificando variables de entorno..."
MISSING_VARS=0

check_env_var "SECRET_KEY" || MISSING_VARS=1
check_env_var "GEMINI_API_KEY" || MISSING_VARS=1
check_env_var "ADMIN_PASSWORD" || MISSING_VARS=1

if [ $MISSING_VARS -eq 1 ]; then
    log_error "Algunas variables críticas no están configuradas"
    log_info "Edita el archivo .env y configura todos los valores"
    exit 1
fi

log_info "✅ Configuración verificada"
echo ""

# 2. VERIFICAR DOCKER
log_step "Paso 2/9: Verificando Docker..."

if ! command -v docker &> /dev/null; then
    log_error "Docker no está instalado"
    log_info "Ejecuta primero: bash scripts/setup-vps.sh"
    exit 1
fi

if ! docker info &> /dev/null; then
    log_error "Docker no está corriendo o no tienes permisos"
    log_info "Intenta: sudo systemctl start docker"
    log_info "O ejecuta este script con sudo si es necesario"
    exit 1
fi

log_info "✅ Docker está disponible"
echo ""

# 3. DETENER CONTENEDORES EXISTENTES
log_step "Paso 3/9: Deteniendo contenedores existentes..."

if docker compose ps -q 2>/dev/null | grep -q .; then
    log_info "Deteniendo contenedores..."
    docker compose down
    log_info "✅ Contenedores detenidos"
else
    log_info "No hay contenedores corriendo"
fi
echo ""

# 4. LIMPIAR IMÁGENES ANTIGUAS (OPCIONAL)
log_step "Paso 4/9: Limpiando imágenes antiguas..."
docker image prune -f
log_info "✅ Limpieza completada"
echo ""

# 5. CONSTRUIR IMÁGENES
log_step "Paso 5/9: Construyendo imágenes Docker..."
log_warn "Esto puede tardar 5-10 minutos la primera vez..."
echo ""

docker compose build

log_info "✅ Imágenes construidas"
echo ""

# 6. VERIFICAR DIRECTORIOS
log_step "Paso 6/9: Verificando directorios necesarios..."

mkdir -p data logs uploads
chmod 755 data logs uploads

if [ ! -f "data/programas_financiacion.json" ]; then
    log_warn "No se encuentra data/programas_financiacion.json"
    log_info "Creando archivo vacío..."
    echo "[]" > data/programas_financiacion.json
fi

log_info "✅ Directorios preparados"
echo ""

# 7. INICIAR CONTENEDORES
log_step "Paso 7/9: Iniciando contenedores..."

docker compose up -d

log_info "✅ Contenedores iniciados"
echo ""

# Esperar a que los contenedores estén listos
log_info "Esperando a que la aplicación esté lista..."
sleep 5

# 8. VERIFICAR ESTADO
log_step "Paso 8/9: Verificando estado..."

echo ""
log_info "Estado de contenedores:"
docker compose ps
echo ""

# Verificar que la app responde
log_info "Probando conexión a la aplicación..."
if curl -f http://localhost:8000 > /dev/null 2>&1; then
    log_info "✅ La aplicación responde correctamente"
else
    log_warn "⚠️  La aplicación no responde aún. Verifica los logs."
fi
echo ""

# 9. MOSTRAR LOGS INICIALES
log_step "Paso 9/9: Mostrando logs iniciales..."
echo ""
docker compose logs --tail=20
echo ""

# RESUMEN FINAL
echo "=================================="
echo "✅ DEPLOY COMPLETADO"
echo "=================================="
echo ""
echo "🌐 Aplicación disponible en:"
echo "  - Local: http://localhost:8000"
echo "  - Servidor: http://$(curl -s ifconfig.me 2>/dev/null || echo 'TU_IP'):8000"
echo ""
echo "🔍 Comandos útiles:"
echo "  - Ver logs:      docker compose logs -f"
echo "  - Ver estado:    docker compose ps"
echo "  - Reiniciar:     docker compose restart"
echo "  - Detener:       docker compose down"
echo "  - Entrar al app: docker compose exec app bash"
echo ""
echo "📝 Próximos pasos:"
echo "  1. Verifica que la aplicación funciona: http://$(curl -s ifconfig.me 2>/dev/null || echo 'TU_IP'):8000"
echo "  2. Configura Nginx (opcional): bash scripts/configure-nginx.sh"
echo "  3. Configura SSL (opcional): bash scripts/configure-ssl.sh"
echo ""
echo "🆘 Si hay problemas:"
echo "  - Ver logs completos: docker compose logs -f"
echo "  - Revisar .env: cat .env"
echo "  - Estado de Docker: docker compose ps"
echo ""
echo "=================================="
