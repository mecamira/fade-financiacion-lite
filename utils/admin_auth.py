"""
Autenticación de administradores.

Sustituye la contraseña única en texto plano por usuarios individuales
con contraseña hasheada (werkzeug/scrypt) y protección básica contra
fuerza bruta (bloqueo temporal tras varios intentos fallidos).

Los usuarios se guardan en data/admin_users.json (fuera de git, igual que
el resto de datos de la app). Para crear o cambiar un usuario, usar:

    docker compose exec flask-app python scripts/crear_admin_user.py
"""

import json
import os
import time
import threading
import logging

from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

_lock = threading.Lock()

# Rate limiting (protección básica contra fuerza bruta)
MAX_INTENTOS = 5
VENTANA_SEGUNDOS = 15 * 60      # 15 minutos
BLOQUEO_SEGUNDOS = 15 * 60      # 15 minutos de bloqueo tras agotar intentos


def _base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _users_path():
    return os.environ.get(
        'ADMIN_USERS_PATH',
        os.path.join(_base_dir(), 'data', 'admin_users.json')
    )


def _attempts_path():
    return os.environ.get(
        'ADMIN_ATTEMPTS_PATH',
        os.path.join(_base_dir(), 'data', 'login_attempts.json')
    )


# ============================================================================
# GESTIÓN DE USUARIOS
# ============================================================================

def load_users():
    """Devuelve {username_lower: {'password_hash':..., 'nombre':...}}"""
    path = _users_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error leyendo {path}: {e}")
        return {}


def save_user(username, password, nombre=None):
    """Crea o actualiza un usuario admin con contraseña hasheada."""
    if not username or not password:
        raise ValueError("Usuario y contraseña son obligatorios")
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")

    username_key = username.strip().lower()
    path = _users_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with _lock:
        users = load_users()
        users[username_key] = {
            'password_hash': generate_password_hash(password),
            'nombre': nombre or username,
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    logger.info(f"Usuario admin creado/actualizado: {username_key}")
    return True


def delete_user(username):
    username_key = username.strip().lower()
    with _lock:
        users = load_users()
        if username_key in users:
            del users[username_key]
            with open(_users_path(), 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            return True
    return False


def verify_credentials(username, password):
    """Devuelve el nombre del usuario si las credenciales son correctas, o None."""
    if not username or not password:
        return None
    users = load_users()
    user = users.get(username.strip().lower())
    if not user:
        # Ejecutar el hash igualmente para no filtrar por timing si el usuario existe o no
        generate_password_hash(password)
        return None
    if check_password_hash(user['password_hash'], password):
        return user.get('nombre', username)
    return None


def hay_usuarios_configurados():
    return len(load_users()) > 0


# ============================================================================
# RATE LIMITING (protección básica contra fuerza bruta)
# ============================================================================

def _load_attempts():
    path = _attempts_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save_attempts(data):
    path = _attempts_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Error guardando intentos de login: {e}")


def comprobar_bloqueo(ip):
    """Devuelve segundos restantes de bloqueo (0 si no está bloqueada)."""
    with _lock:
        data = _load_attempts()
        entry = data.get(ip)
        if not entry:
            return 0
        bloqueado_hasta = entry.get('bloqueado_hasta', 0)
        restante = bloqueado_hasta - time.time()
        return max(0, int(restante))


def registrar_intento_fallido(ip):
    """Registra un intento fallido; bloquea la IP si supera el máximo."""
    with _lock:
        data = _load_attempts()
        ahora = time.time()
        entry = data.get(ip, {'intentos': [], 'bloqueado_hasta': 0})

        # Descartar intentos fuera de la ventana temporal
        entry['intentos'] = [t for t in entry['intentos'] if ahora - t < VENTANA_SEGUNDOS]
        entry['intentos'].append(ahora)

        if len(entry['intentos']) >= MAX_INTENTOS:
            entry['bloqueado_hasta'] = ahora + BLOQUEO_SEGUNDOS
            entry['intentos'] = []
            logger.warning(f"IP bloqueada por exceso de intentos de login: {ip}")

        data[ip] = entry
        _save_attempts(data)


def limpiar_intentos(ip):
    """Limpia el historial de intentos tras un login correcto."""
    with _lock:
        data = _load_attempts()
        if ip in data:
            del data[ip]
            _save_attempts(data)
