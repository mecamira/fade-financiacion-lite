# 🚀 CONTRATAR VPS EN HETZNER

## 📋 INFORMACIÓN DEL PLAN

### Hetzner CX21 - Características
- **Precio**: 4.51€/mes (IVA incluido)
- **CPU**: 2 vCPU AMD
- **RAM**: 4 GB
- **Disco**: 40 GB SSD
- **Tráfico**: 20 TB
- **Ubicación**: Alemania, Finlandia o USA
- **IPv4**: 1 incluida
- **IPv6**: Sí
- **Backups**: +20% del precio (opcional)

**✅ Suficiente para**: 50-100 usuarios simultáneos, con margen de crecimiento

---

## 🎯 PASO A PASO: CREAR CUENTA Y CONTRATAR

### Paso 1: Crear cuenta en Hetzner

1. Ve a: https://accounts.hetzner.com/signUp
2. Completa el formulario:
   - **Email**: Tu email profesional
   - **Contraseña**: Crea una segura
   - **Nombre y apellidos**
   - **Dirección completa**
3. **Importante**: Marca "I have read and agree to the terms and conditions"
4. Click en **"Sign up"**
5. Revisa tu email y confirma la cuenta

### Paso 2: Añadir método de pago

1. Accede a https://console.hetzner.cloud/
2. Ve a tu perfil (arriba derecha)
3. Click en **"Billing"**
4. Click en **"Payment methods"**
5. Añade tarjeta de crédito o PayPal
   - **Recomendado**: Tarjeta de crédito (proceso más rápido)

### Paso 3: Crear proyecto

1. En el panel principal: https://console.hetzner.cloud/
2. Click en **"New Project"**
3. Nombre del proyecto: `fade-financiacion` (o el que prefieras)
4. Click en **"Add Project"**

### Paso 4: Crear servidor (VPS)

1. Dentro del proyecto, click en **"Add Server"**
2. Configuración:

#### **Ubicación** (Location)
- ✅ **Recomendado**: `Falkenstein, Germany` (mejor para España)
- Alternativa: `Helsinki, Finland` (también buena para Europa)

#### **Imagen** (Image)
- **Sistema operativo**: Ubuntu
- **Versión**: `Ubuntu 22.04` (LTS - Long Term Support)

#### **Tipo** (Type)
- Selecciona: **Standard**
- Elige: **CX21** (2 vCPU, 4GB RAM, 40GB SSD)
- Precio mostrado: ~4.51€/mes

#### **Networking**
- **IPv4**: Dejar marcado (necesario)
- **IPv6**: Dejar marcado (gratis)

#### **SSH Keys** (¡IMPORTANTE!)

**Opción A: Crear nueva SSH key (Recomendado si no tienes)**

Desde PowerShell en tu PC:

```powershell
# Crear carpeta .ssh si no existe
mkdir $HOME\.ssh -Force

# Generar clave SSH
ssh-keygen -t ed25519 -C "fade-hetzner" -f $HOME\.ssh\fade-hetzner

# Cuando pregunte por passphrase, puedes dejarlo vacío (Enter) o poner una contraseña
```

Ahora copia la clave pública:

```powershell
# Ver y copiar la clave pública
cat $HOME\.ssh\fade-hetzner.pub
```

En Hetzner:
1. Click en **"Add SSH Key"**
2. Pega el contenido de `fade-hetzner.pub`
3. Nombre: `fade-key`
4. Click en **"Add SSH Key"**

**Opción B: Usar SSH key existente**
- Si ya tienes una SSH key, copia el contenido de tu `~/.ssh/id_rsa.pub` o similar

#### **Backups** (Opcional)
- ❌ No marcar por ahora (puedes activarlo después)
- Cuesta +20% (~0.90€/mes más)

#### **Nombre del servidor**
- Nombre: `fade-financiacion-prod` (o el que prefieras)

5. **Revisar resumen**:
   - Server: CX21
   - Location: Falkenstein
   - Image: Ubuntu 22.04
   - Precio: ~4.51€/mes

6. Click en **"Create & Buy now"**

---

## ⏱️ ESPERANDO EL SERVIDOR

El servidor tarda **30-60 segundos** en crearse.

Verás:
1. Estado: "Initializing..."
2. Estado: "Starting..."  
3. Estado: "Running" ✅

---

## 📝 INFORMACIÓN IMPORTANTE (GUARDAR)

Una vez creado, anota esta información:

```
INFORMACIÓN DEL VPS HETZNER
============================

IP del servidor: ___________________
Usuario: root
SSH Key: ~/.ssh/fade-hetzner (Windows: %USERPROFILE%\.ssh\fade-hetzner)

Panel Hetzner: https://console.hetzner.cloud/
Proyecto: fade-financiacion
Servidor: fade-financiacion-prod

Fecha contratación: ___/___/2025
Precio mensual: 4.51€
```

---

## 🔌 PRIMERA CONEXIÓN AL SERVIDOR

