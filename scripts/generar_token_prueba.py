"""
Genera un enlace de acceso de socio de prueba, igual que lo haría la web de
fade.es, para comprobar /acceso sin depender de WordPress.

Uso en el servidor (usa SOCIOS_JWT_SECRET del contenedor):
    docker compose exec flask-app python scripts/generar_token_prueba.py [id_socio]

El enlace caduca a los 2 minutos y solo sirve una vez.
"""

import os
import secrets
import sys
import time

import jwt

URL_BASE = os.environ.get('SOCIOS_URL_BASE', 'https://financiacion.fade.es')


def main():
    clave = os.environ.get('SOCIOS_JWT_SECRET', '')
    if not clave:
        sys.exit('SOCIOS_JWT_SECRET no está configurada')

    socio_id = sys.argv[1] if len(sys.argv) > 1 else 'prueba'
    ahora = int(time.time())
    token = jwt.encode({
        'iss': 'fade.es',
        'aud': 'financiacion.fade.es',
        'sub': socio_id,
        'iat': ahora,
        'exp': ahora + 120,
        'jti': secrets.token_hex(16),
    }, clave, algorithm='HS256')
    print(f'{URL_BASE}/acceso?token={token}')


if __name__ == '__main__':
    main()
