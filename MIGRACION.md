# 🚀 MIGRACIÓN AL VPS - FADE Financiación Lite

## 📋 ÍNDICE
1. [Requisitos Previos](#requisitos-previos)
2. [Preparación del VPS](#preparación-del-vps)
3. [Instalación de Docker](#instalación-de-docker)
4. [Subir el Código](#subir-el-código)
5. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
6. [Despliegue con Docker](#despliegue-con-docker)
7. [Configuración de Nginx (Opcional)](#configuración-de-nginx-opcional)
8. [Configuración de SSL/HTTPS (Opcional)](#configuración-de-sslhttps-opcional)
9. [Verificación y Testing](#verificación-y-testing)
10. [Mantenimiento y Actualización](#mantenimiento-y-actualización)
11. [Troubleshooting](#troubleshooting)

---

## 1️⃣ REQUISITOS PREVIOS

### ✅ En tu PC Local
- [x] Código funcionando en local
- [x] Repositorio en GitHub: https://github.com/mecamira/fade-financiacion-lite
- [x] Archivo `.env` con tus configuraciones (NO subido a GitHub)

### ✅ Del VPS
- **Sistema Operativo**: Ubuntu 20.04 o 22.04 (recomendado)
- **RAM**: Mínimo 2GB (recomendado 4GB)
- **Disco**: Mínimo 20GB libres
- **Acceso SSH**: Usuario y contraseña o clave SSH
- **IP Pública**: Para acceder desde internet

### 📝 Información a mano
- IP del servidor: `___________________`
- Usuario SSH: `___________________`
- Puerto SSH: `________` (normalmente 22)
- Dominio (opcional): `___________________`

---

## 2️⃣ PREPARACIÓN DEL VPS

### Paso 1: Conectar por SSH

Desde PowerShell en tu PC:

```powershell
ssh usuario@IP_DEL_SERVIDOR
```

O si usa un puerto diferente:

```powershell
ssh -p PUERTO usuario@IP_DEL_SERVIDOR
```

### Paso 2: Actualizar el sistema

```bash
# Actualizar lista de paquetes
sudo apt update

# Actualizar paquetes instalados
sudo apt upgrade -y

# Limpiar paquetes innecesarios
sudo apt autoremove -y
```

### Paso 3: Instalar herramientas básicas

```bash
sudo apt install -y \
    git \
    curl \
    wget \
    nano \
    htop \
    ufw
```

### Paso 4: Configurar Firewall (UFW)

```bash
# Permitir SSH (¡IMPORTANTE! No te bloquees)
sudo ufw allow ssh
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Habilitar firewall
sudo ufw --force enable

# Verificar estado
sudo ufw status
```

---

## 3️⃣ INSTALACIÓN DE DOCKER

### Opción A: Script Oficial (Recomendado)

```bash
# Descargar y ejecutar script oficial de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Añadir tu usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER

# Aplicar cambios de grupo (reloguear o ejecutar)
newgrp docker
```

### Opción B: Instalación Manual

```bash
# Eliminar versiones antiguas si existen
sudo apt remove docker docker-engine docker.io containerd runc

# Instalar dependencias
sudo apt update
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Añadir clave GPG oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Añadir repositorio
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Actualizar e instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Añadir usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### Verificar Instalación

```bash
# Verificar Docker
docker --version
# Debería mostrar: Docker version 24.0.x o superior

# Verificar Docker Compose
docker compose version
# Debería mostrar: Docker Compose version v2.x.x o superior

# Probar Docker
docker run hello-world
# Si ves "Hello from Docker!", ¡funciona! ✅
```

---

## 4️⃣ SUBIR EL CÓDIGO

### Opción A: Clonar desde GitHub (Recomendado)

```bash
# Ir al directorio home
cd ~

# Clonar repositorio
git clone https://github.com/mecamira/fade-financiacion-lite.git

# Entrar al directorio
cd fade-financiacion-lite

# Verificar archivos
ls -la
```

### Opción B: Subir con SCP (Desde tu PC)

Desde PowerShell en tu PC:

```powershell
# Comprimir el proyecto (opcional, más rápido)
Compress-Archive -Path C:\Users\aleja\fade-financiacion-lite\* -DestinationPath fade-financiacion.zip

# Subir al servidor
scp fade-financiacion.zip usuario@IP_SERVIDOR:/home/usuario/

# Luego en el servidor:
# cd ~
# unzip fade-financiacion.zip
# cd fade-financiacion-lite
```

---

## 5️⃣ CONFIGURACIÓN DE VARIABLES DE ENTORNO

### Crear archivo .env en el servidor

```bash
# Estar en el directorio del proyecto
cd ~/fade-financiacion-lite

# Crear archivo .env
nano .env
```

### Contenido del archivo .env (PRODUCCIÓN)

```env
# Flask - PRODUCCIÓN
FLASK_ENV=production
SECRET_KEY=GENERA_UNA_CLAVE_SEGURA_ALEATORIA_MUY_LARGA_AQUI

# Google Gemini AI
GEMINI_API_KEY=TU_API_KEY_REAL_AQUI

# Autenticación Admin
ADMIN_PASSWORD=CONTRASEÑA_SEGURA_ADMIN_PRODUCCION

# Base de datos
DATABASE_PATH=/app/data/programas_financiacion.json

# Selenium (Docker)
SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub

# Logs
LOG_DIR=/app/logs
```

### Generar SECRET_KEY segura

```bash
# Opción 1: Generar con Python
python3 -c 'import secrets; print(secrets.token_hex(32))'

# Opción 2: Generar con OpenSSL
openssl rand -hex 32

# Copia el resultado y pégalo en SECRET_KEY
```

### Guardar y salir de nano
- `Ctrl + O` → Enter (guardar)
- `Ctrl + X` (salir)

### Verificar archivo .env

```bash
cat .env
# Asegúrate de que tiene todos los valores correctos
```

---

## 6️⃣ DESPLIEGUE CON DOCKER

### Paso 1: Construir las imágenes

```bash
# Estar en el directorio del proyecto
cd ~/fade-financiacion-lite

# Construir imágenes (tarda 5-10 minutos la primera vez)
docker compose build

# Ver progreso
# Verás descargas de dependencias, instalaciones, etc.
```

### Paso 2: Iniciar los contenedores

```bash
# Iniciar en modo detached (background)
docker compose up -d

# Ver estado de contenedores
docker compose ps
```

Deberías ver algo como:

```
NAME                     IMAGE                         STATUS              PORTS
fade-app-1              fade-financiacion-lite-app    Up 10 seconds       0.0.0.0:8000->5000/tcp
fade-selenium-1         selenium/standalone-chrome    Up 10 seconds       4444/tcp
```

### Paso 3: Ver logs

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Ver logs solo de la app
docker compose logs -f app

# Ver logs solo de selenium
docker compose logs -f selenium

# Salir de logs: Ctrl + C
```

### Paso 4: Verificar que funciona

```bash
# Hacer petición local
curl http://localhost:8000

# Si ves HTML, ¡funciona! ✅
```

---

## 7️⃣ CONFIGURACIÓN DE NGINX (Opcional pero recomendado)

Si quieres usar el puerto 80 (HTTP estándar) y/o añadir un dominio.

### Instalar Nginx

```bash
sudo apt install -y nginx
```

### Crear configuración para tu sitio

```bash
sudo nano /etc/nginx/sites-available/fade-financiacion
```

### Contenido (SIN dominio - Solo IP)

```nginx
server {
    listen 80;
    server_name IP_DEL_SERVIDOR;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Contenido (CON dominio)

```nginx
server {
    listen 80;
    server_name financiacion.tudominio.com www.financiacion.tudominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Activar configuración

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/fade-financiacion /etc/nginx/sites-enabled/

# Eliminar configuración por defecto (opcional)
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Si dice "test is successful", recargar nginx
sudo systemctl reload nginx
```

### Verificar

Abre tu navegador en:
- `http://IP_DEL_SERVIDOR` (si usaste IP)
- `http://financiacion.tudominio.com` (si usaste dominio)

---

## 8️⃣ CONFIGURACIÓN DE SSL/HTTPS (Opcional)

Solo si tienes un dominio configurado.

### Instalar Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtener certificado SSL

```bash
# Reemplaza con tu dominio real
sudo certbot --nginx -d financiacion.tudominio.com -d www.financiacion.tudominio.com
```

Te preguntará:
1. **Email**: Tu email (para avisos de renovación)
2. **Términos**: Aceptar (A)
3. **Redirect HTTP → HTTPS**: Sí (2)

### Verificar renovación automática

```bash
# Probar renovación
sudo certbot renew --dry-run

# Si no hay errores, ¡todo OK! ✅
```

### Resultado

Ahora tu sitio estará disponible en:
- ✅ `https://financiacion.tudominio.com` (SEGURO)
- 🔄 `http://financiacion.tudominio.com` → redirige a HTTPS

---

## 9️⃣ VERIFICACIÓN Y TESTING

### ✅ Checklist de verificación

```bash
# 1. Contenedores corriendo
docker compose ps
# Ambos deben estar "Up"

# 2. Logs sin errores
docker compose logs app | tail -50
# No debe haber errores críticos

# 3. Puertos escuchando
sudo netstat -tulpn | grep 8000
# Debe mostrar Docker escuchando en 8000

# 4. Nginx funcionando (si lo instalaste)
sudo systemctl status nginx
# Debe estar "active (running)"

# 5. Acceso web
curl -I http://localhost:8000
# Debe devolver "HTTP/1.1 200 OK"
```

### 🧪 Tests funcionales

Abre en tu navegador:

1. **Dashboard público**: `http://tu-servidor/`
   - [ ] Se ve correctamente
   - [ ] Programas cargan
   - [ ] Filtros funcionan

2. **Login admin**: `http://tu-servidor/admin/login`
   - [ ] Puedes hacer login
   - [ ] Ves el panel de gestión

3. **Extracción Gemini**: Panel admin
   - [ ] Pega texto de convocatoria
   - [ ] Extrae información correctamente

4. **Análisis compatibilidad**: `http://tu-servidor/financiacion/analizar-compatibilidad`
   - [ ] Formulario funciona
   - [ ] Análisis se genera

---

## 🔟 MANTENIMIENTO Y ACTUALIZACIÓN

### Ver logs en tiempo real

```bash
docker compose logs -f
```

### Reiniciar aplicación

```bash
# Reiniciar solo la app
docker compose restart app

# Reiniciar todo
docker compose restart
```

### Detener aplicación

```bash
docker compose down
```

### Actualizar código desde GitHub

```bash
# 1. Detener contenedores
docker compose down

# 2. Actualizar código
git pull origin main

# 3. Reconstruir imágenes (si hay cambios en Dockerfile)
docker compose build

# 4. Iniciar de nuevo
docker compose up -d

# 5. Verificar logs
docker compose logs -f
```

### Ver uso de recursos

```bash
# CPU y RAM de contenedores
docker stats

# Espacio en disco
df -h

# Contenedores corriendo
docker ps
```

### Backup de datos

```bash
# Backup del JSON de programas
cp ~/fade-financiacion-lite/data/programas_financiacion.json \
   ~/fade-financiacion-lite/data/programas_financiacion.json.backup-$(date +%Y%m%d)

# Backup de logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz ~/fade-financiacion-lite/logs/
```

---

## 🆘 TROUBLESHOOTING

### Problema 1: "docker: command not found"

```bash
# Reinstalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Añadir usuario al grupo
sudo usermod -aG docker $USER
newgrp docker
```

### Problema 2: "Permission denied" al ejecutar Docker

```bash
# Añadir usuario al grupo docker
sudo usermod -aG docker $USER

# Reloguear o aplicar cambios
newgrp docker

# O cerrar sesión SSH y volver a conectar
```

### Problema 3: Puerto 8000 ya en uso

```bash
# Ver qué está usando el puerto
sudo netstat -tulpn | grep 8000

# Matar proceso si es necesario
sudo kill -9 PID_DEL_PROCESO

# O cambiar puerto en docker-compose.yml:
# ports:
#   - "8001:5000"  # Usar 8001 en lugar de 8000
```

### Problema 4: Contenedor se reinicia constantemente

```bash
# Ver logs detallados
docker compose logs app

# Entrar al contenedor para debug
docker compose exec app bash

# Ver variables de entorno
docker compose exec app env
```

### Problema 5: "Error: GEMINI_API_KEY no está configurada"

```bash
# Verificar que el .env existe
ls -la ~/fade-financiacion-lite/.env

# Verificar contenido
cat ~/fade-financiacion-lite/.env | grep GEMINI

# Reiniciar contenedores después de cambiar .env
docker compose down
docker compose up -d
```

### Problema 6: Nginx no inicia

```bash
# Ver estado
sudo systemctl status nginx

# Ver logs
sudo journalctl -u nginx -n 50

# Probar configuración
sudo nginx -t

# Reiniciar nginx
sudo systemctl restart nginx
```

### Problema 7: No se puede acceder desde internet

```bash
# Verificar firewall
sudo ufw status

# Asegurarse de que puerto 80 está abierto
sudo ufw allow 80/tcp

# Verificar que nginx escucha en todas las IPs
sudo netstat -tulpn | grep :80
# Debe mostrar 0.0.0.0:80 no solo 127.0.0.1:80
```

### Problema 8: Scraping BDNS falla

```bash
# Ver logs de Selenium
docker compose logs selenium

# Verificar que Selenium está corriendo
docker compose ps selenium

# Reiniciar solo Selenium
docker compose restart selenium
```

### Problema 9: Cambios en código no se reflejan

```bash
# Reconstruir imágenes
docker compose build --no-cache

# Reiniciar contenedores
docker compose up -d --force-recreate
```

### Problema 10: Disco lleno

```bash
# Ver espacio
df -h

# Limpiar imágenes Docker no usadas
docker system prune -a

# Limpiar logs viejos
sudo journalctl --vacuum-time=7d

# Limpiar paquetes
sudo apt autoremove
sudo apt clean
```

---

## 📊 COMANDOS ÚTILES RÁPIDOS

```bash
# Estado general
docker compose ps                    # Ver contenedores
docker compose logs -f              # Ver logs en vivo
docker stats                        # Ver uso de recursos

# Gestión contenedores
docker compose up -d                # Iniciar
docker compose down                 # Detener
docker compose restart              # Reiniciar
docker compose build                # Reconstruir

# Acceso a contenedores
docker compose exec app bash        # Entrar al contenedor de la app
docker compose exec selenium bash   # Entrar al contenedor de selenium

# Logs
docker compose logs app             # Logs de la app
docker compose logs selenium        # Logs de selenium
docker compose logs -f --tail=100   # Últimas 100 líneas en vivo

# Actualización
git pull                            # Actualizar código
docker compose build                # Reconstruir
docker compose up -d                # Reiniciar
```

---

## 🎯 RESUMEN EJECUTIVO

### Para arrancar la aplicación:
```bash
cd ~/fade-financiacion-lite
docker compose up -d
```

### Para ver si funciona:
```bash
docker compose ps
docker compose logs -f
```

### Para actualizar:
```bash
docker compose down
git pull
docker compose build
docker compose up -d
```

### Para detener:
```bash
docker compose down
```

---

## 📞 CONTACTO Y SOPORTE

- **Documentación Docker**: https://docs.docker.com/
- **Documentación Flask**: https://flask.palletsprojects.com/
- **Documentación Nginx**: https://nginx.org/en/docs/

---

**Fecha de creación**: 2025-10-11  
**Versión**: 1.0.0  
**Autor**: Alejandro Camira

---

## ✅ CHECKLIST FINAL DE MIGRACIÓN

- [ ] VPS actualizado y configurado
- [ ] Docker y Docker Compose instalados
- [ ] Firewall configurado (UFW)
- [ ] Código clonado desde GitHub
- [ ] Archivo .env creado con valores de producción
- [ ] Imágenes Docker construidas
- [ ] Contenedores iniciados correctamente
- [ ] Nginx instalado y configurado (opcional)
- [ ] SSL/HTTPS configurado (opcional)
- [ ] Todos los tests funcionales pasados
- [ ] Backup inicial realizado

**¡Cuando todos estén marcados, tu aplicación está en producción! 🎉**