### Desde PowerShell en Windows:

```powershell
# Conectar usando la clave SSH
ssh -i $HOME\.ssh\fade-hetzner root@IP_DEL_SERVIDOR
```

**Primera vez**:
- Te preguntará: "Are you sure you want to continue connecting?"
- Escribe: `yes` y Enter

Deberías ver algo como:

```
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-91-generic x86_64)
...
root@fade-financiacion-prod:~#
```

**¡Enhorabuena! Ya estás dentro del servidor.** 🎉

---

## 🔒 PRIMERA CONFIGURACIÓN DE SEGURIDAD (IMPORTANTE)

### Paso 1: Actualizar sistema

```bash
apt update && apt upgrade -y
```

### Paso 2: Crear usuario no-root (Seguridad)

```bash
# Crear usuario
adduser fade

# Cuando pida contraseña, crea una SEGURA y GUÁRDALA
# El resto de campos puedes dejarlos vacíos (Enter)

# Dar permisos sudo
usermod -aG sudo fade

# Copiar SSH key al nuevo usuario
rsync --archive --chown=fade:fade ~/.ssh /home/fade/
```

### Paso 3: Configurar firewall básico

```bash
# Instalar UFW
apt install -y ufw

# Permitir SSH (IMPORTANTE: no te bloquees)
ufw allow 22/tcp
ufw allow OpenSSH

# Permitir HTTP y HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Habilitar firewall
ufw --force enable

# Verificar
ufw status
```

### Paso 4: Desconectar y probar nuevo usuario

```bash
# Salir del servidor
exit
```

Desde tu PC, conectar con el nuevo usuario:

```powershell
ssh -i $HOME\.ssh\fade-hetzner fade@IP_DEL_SERVIDOR
```

Si funciona, **¡perfecto!** ✅

---

## 📊 PANEL DE CONTROL HETZNER

### Opciones útiles del panel:

1. **Graphs**: Ver uso de CPU, RAM, disco, red
2. **Console**: Acceder por navegador (emergencias)
3. **Snapshots**: Crear copias del servidor (3.5€ cada una)
4. **Backups**: Backups automáticos (+20% precio)
5. **Networking**: Ver/cambiar IPs
6. **Rescue**: Modo recuperación si algo sale mal
7. **Power**: Reiniciar, apagar, etc.

---

## 💰 FACTURACIÓN

- **Cobro**: Mensual
- **Método**: Al inicio de cada mes
- **Cancelación**: En cualquier momento
- **Borrado**: Si borras el servidor, solo pagas por las horas usadas

### Ver facturas
1. Panel Hetzner → Tu perfil (arriba derecha)
2. **Billing** → **Invoices**

---

## 🆘 SI ALGO SALE MAL

### No puedo conectar por SSH

**Solución 1**: Usar la consola web de Hetzner
1. Panel → Servers → Tu servidor
2. Click en **"Console"** (arriba derecha)
3. Te abre una terminal en el navegador

**Solución 2**: Modo Rescue
1. Panel → Servers → Tu servidor
2. Click en **"Rescue"**
3. Activar modo rescue
4. **Power** → **Reset**
5. Conectar por SSH (te dará una contraseña temporal)

### Me he quedado sin dinero/saldo

1. Añade saldo en: **Billing** → **Add credit**
2. O añade método de pago automático

### Quiero cancelar/borrar el servidor

1. Panel → Servers → Tu servidor
2. Click en el servidor
3. **Settings** (rueda dentada) → **Delete**
4. Confirmar

**⚠️ IMPORTANTE**: Los datos se borrarán permanentemente

---

## ✅ CHECKLIST - ¿TODO LISTO?

Marca cuando completes cada paso:

- [ ] Cuenta Hetzner creada y verificada
- [ ] Método de pago añadido
- [ ] Proyecto creado
- [ ] Servidor CX21 contratado y corriendo
- [ ] SSH key generada y añadida
- [ ] Primera conexión SSH exitosa
- [ ] Sistema actualizado
- [ ] Usuario `fade` creado
- [ ] Firewall configurado
- [ ] Probada conexión con usuario `fade`
- [ ] IP del servidor anotada

**Cuando todo esté ✅, continuar con: `MIGRACION.md`**

---

## 🎯 PRÓXIMOS PASOS

1. ✅ Servidor contratado y accesible
2. ➡️ **Ejecutar script de setup automático** (`setup-vps.sh`)
3. ➡️ **Desplegar aplicación** (`deploy.sh`)
4. ➡️ Configurar DNS (si tienes dominio)
5. ➡️ Configurar SSL/HTTPS

---

## 📞 SOPORTE HETZNER

- **Web**: https://docs.hetzner.com/
- **Status**: https://status.hetzner.com/
- **Support**: support@hetzner.com (responden en 24-48h)
- **Community**: https://community.hetzner.com/

---

**Fecha**: 2025-10-11  
**Versión**: 1.0.0  
**Coste estimado**: 4.51€/mes + IVA
