# Puesta en producción: financiacion.fade.es con HTTPS y acceso de socios

Guía paso a paso para pasar la herramienta de `http://178.105.160.148` a
`https://financiacion.fade.es`, accesible solo para socios desde la zona privada
de fade.es.

Cada paso se puede hacer en un día distinto. Hasta el paso 6, los socios no
notan nada: la herramienta sigue abierta como ahora.

| Quién | Qué |
|---|---|
| Jorge | Registro DNS de `financiacion.fade.es` |
| Intermark (Eva) | Redirección con token firmado en la zona privada (WordPress) |
| Nosotros | Pasos de esta guía |

Todos los comandos se ejecutan en el servidor, dentro de la carpeta del proyecto:

```bash
ssh fadeadmin@178.105.160.148
cd ~/fade-financiacion-lite
```

---

## Paso 1 — Panel de Hetzner (sin consola)

En https://console.hetzner.cloud, entra en el proyecto y luego en el servidor:

1. **Backups**: actívalos (cuestan un 20 % del precio del servidor). Hetzner
   guarda 7 copias diarias del servidor completo.
2. **Firewalls** → *Create Firewall* con estas reglas de entrada (Inbound), y
   aplícalo al servidor:
   - TCP 22 (SSH)
   - TCP 80 (HTTP)
   - TCP 443 (HTTPS)
   - ICMP (opcional, para hacer ping)

## Paso 2 — Desplegar la nueva versión

```bash
git pull
bash scripts/deploy.sh
```

Qué cambia:

- La app ya solo escucha en `127.0.0.1:8000`, así que `http://IP:8000` deja de
  funcionar. Se sigue entrando por `http://178.105.160.148` (puerto 80, nginx).
- La ruta `/acceso` ya existe, pero el acceso sigue abierto
  (`SOCIOS_ACCESO_OBLIGATORIO` no está activado).

## Paso 3 — HTTPS (cuando Jorge confirme el DNS)

Comprueba que el DNS ya funciona en
https://toolbox.googleapps.com/apps/dig/#A/financiacion.fade.es: tiene que
salir `178.105.160.148`. Después:

```bash
sudo bash scripts/configurar-https.sh correo@fade.es
```

El correo recibe los avisos de Let's Encrypt si una renovación fallara. El script:

1. comprueba que el dominio apunta a este servidor y que la app responde;
2. hace una copia de la configuración de nginx en `/root/nginx-backup-FECHA`;
3. obtiene el certificado y activa `nginx/fade-financiacion.conf`. A partir de
   aquí `http://` y la IP redirigen a `https://financiacion.fade.es`;
4. prueba la renovación automática (cada 60 días, sin hacer nada);
5. activa la cookie de sesión segura (`SESSION_COOKIE_SECURE=1` en `.env`).

**Comprobar:** abre https://financiacion.fade.es y comprueba que sale el candado
y que el login de admin funciona en https://financiacion.fade.es/admin/login.

**Si algo va mal:** el script se para y explica el motivo. Para volver a la
configuración anterior de nginx:

```bash
sudo cp -a /root/nginx-backup-FECHA/sites-available/. /etc/nginx/sites-available/
sudo rm /etc/nginx/sites-enabled/*
sudo cp -a /root/nginx-backup-FECHA/sites-enabled/. /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Paso 4 — Clave secreta compartida con fade.es

1. Genera la clave:

   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

2. Añádela a `.env` (con `nano .env`):

   ```
   SOCIOS_JWT_SECRET=la-clave-generada
   ```

3. Reinicia la app para que la lea:

   ```bash
   docker compose up -d --force-recreate flask-app
   ```

4. Pásasela a Intermark **por un canal seguro**: por teléfono, o con un enlace de
   un solo uso. **Nunca por email ni por chat.** La guardarán en `wp-config.php`.

## Paso 5 — Pruebas (el acceso sigue abierto)

**Nuestra prueba**, sin depender de WordPress. Genera un enlace como el que
generará fade.es:

```bash
docker compose exec flask-app python scripts/generar_token_prueba.py prueba
```

Abre el enlace en una ventana privada del navegador antes de 2 minutos: entra al
dashboard. Si lo abres otra vez, te lleva a fade.es/login, porque el enlace
solo sirve una vez.

**Prueba con Intermark**: que pongan el código de la especificación en una
página privada **de prueba** (no en la del Buscador todavía) y que un socio de
prueba la abra. En los logs debe aparecer el acceso:

```bash
docker compose logs flask-app --tail=50 | grep "socio"
```

- `Acceso de socio — id: 123` significa que funciona.
- `Acceso de socio rechazado — <motivo>` indica qué falla: clave distinta,
  caducado, campos que faltan…

## Paso 6 — Lanzamiento

Coordinado con Intermark, el mismo día:

1. **Nosotros**: en `.env`, añadir `SOCIOS_ACCESO_OBLIGATORIO=1` y reiniciar:

   ```bash
   docker compose up -d --force-recreate flask-app
   ```

2. **Intermark**: en `/zona-privada/buscador-de-subvenciones/`, quitar el iframe de
   Power BI y activar la redirección.

**Comprobar:**

- [ ] Un socio pulsa "Buscador de subvenciones" en la zona privada y entra directamente.
- [ ] Sin sesión en fade.es, la página de la zona privada sigue dando 404 o login, como ahora.
- [ ] https://financiacion.fade.es abierto directamente (en ventana privada) redirige a fade.es/login.
- [ ] El login de admin sigue funcionando en https://financiacion.fade.es/admin/login.

**Volver atrás**: poner `SOCIOS_ACCESO_OBLIGATORIO=0` y reiniciar (la herramienta
vuelve a quedar abierta), y que Intermark restaure el iframe si hiciera falta.

---

## Referencia: variables de `.env`

| Variable | Valor | Para qué |
|---|---|---|
| `SESSION_COOKIE_SECURE` | `1` | La cookie de sesión solo viaja por HTTPS. La pone el script del paso 3. |
| `SOCIOS_JWT_SECRET` | clave | Clave compartida con fade.es para validar los enlaces. |
| `SOCIOS_ACCESO_OBLIGATORIO` | `0` / `1` | `1` = solo socios (vía zona privada) y admins. |
| `SOCIOS_LOGIN_URL` | opcional | Adónde se envía a quien no tiene acceso (por defecto `https://fade.es/login/`). |

La sesión del socio dura 12 horas. Después vuelve a entrar desde la zona privada.
