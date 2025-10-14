# 🚀 GUÍA COMPLETA DE DESPLIEGUE

## 📅 PLAN DE 3 DÍAS

Esta guía te llevará paso a paso desde cero hasta tener la aplicación en producción.

---

## ✅ DÍA 1: PREPARACIÓN (Completado)

### Ya has hecho:
- [x] Estructura del proyecto creada
- [x] Archivos copiados del monolito
- [x] Código funcionando en local
- [x] Pruebas locales completadas
- [x] Repositorio en GitHub creado
- [x] Código subido a GitHub

**Estado**: ✅ Completado

---

## 🎯 DÍA 2: DEPLOY (2-4 horas)

### Checklist del Día 2

#### Parte 1: Contratar VPS (30 minutos)
- [ ] Leer: `CONTRATAR_HETZNER.md`
- [ ] Crear cuenta en Hetzner
- [ ] Contratar Hetzner CX21 (4.51€/mes)
- [ ] Anotar IP del servidor
- [ ] Crear SSH key
- [ ] Primera conexión exitosa
- [ ] Crear usuario `fade`

📄 **Documento**: `CONTRATAR_HETZNER.md`

---

#### Parte 2: Configurar VPS (30 minutos)

**Paso 1**: Conectar al VPS

```bash
# Desde tu PC (PowerShell)
ssh -i $HOME\.ssh\fade-hetzner fade@IP_DEL_SERVIDOR
```

**Paso 2**: Subir script de setup

Opción A - Clonar repositorio (recomendado):
```bash
# En el VPS
cd ~
git clone https://github.com/mecamira/fade-financiacion-lite.git
cd fade-financiacion-lite
```

Opción B - Subir script manualmente:
```powershell
# Desde tu PC
scp -i $HOME\.ssh\fade-hetzner scripts/setup-vps.sh fade@IP_SERVIDOR:~/
```

**Paso 3**: Ejecutar setup automático

```bash
# En el VPS
sudo bash scripts/setup-vps.sh
```

Este script instalará automáticamente:
- ✅ Docker y Docker Compose
- ✅ Nginx
- ✅ Certbot (para SSL)
- ✅ Firewall configurado
- ✅ Herramientas básicas

⏱️ **Duración**: 5-10 minutos

**Paso 4**: Cerrar y reconectar

```bash
# Salir del VPS
exit

# Volver a conectar (para aplicar grupo docker)
ssh -i $HOME\.ssh\fade-hetzner fade@IP_DEL_SERVIDOR
```

---

#### Parte 3: Configurar aplicación (20 minutos)

**Paso 1**: Entrar al directorio del proyecto

```bash
cd ~/fade-financiacion-lite
```

**Paso 2**: Crear archivo .env

```bash
# Copiar ejemplo
cp .env.example .env

# Editar con nano
nano .env
```

**Contenido del .env (IMPORTANTE - Usar valores reales)**:

```env
# Flask - PRODUCCIÓN
FLASK_ENV=production
SECRET_KEY=PEGA_AQUI_LA_CLAVE_GENERADA_ABAJO

# Google Gemini AI
GEMINI_API_KEY=TU_API_KEY_REAL_DE_GEMINI

# Autenticación Admin
ADMIN_PASSWORD=UNA_CONTRASEÑA_MUY_SEGURA_PARA_ADMIN

# Base de datos
DATABASE_PATH=/app/data/programas_financiacion.json

# Selenium (Docker)
SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub

# Logs
LOG_DIR=/app/logs
```

**Paso 3**: Generar SECRET_KEY segura

```bash
# Generar clave aleatoria
python3 -c 'import secrets; print(secrets.token_hex(32))'

# Copiar el resultado y pegarlo en SECRET_KEY en el archivo .env
```

**Paso 4**: Guardar archivo .env

- Presiona `Ctrl + O` → Enter (para guardar)
- Presiona `Ctrl + X` (para salir)

**Paso 5**: Verificar .env

```bash
# Ver el archivo (sin mostrar contraseñas)
cat .env
```

---

#### Parte 4: Desplegar aplicación (10 minutos)

**Ejecutar script de deploy**:

```bash
# En el VPS, dentro del directorio del proyecto
bash scripts/deploy.sh
```

Este script hará automáticamente:
1. ✅ Verificar configuración (.env)
2. ✅ Verificar Docker
3. ✅ Detener contenedores antiguos (si existen)
4. ✅ Construir imágenes Docker (5-10 min)
5. ✅ Crear directorios necesarios
6. ✅ Iniciar contenedores
7. ✅ Verificar que funciona
8. ✅ Mostrar logs iniciales

