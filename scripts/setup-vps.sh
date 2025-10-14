#!/bin/bash
#
# SETUP VPS - Configuración automática del servidor
# Este script prepara el VPS con todo lo necesario para la aplicación
#
# Uso: bash setup-vps.sh
#

set -e  # Detener si hay error

echo "=================================="
echo "🚀 FADE Financiación - Setup VPS"
echo "=================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Verificar que se ejecuta como root o con sudo
if [ "$EUID" -ne 0 ]; then 
    log_error "Este script debe ejecutarse como root o con sudo"
    log_info "Ejecuta: sudo bash setup-vps.sh"
    exit 1
fi

# 1. ACTUALIZAR SISTEMA
log_info "Paso 1/8: Actualizando sistema..."
apt update -y
apt upgrade -y
apt autoremove -y
log_info "✅ Sistema actualizado"
echo ""

# 2. INSTALAR HERRAMIENTAS BÁSICAS
log_info "Paso 2/8: Instalando herramientas básicas..."
apt install -y \
    git \
    curl \
    wget \
    nano \
    vim \
    htop \
    unzip \
    ufw \
    ca-certificates \
    gnupg \
    lsb-release
log_info "✅ Herramientas básicas instaladas"
echo ""

# 3. CONFIGURAR FIREWALL
log_info "Paso 3/8: Configurando firewall UFW..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
log_info "✅ Firewall configurado"
ufw status
echo ""

# 4. INSTALAR DOCKER
log_info "Paso 4/8: Instalando Docker..."

# Eliminar versiones antiguas
apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Añadir repositorio oficial de Docker
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
apt update -y
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalación
docker --version
docker compose version

log_info "✅ Docker instalado correctamente"
echo ""

# 5. CONFIGURAR DOCKER PARA USUARIO NO-ROOT
log_info "Paso 5/8: Configurando permisos Docker..."

# Si existe el usuario 'fade', añadirlo al grupo docker
if id "fade" &>/dev/null; then
    usermod -aG docker fade
    log_info "✅ Usuario 'fade' añadido al grupo docker"
else
    log_warn "Usuario 'fade' no existe. Crear manualmente si es necesario."
fi

# Permitir que docker funcione sin sudo para el usuario actual
if [ ! -z "$SUDO_USER" ]; then
    usermod -aG docker $SUDO_USER
    log_info "✅ Usuario '$SUDO_USER' añadido al grupo docker"
fi

echo ""

# 6. INSTALAR NGINX
log_info "Paso 6/8: Instalando Nginx..."
apt install -y nginx
systemctl enable nginx
systemctl start nginx
log_info "✅ Nginx instalado y corriendo"
echo ""

# 7. INSTALAR CERTBOT (para SSL)
log_info "Paso 7/8: Instalando Certbot..."
apt install -y certbot python3-certbot-nginx
log_info "✅ Certbot instalado"
echo ""

# 8. CONFIGURAR LÍMITES DEL SISTEMA
log_info "Paso 8/8: Optimizando configuración del sistema..."

# Aumentar límites de archivos abiertos
cat >> /etc/security/limits.conf << EOF
# Límites para aplicaciones Docker
*               soft    nofile          65536
*               hard    nofile          65536
root            soft    nofile          65536
root            hard    nofile          65536
EOF

# Optimizar configuración de red para Docker
cat >> /etc/sysctl.conf << EOF
# Optimizaciones para Docker
net.ipv4.ip_forward=1
net.ipv4.conf.all.forwarding=1
net.bridge.bridge-nf-call-iptables=1
net.bridge.bridge-nf-call-ip6tables=1
EOF

sysctl -p

log_info "✅ Sistema optimizado"
echo ""

# RESUMEN
echo ""
echo "=================================="
echo "✅ SETUP COMPLETADO"
echo "=================================="
echo ""
echo "📦 Software instalado:"
echo "  - Docker: $(docker --version)"
echo "  - Docker Compose: $(docker compose version)"
echo "  - Nginx: $(nginx -v 2>&1)"
echo "  - Certbot: $(certbot --version)"
echo ""
echo "🔒 Firewall (UFW):"
ufw status | grep -E "Status|22|80|443"
echo ""
echo "🎯 Próximos pasos:"
echo "  1. Cerrar sesión SSH y volver a entrar (para aplicar grupo docker)"
echo "  2. Clonar repositorio: git clone https://github.com/mecamira/fade-financiacion-lite.git"
echo "  3. Configurar .env con tus valores"
echo "  4. Ejecutar: bash deploy.sh"
echo ""
echo "=================================="

# Crear directorio para la aplicación
log_info "Creando directorio para la aplicación..."
mkdir -p /opt/fade-financiacion
chown -R ${SUDO_USER:-root}:${SUDO_USER:-root} /opt/fade-financiacion
log_info "✅ Directorio /opt/fade-financiacion creado"
echo ""

log_info "🎉 ¡Setup completado con éxito!"
log_warn "⚠️  IMPORTANTE: Cierra la sesión SSH y vuelve a entrar para que los cambios de grupo docker surtan efecto"
