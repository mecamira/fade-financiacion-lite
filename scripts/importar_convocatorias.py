#!/usr/bin/env python3
"""
Da de alta en bloque las convocatorias de un archivo de carga (scripts/cargas/*.json).

Cada convocatoria se guarda con la misma función que usa el botón «Guardar» del editor
(financing_dashboard.agregar_programa): mismo bloqueo del JSON, misma comprobación de
código BDNS duplicado y mismo identificador generado a partir del nombre.

Por defecto NO escribe nada: enseña qué haría. Para guardar de verdad, añade --aplicar.
Antes de escribir hace una copia del JSON junto a él, en data/ (que es el volumen del
contenedor, así que la copia sobrevive a los reinicios).

No da de alta una convocatoria si ya existe otra con el mismo nombre o con uno muy
parecido; así se puede ejecutar dos veces sin duplicar nada.

Uso (dentro del contenedor, para que escriba en el volumen correcto):

    docker compose exec flask-app python scripts/importar_convocatorias.py scripts/cargas/2026-11_convocatorias_abiertas.json
    docker compose exec flask-app python scripts/importar_convocatorias.py scripts/cargas/2026-11_convocatorias_abiertas.json --aplicar
"""

import argparse
import difflib
import json
import os
import shutil
import sys
import unicodedata
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from utils import financing_dashboard  # noqa: E402

JSON_PROGRAMAS = os.path.join(BASE_DIR, 'data', 'programas_financiacion.json')
PARECIDO_MINIMO = 0.85


def _clave(texto):
    """Nombre en minúsculas, sin acentos ni espacios sobrantes, para comparar."""
    t = unicodedata.normalize('NFKD', str(texto or '')).encode('ascii', 'ignore').decode()
    return ' '.join(t.lower().split())


def _nombre(p):
    return p.get('nombre_coloquial') or p.get('nombre') or ''


def _ya_existe(nuevo, existentes):
    """Devuelve la convocatoria existente con el mismo nombre (o casi), o None."""
    clave = _clave(_nombre(nuevo))
    mejor, ratio_mejor = None, 0.0
    for p in existentes:
        for nombre in (_nombre(p), p.get('nombre_oficial')):
            if not nombre:
                continue
            ratio = difflib.SequenceMatcher(None, clave, _clave(nombre)).ratio()
            if ratio > ratio_mejor:
                mejor, ratio_mejor = p, ratio
    return (mejor, ratio_mejor) if ratio_mejor >= PARECIDO_MINIMO else (None, ratio_mejor)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('carga', help='Archivo JSON de carga (con una lista "programas")')
    parser.add_argument('--aplicar', action='store_true', help='Guardar de verdad (sin esto, solo muestra qué haría)')
    args = parser.parse_args()

    with open(args.carga, encoding='utf-8') as f:
        nuevos = json.load(f)['programas']
    with open(JSON_PROGRAMAS, encoding='utf-8') as f:
        existentes = json.load(f)['programas']

    print(f'Archivo de carga: {args.carga} ({len(nuevos)} convocatorias)')
    print(f'Convocatorias actuales en la aplicación: {len(existentes)}')
    print('MODO PRUEBA: no se guarda nada\n' if not args.aplicar else 'GUARDANDO\n')

    pendientes, omitidas = [], []
    for p in nuevos:
        previa, ratio = _ya_existe(p, existentes)
        if previa:
            omitidas.append((p, previa, ratio))
        else:
            pendientes.append(p)

    for p, previa, ratio in omitidas:
        print(f'  = YA EXISTE  {_nombre(p)}\n'
              f'               parecida a «{_nombre(previa)}» (id {previa.get("id")}, {ratio:.0%}): no se da de alta')

    if args.aplicar and pendientes:
        copia = f'{JSON_PROGRAMAS}.antes-carga-{datetime.now():%Y%m%d-%H%M%S}'
        shutil.copy2(JSON_PROGRAMAS, copia)
        print(f'\nCopia de seguridad: {copia}\n')

    creadas, errores = [], []
    for p in pendientes:
        if not args.aplicar:
            print(f'  + SE DARÍA DE ALTA  {_nombre(p)}')
            continue
        try:
            nuevo_id = financing_dashboard.agregar_programa(dict(p))
        except financing_dashboard.ProgramaDuplicado as e:
            errores.append((p, str(e)))
            continue
        if nuevo_id:
            creadas.append(nuevo_id)
            print(f'  + ALTA  {_nombre(p)}\n          /financiacion/programa/{nuevo_id}')
        else:
            errores.append((p, 'agregar_programa no devolvió id (ver el log)'))

    for p, error in errores:
        print(f'  ! ERROR  {_nombre(p)}: {error}')

    print(f'\nResumen: {len(creadas) if args.aplicar else len(pendientes)} '
          f'{"dadas de alta" if args.aplicar else "se darían de alta"}, '
          f'{len(omitidas)} ya existían, {len(errores)} con error.')
    if not args.aplicar and pendientes:
        print('Para guardarlas, repite el comando con --aplicar.')
    return 1 if errores else 0


if __name__ == '__main__':
    sys.exit(main())