⏱️ **Duración**: 5-10 minutos (construcción de imágenes)

**Resultado esperado**:

```
==================================
✅ DEPLOY COMPLETADO
==================================

🌐 Aplicación disponible en:
  - Local: http://localhost:8000
  - Servidor: http://TU_IP:8000

🔍 Comandos útiles:
  - Ver logs:      docker compose logs -f
  - Ver estado:    docker compose ps
  - Reiniciar:     docker compose restart
  - Detener:       docker compose down
```

---

#### Parte 5: Verificar funcionamiento (10 minutos)

**Paso 1**: Acceder desde el navegador

```
http://TU_IP_DEL_SERVIDOR:8000
```

**Paso 2**: Checklist de verificación

- [ ] Dashboard público carga
- [ ] Se ven los programas de financiación
- [ ] Los filtros funcionan
- [ ] Login admin funciona (http://TU_IP:8000/admin/login)
- [ ] Panel de gestión accesible
- [ ] No hay errores en los logs

**Ver logs en tiempo real**:

```bash
docker compose logs -f
```

(Presiona `Ctrl + C` para salir)

---

#### Parte 6: Configurar Nginx (Opcional - 15 minutos)

Si quieres usar el puerto 80 (HTTP estándar) en lugar del 8000.

**Crear configuración de Nginx**:

```bash
sudo nano /etc/nginx/sites-available/fade-financiacion
```

**Contenido**:

```nginx
server {
    listen 80;
    server_name TU_IP_DEL_SERVIDOR;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts para operaciones largas (IA, scraping)
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

**Activar configuración**:

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/fade-financiacion /etc/nginx/sites-enabled/

# Eliminar configuración por defecto
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

**Ahora accesible en**:
```
http://TU_IP_DEL_SERVIDOR
```

---

#### Parte 7: Configurar Dominio (Opcional - 20 minutos)

Solo si tienes un dominio (ej: financiacion.fade.es)

**Paso 1**: Configurar DNS

En tu proveedor de dominios (donde compraste el dominio), crea un registro A:

```
Tipo: A
Nombre: financiacion (o @ para el dominio raíz)
Valor: TU_IP_DEL_SERVIDOR
TTL: 3600 (o automático)
```

**Paso 2**: Esperar propagación DNS (5-30 minutos)

Verificar:
```bash
# Desde tu PC
nslookup financiacion.tudominio.com
```

**Paso 3**: Actualizar configuración Nginx

```bash
sudo nano /etc/nginx/sites-available/fade-financiacion
```

Cambiar línea `server_name`:

```nginx
server_name financiacion.tudominio.com www.financiacion.tudominio.com;
```

Recargar:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

#### Parte 8: Configurar SSL/HTTPS (Opcional - 10 minutos)

Solo si configuraste un dominio en el paso anterior.

**Obtener certificado SSL gratuito**:

```bash
sudo certbot --nginx -d financiacion.tudominio.com
```

Certbot preguntará:
1. **Email**: Tu email (para avisos de renovación)
2. **Términos**: Escribe `A` (aceptar)
3. **Redirect HTTP → HTTPS**: Escribe `2` (sí, redirigir)

**¡Listo! Ahora tienes HTTPS** 🔒:
```
https://financiacion.tudominio.com
```

**Renovación automática**:

Certbot configura renovación automática. Verificar:

```bash
sudo certbot renew --dry-run
```

---

### 📊 Resumen del Día 2

Al final del Día 2 deberías tener:

- ✅ VPS Hetzner contratado y configurado
- ✅ Docker instalado
- ✅ Aplicación desplegada y funcionando
- ✅ Accesible desde internet (http://TU_IP:8000)
- ✅ Nginx configurado (opcional)
- ✅ Dominio configurado (opcional)
- ✅ SSL/HTTPS activo (opcional)

---

## 🔍 DÍA 3: VALIDACIÓN Y OPTIMIZACIÓN (2 horas)

### Checklist del Día 3

#### Parte 1: Pruebas funcionales completas (30 minutos)

**1. Dashboard público**
- [ ] Acceder a la home
- [ ] Buscar programas con diferentes filtros
- [ ] Ver detalles de un programa
- [ ] Verificar que las imágenes cargan
- [ ] Probar en móvil (responsive)

**2. Panel de administración**
- [ ] Login con contraseña admin
- [ ] Ver lista de programas
- [ ] Crear programa nuevo
- [ ] Editar programa existente
- [ ] Eliminar programa de prueba

**3. Extracción con Gemini AI**
- [ ] Pegar texto de una convocatoria
- [ ] Verificar que extrae la información
- [ ] Guardar el programa extraído
- [ ] Verificar que aparece en el dashboard

**4. Análisis de compatibilidad**
- [ ] Acceder a /financiacion/analizar-compatibilidad
- [ ] Completar formulario empresa
- [ ] Seleccionar convocatoria
- [ ] Generar análisis
- [ ] Verificar que el análisis tiene sentido

**5. Scraping BDNS (si funciona)**
- [ ] Probar búsqueda en BDNS
- [ ] Verificar que encuentra resultados
- [ ] Importar convocatoria

---

#### Parte 2: Configurar backups (20 minutos)

**Script de backup automático**:

```bash
# Crear script
nano ~/backup-fade.sh
```

**Contenido**:

```bash
#!/bin/bash
# Backup automático FADE Financiación

BACKUP_DIR="$HOME/backups"
PROJECT_DIR="$HOME/fade-financiacion-lite"
DATE=$(date +%Y%m%d-%H%M%S)

# Crear directorio de backups
mkdir -p $BACKUP_DIR

# Backup del JSON de programas
cp $PROJECT_DIR/data/programas_financiacion.json \
   $BACKUP_DIR/programas-$DATE.json

# Backup de logs (comprimir)
tar -czf $BACKUP_DIR/logs-$DATE.tar.gz \
   $PROJECT_DIR/logs/

# Mantener solo los últimos 7 backups
cd $BACKUP_DIR
ls -t programas-*.json | tail -n +8 | xargs rm -f
ls -t logs-*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup completado: $DATE"
```

**Hacer ejecutable**:

```bash
chmod +x ~/backup-fade.sh
```

**Configurar cron (backup diario a las 3 AM)**:

```bash
# Editar crontab
crontab -e

# Añadir línea (al final del archivo):
0 3 * * * /home/fade/backup-fade.sh >> /home/fade/backup.log 2>&1
```

**Probar backup manual**:

```bash
bash ~/backup-fade.sh
ls -lh ~/backups/
```

---

#### Parte 3: Monitorización básica (15 minutos)

**Ver uso de recursos**:

```bash
# CPU y RAM de contenedores
docker stats

# Espacio en disco
df -h

# Ver logs en tiempo real
docker compose logs -f app
```

**Script de health check**:

```bash
nano ~/check-fade.sh
```

**Contenido**:

```bash
#!/bin/bash
# Health check FADE Financiación

echo "=== FADE Health Check ==="
echo "Fecha: $(date)"
echo ""

# Verificar contenedores
echo "Contenedores:"
docker compose -f ~/fade-financiacion-lite/docker-compose.yml ps
echo ""

# Verificar respuesta HTTP
echo "HTTP Check:"
if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Aplicación responde OK"
else
    echo "❌ Aplicación NO responde"
fi
echo ""

# Uso de disco
echo "Espacio en disco:"
df -h / | grep -v "Filesystem"
echo ""

# Memoria
echo "Memoria:"
free -h | grep -E "Mem:|Swap:"
```

**Hacer ejecutable y probar**:

```bash
chmod +x ~/check-fade.sh
bash ~/check-fade.sh
```

---

#### Parte 4: Documentación para FADE (30 minutos)

**Crear documento de operaciones**:

```bash
nano ~/OPERACIONES_FADE.md
```

**Contenido**:

```markdown
# 📖 FADE Financiación - Guía de Operaciones

## 🌐 Accesos

- **URL Pública**: http://TU_IP_O_DOMINIO
- **Panel Admin**: http://TU_IP_O_DOMINIO/admin/login
- **Contraseña Admin**: [GUARDADA EN LUGAR SEGURO]

## 🔐 Acceso SSH

```bash
ssh -i ~/.ssh/fade-hetzner fade@TU_IP
```

## 🔧 Comandos Útiles

### Ver estado
```bash
cd ~/fade-financiacion-lite
docker compose ps
```

### Ver logs
```bash
docker compose logs -f
```

### Reiniciar aplicación
```bash
docker compose restart
```

### Detener aplicación
```bash
docker compose down
```

### Iniciar aplicación
```bash
docker compose up -d
```

### Ver uso de recursos
```bash
docker stats
```

## 🔄 Actualizar aplicación

```bash
cd ~/fade-financiacion-lite
docker compose down
git pull origin main
docker compose build
docker compose up -d
```

## 💾 Backups

Los backups se ejecutan automáticamente cada día a las 3 AM.

Ver backups:
```bash
ls -lh ~/backups/
```

Backup manual:
```bash
bash ~/backup-fade.sh
```

## 🆘 Problemas Comunes

### La aplicación no responde
```bash
# Ver logs
docker compose logs app

# Reiniciar
docker compose restart app
```

### Contenedores no inician
```bash
# Ver errores
docker compose logs

# Verificar .env
cat .env
```

### Disco lleno
```bash
# Ver espacio
df -h

# Limpiar Docker
docker system prune -a
```

## 📞 Soporte Técnico

- **Hetzner Support**: support@hetzner.com
- **GitHub Repo**: https://github.com/mecamira/fade-financiacion-lite
```

---

#### Parte 5: Optimizaciones (30 minutos)

**1. Configurar logs rotativos**

```bash
sudo nano /etc/logrotate.d/fade-financiacion
```

**Contenido**:

```
/home/fade/fade-financiacion-lite/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

**2. Ajustar Docker para producción**

Editar `docker-compose.yml`:

```bash
nano ~/fade-financiacion-lite/docker-compose.yml
```

Añadir restart policies y limites de recursos:

```yaml
services:
  app:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 512M
  
  selenium:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 512M
```

Aplicar cambios:

```bash
docker compose down
docker compose up -d
```

**3. Configurar alertas por email (opcional)**

Instalar mailutils:

```bash
sudo apt install -y mailutils
```

Script de alerta:

```bash
nano ~/alert-fade.sh
```

**Contenido**:

```bash
#!/bin/bash
# Alerta si la aplicación no responde

if ! curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "ALERTA: FADE Financiación no responde" | \
    mail -s "FADE Down" tu-email@fade.es
fi
```

Añadir a crontab (check cada 15 min):

```bash
crontab -e

# Añadir:
*/15 * * * * /home/fade/alert-fade.sh
```

---

### 📊 Resumen del Día 3

Al final del Día 3 deberías tener:

- ✅ Todas las funcionalidades probadas
- ✅ Backups automáticos configurados
- ✅ Monitorización básica
- ✅ Documentación para operaciones
- ✅ Logs rotativos configurados
- ✅ Optimizaciones aplicadas
- ✅ Sistema de alertas (opcional)

---

## 🎯 CHECKLIST FINAL COMPLETO

### Infraestructura
- [ ] VPS contratado y pagado
- [ ] Docker instalado y funcionando
- [ ] Firewall configurado
- [ ] Nginx instalado (opcional)
- [ ] SSL/HTTPS activo (opcional)

### Aplicación
- [ ] Código desplegado
- [ ] Variables de entorno configuradas
- [ ] Contenedores corriendo
- [ ] Aplicación accesible desde internet
- [ ] Panel admin funcional

### Funcionalidades
- [ ] Dashboard público funciona
- [ ] Búsqueda y filtros funcionan
- [ ] Login admin funciona
- [ ] Gestión de programas funciona
- [ ] Extracción Gemini funciona
- [ ] Análisis compatibilidad funciona
- [ ] Scraping BDNS funciona (opcional)

### Seguridad y Operaciones
- [ ] Contraseña admin fuerte
- [ ] SSH con clave (no contraseña)
- [ ] Firewall activo
- [ ] Backups automáticos
- [ ] Logs configurados
- [ ] Documentación lista

---

## 📞 CONTACTOS Y RECURSOS

### Proveedores
- **Hetzner**: https://console.hetzner.cloud/
- **Hetzner Support**: support@hetzner.com

### Documentación
- **Docker**: https://docs.docker.com/
- **Nginx**: https://nginx.org/en/docs/
- **Certbot**: https://certbot.eff.org/

### Repositorio
- **GitHub**: https://github.com/mecamira/fade-financiacion-lite

---

## 🎉 ¡ENHORABUENA!

Si has completado todos los pasos, ahora tienes:

✅ Una aplicación Flask en producción  
✅ Con Docker y contenedores  
✅ Accesible desde internet  
✅ Con HTTPS (si configuraste dominio)  
✅ Con backups automáticos  
✅ Monitoreada y documentada  

**¡Tu proyecto está en producción!** 🚀

---

**Versión**: 1.0.0  
**Fecha**: 2025-10-11  
**Tiempo total estimado**: 6-12 horas  
**Coste mensual**: ~4.51€/mes
