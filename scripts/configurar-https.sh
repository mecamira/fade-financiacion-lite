#!/bin/bash
#
# CONFIGURAR HTTPS - financiacion.fade.es con certificado de Let's Encrypt
#
# Requisitos: el registro DNS de financiacion.fade.es ya apunta a este servidor
# y la app está desplegada con la versión actual (bash scripts/deploy.sh).
#
# Uso: sudo bash scripts/configurar-https.sh correo@fade.es
#      (el correo recibe los avisos de Let's Encrypt si la renovación fallara)
#

set -e

DOMINIO="financiacion.fade.es"
WEBROOT="/var/www/certbot"
SITIO="/etc/nginx/sites-available/fade-financiacion"
EMAIL="$1"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "${BLUE}[STEP]${NC} $1"; }

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=================================="
echo "🔒 FADE Financiación - HTTPS"
echo "=================================="
echo ""

# 1. COMPROBACIONES PREVIAS
log_step "Paso 1/6: Comprobaciones previas..."

if [ "$(id -u)" -ne 0 ]; then
    log_error "Ejecuta el script con sudo: sudo bash scripts/configurar-https.sh correo@fade.es"
    exit 1
fi

if [ -z "$EMAIL" ]; then
    log_error "Falta el correo para los avisos de Let's Encrypt"
    log_info "Uso: sudo bash scripts/configurar-https.sh correo@fade.es"
    exit 1
fi

IP_DOMINIO=$(getent ahostsv4 "$DOMINIO" | awk 'NR==1 {print $1}')
IP_SERVIDOR=$(curl -4 -s --max-time 10 https://ifconfig.me || true)

if [ -z "$IP_DOMINIO" ]; then
    log_error "$DOMINIO todavía no resuelve. Espera a que el registro DNS esté creado y propagado."
    exit 1
fi
if [ "$IP_DOMINIO" != "$IP_SERVIDOR" ]; then
    log_error "$DOMINIO apunta a $IP_DOMINIO, pero este servidor es $IP_SERVIDOR"
    exit 1
fi
log_info "✅ $DOMINIO apunta a este servidor ($IP_SERVIDOR)"

if ! curl -sf --max-time 10 http://127.0.0.1:8000/health > /dev/null; then
    log_error "La app no responde en 127.0.0.1:8000. Despliégala primero: bash scripts/deploy.sh"
    exit 1
fi
log_info "✅ La app responde"

if ! command -v certbot &> /dev/null; then
    log_info "Instalando certbot..."
    apt-get update -qq && apt-get install -y -qq certbot
fi
echo ""

# 2. COPIA DE SEGURIDAD DE NGINX
log_step "Paso 2/6: Copia de seguridad de la configuración de nginx..."
BACKUP="/root/nginx-backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP"
for d in sites-available sites-enabled conf.d; do
    [ -d "/etc/nginx/$d" ] && cp -a "/etc/nginx/$d" "$BACKUP/"
done
log_info "✅ Copia en $BACKUP"
echo ""

# 3. NGINX TEMPORAL (solo HTTP) PARA VALIDAR EL DOMINIO
log_step "Paso 3/6: Preparando nginx para la validación de Let's Encrypt..."
mkdir -p "$WEBROOT"

cat > "$SITIO" <<EOF
server {
    listen 80 default_server;
    server_name $DOMINIO _;
    client_max_body_size 20M;

    location /.well-known/acme-challenge/ {
        root $WEBROOT;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }
}
EOF

# Este servidor solo aloja la herramienta: se deja activo únicamente este sitio
find /etc/nginx/sites-enabled -mindepth 1 -delete
ln -s "$SITIO" /etc/nginx/sites-enabled/fade-financiacion

if ls /etc/nginx/conf.d/*.conf &> /dev/null; then
    log_warn "Hay ficheros en /etc/nginx/conf.d/ que podrían interferir:"
    ls /etc/nginx/conf.d/*.conf
fi

nginx -t
systemctl reload nginx
log_info "✅ nginx preparado"
echo ""

# 4. CERTIFICADO
log_step "Paso 4/6: Solicitando el certificado a Let's Encrypt..."
certbot certonly --webroot -w "$WEBROOT" -d "$DOMINIO" \
    --email "$EMAIL" --agree-tos --no-eff-email --non-interactive \
    --deploy-hook "systemctl reload nginx"
log_info "✅ Certificado emitido"
echo ""

# 5. NGINX DEFINITIVO (HTTPS)
log_step "Paso 5/6: Activando HTTPS..."
cp "$SITIO" "$BACKUP/fade-financiacion.temporal"
cp "$PROJECT_DIR/nginx/fade-financiacion.conf" "$SITIO"

if ! nginx -t; then
    log_error "La configuración HTTPS no es válida. Se restaura la temporal (HTTP)."
    cp "$BACKUP/fade-financiacion.temporal" "$SITIO"
    systemctl reload nginx
    exit 1
fi
systemctl reload nginx

if curl -sf --max-time 10 "https://$DOMINIO/health" > /dev/null; then
    log_info "✅ https://$DOMINIO responde"
else
    log_warn "⚠️  https://$DOMINIO no responde todavía. Revisa: systemctl status nginx"
fi

log_info "Probando la renovación automática..."
certbot renew --dry-run
echo ""

# 6. COOKIE DE SESIÓN SEGURA
log_step "Paso 6/6: Activando la cookie de sesión segura..."
cd "$PROJECT_DIR"
if grep -q '^SESSION_COOKIE_SECURE=' .env; then
    sed -i 's/^SESSION_COOKIE_SECURE=.*/SESSION_COOKIE_SECURE=1/' .env
else
    echo "SESSION_COOKIE_SECURE=1" >> .env
fi
docker compose up -d --force-recreate flask-app
log_info "✅ Cookie segura activada"
echo ""

echo "=================================="
echo "✅ HTTPS CONFIGURADO"
echo "=================================="
echo ""
echo "🌐 https://$DOMINIO"
echo "🔁 El certificado se renueva solo (certbot.timer)"
echo "💾 Copia de la configuración anterior de nginx: $BACKUP"
echo ""
