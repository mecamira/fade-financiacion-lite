# -*- coding: utf-8 -*-
"""Recorre la guía como lo haría una persona (teclado) y fotografía cada estado."""
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
RUTA = (AQUI / 'Guia_Usuario_Programas_Financiacion.html').as_uri()
SOLO = {int(x) for x in sys.argv[1:]}      # opcional: solo esas diapositivas
(AQUI / 'qa').mkdir(exist_ok=True)
errores = []

with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome', headless=True)
    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    pg.on('console', lambda m: errores.append(('console', m.type, m.text)) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errores.append(('pageerror', str(e))))
    pg.goto(RUTA)
    pg.wait_for_timeout(900)
    total = pg.evaluate('window.__guia.total')
    n = 0
    for i in range(total):
        if SOLO and (i + 1) not in SOLO:
            continue
        pg.evaluate(f'window.__guia.ir({i}, 0)')
        pg.wait_for_timeout(700)
        pg.screenshot(path=str(AQUI / 'qa' / f's{i + 1:02d}_p00.png')); n += 1
        k = 0
        while k < 30:                       # tope de seguridad
            antes = pg.evaluate('({i: window.__guia.estado.i, p: window.__guia.estado.p})')
            pg.keyboard.press('ArrowRight')
            pg.wait_for_timeout(1500 if k == 0 else 1250)
            est = pg.evaluate('({i: window.__guia.estado.i, p: window.__guia.estado.p})')
            if est['i'] != antes['i'] or est == antes:   # pasó de diapositiva o ya no hay más pasos
                break
            k += 1
            pg.screenshot(path=str(AQUI / 'qa' / f's{i + 1:02d}_p{est["p"]:02d}.png')); n += 1
    print('diapositivas:', total, '· capturas de QA:', n)
    b.close()
print('ERRORES:', errores if errores else 'ninguno')
