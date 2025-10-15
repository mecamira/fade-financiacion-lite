# 📚 MANUAL DE GESTIÓN DEL SERVIDOR - FADE FINANCIACIÓN

## 🔐 ACCESO AL SERVIDOR

### Datos de Conexión
- **Servidor:** 116.202.12.50
- **Usuario:** fadeadmin
- **Contraseña:** [LA QUE CREEMOS]
- **Puerto SSH:** 22

### Cómo Conectarse

#### Desde Windows (PowerShell):
```powershell
ssh fadeadmin@116.202.12.50
```

#### Desde Mac/Linux (Terminal):
```bash
ssh fadeadmin@116.202.12.50
```

---

## 🎯 SCRIPT DE GESTIÓN AUTOMÁTICO

Una vez conectados al servidor, existe un script que facilita todas las operaciones:

```bash
cd ~/fade-financiacion-lite
./scripts/gestionar.sh
```

Este script muestra un menú interactivo con todas las opciones disponibles.

---

## 📋 OPERACIONES COMUNES

### 1. Ver Estado del Sistema

```bash
cd ~/fade-financiacion-lite
docker compose ps
```

**Deberías ver:**
- `fade-financiacion-app` - Estado: Up (healthy)
- `fade-selenium` - Estado: Up (healthy)

---

### 2. Ver Logs de la Aplicación

```bash
cd ~/fade-financiacion-lite
docker compose logs flask-app --tail=50
```

**Para ver logs en tiempo real:**
```bash
docker compose logs -f flask-app
```
(Presiona Ctrl+C para salir)

---

### 3. Reiniciar la Aplicación

**Si la aplicación falla o se comporta extraño:**

```bash
cd ~/fade-financiacion-lite
docker compose restart flask-app
```

**Para reiniciar todo el sistema:**
```bash
docker compose restart
```

---

### 4. Actualizar desde GitHub

**Cuando haya nuevas actualizaciones del código:**

```bash
cd ~/fade-financiacion-lite

# Descargar cambios
git pull origin main

# Reconstruir y reiniciar
docker compose down
docker compose build flask-app
docker compose up -d

# Verificar que todo funciona
docker compose ps
```

---

### 5. Hacer Backup de Datos

**Backup manual de las convocatorias:**

```bash
cd ~/fade-financiacion-lite

# Crear carpeta de backups si no existe
mkdir -p backups

# Copiar el archivo de datos
cp data/programas_financiacion.json backups/programas_$(date +%Y%m%d_%H%M%S).json

# Listar backups
ls -lh backups/
```

**Para descargar el backup a tu ordenador:**

Desde tu ordenador (no desde el servidor):
```bash
scp fadeadmin@116.202.12.50:~/fade-financiacion-lite/backups/programas_*.json .
```

---

### 6. Restaurar un Backup

```bash
cd ~/fade-financiacion-lite

# Ver backups disponibles
ls -lh backups/

# Restaurar un backup específico
cp backups/programas_20250115_140000.json data/programas_financiacion.json

# Dar permisos correctos
chmod 666 data/programas_financiacion.json

# Reiniciar la aplicación
docker compose restart flask-app
```

---

### 7. Solucionar Problemas de Permisos

**Si aparece "Permission denied" al guardar convocatorias:**

```bash
cd ~/fade-financiacion-lite
chmod 666 data/programas_financiacion.json
```

---

### 8. Ver Uso de Recursos del Servidor

**CPU y Memoria:**
```bash
htop
```
(Presiona Q para salir)

**Espacio en disco:**
```bash
df -h
```

**Memoria usada por Docker:**
```bash
docker stats
```
(Presiona Ctrl+C para salir)

---

## 🆘 RESOLUCIÓN DE PROBLEMAS COMUNES

### La aplicación no responde

1. Ver logs para detectar errores:
   ```bash
   docker compose logs flask-app --tail=100
   ```

2. Reiniciar:
   ```bash
   docker compose restart flask-app
   ```

3. Si sigue sin funcionar, reiniciar todo:
   ```bash
   docker compose down
   docker compose up -d
   ```

---

### Error "Selenium no responde"

```bash
docker compose restart selenium
```

Esperar 10 segundos y probar de nuevo.

---

### El servidor está muy lento

1. Ver qué está consumiendo recursos:
   ```bash
   docker stats
   ```

2. Reiniciar contenedores:
   ```bash
   docker compose restart
   ```

3. Si persiste, reiniciar el servidor completo:
   ```bash
   sudo reboot
   ```
   (La aplicación se reiniciará automáticamente)

---

### No puedo guardar convocatorias

```bash
cd ~/fade-financiacion-lite
sudo chmod 666 data/programas_financiacion.json
docker compose restart flask-app
```

---

## 🔒 SEGURIDAD

### Cambiar Contraseña del Usuario

```bash
passwd
```

### Cambiar Contraseña de Admin de la Aplicación

Editar el archivo `.env`:
```bash
cd ~/fade-financiacion-lite
nano .env
```

Buscar la línea `ADMIN_PASSWORD=` y cambiar el valor.

Guardar (Ctrl+O, Enter) y salir (Ctrl+X).

Reiniciar:
```bash
docker compose restart flask-app
```

---

## 📞 CONTACTOS DE EMERGENCIA

**Desarrollador:** Alejandro (Tu contacto aquí)
**Servidor:** Hetzner - https://console.hetzner.cloud/

---

## 🔄 MANTENIMIENTO RECOMENDADO

### Semanal
- Ver logs para detectar errores
- Verificar espacio en disco
- Hacer backup de datos

### Mensual
- Actualizar desde GitHub si hay cambios
- Revisar backups antiguos y eliminar los muy viejos
- Verificar uso de recursos

---

## 📚 COMANDOS RÁPIDOS DE REFERENCIA

```bash
# Ir a la carpeta del proyecto
cd ~/fade-financiacion-lite

# Ver estado
docker compose ps

# Ver logs
docker compose logs flask-app --tail=50

# Reiniciar
docker compose restart flask-app

# Actualizar
git pull origin main && docker compose down && docker compose build && docker compose up -d

# Backup
cp data/programas_financiacion.json backups/backup_$(date +%Y%m%d).json

# Permisos
chmod 666 data/programas_financiacion.json
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

Después de cualquier operación importante:

- [ ] Los contenedores están "Up (healthy)"
- [ ] La web carga en http://116.202.12.50
- [ ] Puedo hacer login como admin
- [ ] Puedo ver las convocatorias
- [ ] No hay errores en los logs

---

**Versión del Manual:** 1.0  
**Fecha:** Octubre 2025  
**Actualizado por:** Alejandro
