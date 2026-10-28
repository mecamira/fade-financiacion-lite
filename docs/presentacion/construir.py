# -*- coding: utf-8 -*-
"""
Construye el HTML único y autocontenido de la guía a partir de:
  capturas/*.webp + regiones.json (capturar.py), guion.py y plantilla.html

Uso:  python construir.py [LOGO.png]
Salida: Guia_Usuario_Programas_Financiacion.html
"""
import base64
import io
import json
import os
import sys

from PIL import Image

import guion

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, 'Guia_Usuario_Programas_Financiacion.html')
LOGO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'logo.png')


def b64(ruta, mime):
    with open(ruta, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def logo_data():
    im = Image.open(LOGO).convert('RGBA')
    im.thumbnail((420, 220))
    buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def main():
    with open(os.path.join(AQUI, 'regiones.json'), encoding='utf-8') as f:
        reg = json.load(f)
    caps = reg['capturas']
    errores, imagenes, slides = [], {}, []

    for n, s in enumerate(guion.SLIDES, 1):
        s = json.loads(json.dumps(s))            # copia
        if s['tipo'] == 'captura':
            frames = []
            for nombre in s['frames']:
                if nombre not in caps:
                    errores.append(f'diapositiva {n}: no existe la captura {nombre!r}'); continue
                c = caps[nombre]
                imagenes.setdefault(nombre, b64(os.path.join(AQUI, 'capturas', nombre + '.webp'), 'image/webp'))
                frames.append({'img': nombre, 'w': c['w'], 'h': c['h'], 'regiones': c['regiones']})
            s['frames'] = frames
            for k, p in enumerate(s['pasos'], 1):
                fi = p.get('frame', 0)
                if fi >= len(frames):
                    errores.append(f'diapositiva {n}, paso {k}: frame {fi} inexistente'); continue
                claves = p['region'] if isinstance(p['region'], list) else [p['region']]
                for c in claves:
                    if c not in frames[fi]['regiones']:
                        errores.append(f'diapositiva {n}, paso {k}: la región {c!r} no existe en {frames[fi]["img"]}')
        slides.append(s)

    if errores:
        print('ERRORES:'); [print('  -', e) for e in errores]; sys.exit(1)

    datos = {'meta': reg['meta'], 'slides': slides, 'imagenes': imagenes, 'logo': logo_data()}
    texto = json.dumps(datos, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    with open(os.path.join(AQUI, 'plantilla.html'), encoding='utf-8') as f:
        html = f.read().replace('__DATOS__', texto)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'{len(slides)} diapositivas · {len(imagenes)} imágenes · {os.path.getsize(SALIDA) / 1024 / 1024:.1f} MB -> {os.path.basename(SALIDA)}')


if __name__ == '__main__':
    main()
