"""
Acceso de socios desde la zona privada de fade.es mediante enlace firmado.

La web de fade.es (WordPress) genera un JWT HS256 de corta duración y redirige a
/acceso?token=... (ver especificación entregada a Intermark). Aquí se valida:

- firma con la clave compartida (SOCIOS_JWT_SECRET)
- emisor "fade.es" y audiencia "financiacion.fade.es"
- caducidad, con un margen de 30 s por desfase de relojes
- que el token no dure más de MAX_VIDA_TOKEN (por si el emisor se configura mal)
- que el token no se haya usado antes (jti), con un registro en SQLite
  compartido entre los workers de gunicorn (en /tmp: solo hace falta
  recordar los tokens mientras no caducan)
"""

import os
import sqlite3
import time
import logging

import jwt

logger = logging.getLogger(__name__)

EMISOR = 'fade.es'
AUDIENCIA = 'financiacion.fade.es'
ALGORITMO = 'HS256'
MARGEN_RELOJ = 30          # segundos
MAX_VIDA_TOKEN = 300       # segundos entre iat y exp
LONGITUD_MINIMA_CLAVE = 32


class TokenInvalido(Exception):
    """El token no permite el acceso. El mensaje es para el log, no para el usuario."""


def _ruta_registro(base_dir):
    return os.path.join(base_dir, 'tokens_socios_usados.db')


def _marcar_usado(jti, exp, base_dir):
    """Registra el jti. Devuelve False si ya estaba (token reutilizado)."""
    con = sqlite3.connect(_ruta_registro(base_dir), timeout=10)
    try:
        with con:
            con.execute('CREATE TABLE IF NOT EXISTS usados (jti TEXT PRIMARY KEY, exp INTEGER NOT NULL)')
            # Los caducados ya no pueden reutilizarse: basta con guardar los vigentes
            con.execute('DELETE FROM usados WHERE exp < ?', (int(time.time()) - MARGEN_RELOJ,))
            try:
                con.execute('INSERT INTO usados (jti, exp) VALUES (?, ?)', (jti, int(exp)))
            except sqlite3.IntegrityError:
                return False
        return True
    finally:
        con.close()


def validar_token(token, clave, base_dir):
    """
    Valida el token y devuelve el identificador del socio (claim "sub").
    Lanza TokenInvalido si no es válido.
    """
    if not clave or len(clave) < LONGITUD_MINIMA_CLAVE:
        raise TokenInvalido('SOCIOS_JWT_SECRET no configurada o demasiado corta')
    if not token:
        raise TokenInvalido('falta el token')

    try:
        datos = jwt.decode(
            token,
            clave,
            algorithms=[ALGORITMO],
            audience=AUDIENCIA,
            issuer=EMISOR,
            leeway=MARGEN_RELOJ,
            options={'require': ['iss', 'aud', 'sub', 'iat', 'exp', 'jti']},
        )
    except jwt.ExpiredSignatureError:
        raise TokenInvalido('token caducado')
    except jwt.InvalidTokenError as e:
        raise TokenInvalido(f'token no válido ({type(e).__name__}: {e})')

    socio_id = str(datos['sub']).strip()
    jti = str(datos['jti']).strip()
    if not socio_id or not jti:
        raise TokenInvalido('sub o jti vacíos')
    if datos['exp'] - datos['iat'] > MAX_VIDA_TOKEN:
        raise TokenInvalido(f"vida del token demasiado larga ({datos['exp'] - datos['iat']} s)")

    try:
        nuevo = _marcar_usado(jti, datos['exp'], base_dir)
    except sqlite3.Error as e:
        raise TokenInvalido(f'no se pudo registrar el token en {base_dir}: {e}')
    if not nuevo:
        raise TokenInvalido(f'token reutilizado (jti {jti})')

    return socio_id
