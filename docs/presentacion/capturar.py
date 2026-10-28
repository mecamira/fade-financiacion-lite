"""
Captura las pantallas de la guía de usuario desde el sitio en producción.

Para cada captura guarda la imagen (WebP) y las regiones que se resaltarán,
calculadas del DOM real, de modo que las indicaciones encajan al píxel y se
pueden regenerar cuando cambien los datos o el diseño.

Uso:  python capturar.py [URL_BASE]
Requiere: pip install playwright pillow   (usa el Chrome ya instalado)
"""
import io
import json
import os
import sys
import time
from datetime import datetime

import requests
from PIL import Image
from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://178.105.160.148').rstrip('/')
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, 'capturas')
os.makedirs(OUT, exist_ok=True)

ANCHO, ALTO, ESCALA = 1440, 900, 1.5
CALIDAD_WEBP = 80

# Solo para las capturas: oculta el enlace de acceso de administración (la guía es
# para personas usuarias) y las transiciones, para fotografiar estados ya asentados.
CSS = """
html { scroll-behavior: auto !important; }
a.nav-link[href*="/admin/login"], a[href*="/admin/login"].nav-link { display: none !important; }
.fade, .modal.fade .modal-dialog, .collapsing { transition: none !important; }
.programa-card, .card-hover-lift { transition: none !important; }
"""

REGIONES = {}
AVISOS = []


# ---------------------------------------------------------------- utilidades
def _union(boxes):
    x1 = min(b['x'] for b in boxes); y1 = min(b['y'] for b in boxes)
    x2 = max(b['x'] + b['width'] for b in boxes); y2 = max(b['y'] + b['height'] for b in boxes)
    return {'x': x1, 'y': y1, 'w': x2 - x1, 'h': y2 - y1}


def caja(pg, spec, vp):
    """Rectángulo (coordenadas de la ventana) de un selector o de la unión de varios."""
    d = {'sel': spec} if isinstance(spec, str) else dict(spec)
    loc = pg.locator(d['sel'])
    total = loc.count()
    idx = [d['nth']] if d.get('nth') is not None else range(min(total, 60))
    boxes = []
    for i in idx:
        if i >= total:
            continue
        try:
            b = loc.nth(i).bounding_box()
        except Exception:
            b = None
        if not b or b['width'] <= 0 or b['height'] <= 0:
            continue
        # ignorar los elementos que quedan fuera de la ventana visible
        if b['y'] + b['height'] < 0 or b['y'] > vp['height'] or b['x'] + b['width'] < 0 or b['x'] > vp['width']:
            continue
        boxes.append(b)
    if not boxes:
        return None
    u = _union(boxes)
    p = d.get('pad', 0)
    return {'x': u['x'] - p, 'y': u['y'] - p, 'w': u['w'] + 2 * p, 'h': u['h'] + 2 * p}


def abrir(pg, ruta, esperar='.programa-card'):
    pg.goto(BASE + ruta, wait_until='networkidle')
    pg.add_style_tag(content=CSS)
    if esperar:
        pg.wait_for_selector(esperar, timeout=20000)
    pg.wait_for_timeout(600)


def ir_a(pg, sel, arriba=90):
    """Desplaza la página para que el elemento quede `arriba` px bajo el borde superior."""
    loc = pg.locator(sel)
    if loc.count() == 0:
        AVISOS.append(f'ir_a: no se encontró {sel!r}')
        return
    # Dos pasadas: al primer desplazamiento el menú pasa de 'relative' a fijo, deja de
    # ocupar espacio y el contenido sube; la segunda corrige con el diseño ya asentado.
    for _ in range(2):
        loc.first.evaluate("(e, arriba) => window.scrollTo({top: e.getBoundingClientRect().top + window.scrollY - arriba, behavior: 'instant'})", arriba)
        pg.wait_for_timeout(220)


def foto(pg, nombre, regiones=None, clip=None, pad_clip=0):
    """
    Guarda la captura `nombre` y las regiones indicadas.
    clip: None = ventana completa · dict(x,y,w,h) · selector (se recorta a ese elemento + pad_clip)
    """
    vp = pg.viewport_size
    if clip is None:
        c = {'x': 0, 'y': 0, 'w': vp['width'], 'h': vp['height']}
    elif isinstance(clip, dict) and 'x' in clip:
        c = dict(clip)
    else:
        b = caja(pg, clip, vp)
        if b is None:
            AVISOS.append(f'{nombre}: no se encontró el recorte {clip!r}')
            c = {'x': 0, 'y': 0, 'w': vp['width'], 'h': vp['height']}
        else:
            c = {'x': b['x'] - pad_clip, 'y': b['y'] - pad_clip, 'w': b['w'] + 2 * pad_clip, 'h': b['h'] + 2 * pad_clip}
    # ajustar a la ventana
    x1, y1 = max(0, c['x']), max(0, c['y'])
    x2, y2 = min(vp['width'], c['x'] + c['w']), min(vp['height'], c['y'] + c['h'])
    c = {'x': x1, 'y': y1, 'w': x2 - x1, 'h': y2 - y1}

    png = pg.screenshot(clip={'x': c['x'], 'y': c['y'], 'width': c['w'], 'height': c['h']})
    im = Image.open(io.BytesIO(png)).convert('RGB')
    ruta = os.path.join(OUT, nombre + '.webp')
    im.save(ruta, 'WEBP', quality=CALIDAD_WEBP, method=6)

    regs = {}
    for clave, spec in (regiones or {}).items():
        b = caja(pg, spec, vp)
        if b is None:
            AVISOS.append(f'{nombre}.{clave}: no encontrado')
            continue
        # recortar la región al área de la captura
        rx1, ry1 = max(b['x'], c['x']), max(b['y'], c['y'])
        rx2, ry2 = min(b['x'] + b['w'], c['x'] + c['w']), min(b['y'] + b['h'], c['y'] + c['h'])
        if rx2 - rx1 < 4 or ry2 - ry1 < 4:
            AVISOS.append(f'{nombre}.{clave}: fuera de la captura')
            continue
        regs[clave] = [round((rx1 - c['x']) / c['w'], 4), round((ry1 - c['y']) / c['h'], 4),
                       round((rx2 - rx1) / c['w'], 4), round((ry2 - ry1) / c['h'], 4)]
    REGIONES[nombre] = {'w': im.width, 'h': im.height, 'kb': round(os.path.getsize(ruta) / 1024), 'regiones': regs}
    print(f'  {nombre:16} {im.width}x{im.height}  {REGIONES[nombre]["kb"]:4} KB  regiones: {len(regs)}/{len(regiones or {})}')


def h(texto, anc='card'):
    """Bloque (tarjeta) de la ficha que contiene el encabezado con ese texto."""
    return (f'xpath=(//h1|//h2|//h3|//h4|//h5|//h6)[starts-with(normalize-space(.), "{texto}")][1]'
            f'/ancestor::div[contains(concat(" ", normalize-space(@class), " "), " {anc} ")][1]')


def etiqueta_tarjeta_limpia(pg):
    """Marca con data-guia la tarjeta del dashboard que mejor se ve en una captura."""
    return pg.evaluate("""() => {
      const cards = [...document.querySelectorAll('.programa-card')];
      let best = null, bestScore = -1e9;
      cards.forEach(c => {
        const r = c.getBoundingClientRect(); if (!r.width) return;
        const txt = s => (c.querySelector(s)?.innerText || '').trim();
        const fecha = txt('.programa-fecha'), inten = txt('.programa-intensidad'), res = txt('.programa-resumen');
        const ben = c.querySelectorAll('.programa-beneficiarios .badge').length;
        const bd = c.querySelector('.programa-fecha-bdns-container');
        const abierta = /d[ií]as?\\b/i.test(fecha) && !/cerrada/i.test(fecha) ? 1 : 0;
        const score = abierta * 4 + (bd && bd.style.display !== 'none' ? 2 : 0) + (ben > 0 ? 1 : 0)
          + (inten && inten.length < 110 ? 2 : -2) + (res.length > 40 && res.length < 260 ? 1 : 0)
          + (c.querySelector('.programa-importe') && !/No especificado/.test(txt('.programa-importe')) ? 1 : 0)
          - r.height / 1500;
        if (score > bestScore) { bestScore = score; best = c; }
      });
      if (!best) return null;
      best.setAttribute('data-guia', '1');
      return {nombre: best.querySelector('.programa-nombre').innerText, href: best.querySelector('.programa-detalle').getAttribute('href')};
    }""")


# ---------------------------------------------------------------- escenas
def escena_dashboard(ctx):
    pg = ctx.new_page(); pg.set_viewport_size({'width': ANCHO, 'height': ALTO})
    abrir(pg, '/financiacion/dashboard')
    pg.evaluate("window.scrollTo({top:0, behavior:'instant'})"); pg.wait_for_timeout(300)
    foto(pg, 'dash_general', {
        'nav': '#mainNavbar', 'kpis': '.kpi-card', 'buscar': '#search',
        'filtros': '.col-md-3 > .card', 'pestanas': '#view-tabs',
        'barra': '#export-excel, #dropdownSortButton', 'tarjetas': {'sel': '.programa-card', 'nth': 0},
        'tarjetas2': '.programa-card'})
    kpis = pg.evaluate("() => [...document.querySelectorAll('.kpi-card-value')].map(e => e.innerText)")

    # ---- tarjeta "limpia" a tamaño grande
    pg.set_viewport_size({'width': ANCHO, 'height': 1250})
    info = etiqueta_tarjeta_limpia(pg)
    ir_a(pg, '[data-guia]', 80)
    foto(pg, 'tarjeta', {
        'estado': '[data-guia] .card-header span.badge:not(.programa-fecha-bdns-badge)',
        'bdns_fecha': '[data-guia] .programa-fecha-bdns-badge', 'comparar': '[data-guia] .card-header .form-check',
        'titulo': '[data-guia] .programa-nombre', 'organismo': '[data-guia] .programa-organismo',
        'resumen': '[data-guia] .programa-resumen', 'cierre': '[data-guia] .programa-fecha',
        'codigo': {'sel': '[data-guia] .card-body > div.mt-2'},
        'ayuda_ambito': {'sel': '[data-guia] .programa-tipo-ayuda, [data-guia] .programa-ambito', 'pad': 24},
        'presupuesto': '[data-guia] .programa-importe', 'intensidad': '[data-guia] .programa-intensidad',
        'beneficiarios': '[data-guia] .programa-beneficiarios', 'botones': '[data-guia] .card-footer'},
        clip={'sel': '[data-guia]'}, pad_clip=14)
    pg.set_viewport_size({'width': ANCHO, 'height': ALTO})

    # ---- filtros acumulables
    pg.evaluate('window.scrollTo(0,0)'); ir_a(pg, '.col-md-3 > .card', 80)
    R0 = {'buscar': '#search', 'selector': '#filter-type-select', 'aplicar': '#filter-form button[type=submit]',
          'filtros': '.col-md-3 > .card', 'tarjetas': {'sel': '.programa-card', 'nth': 0}}
    foto(pg, 'filtros_0', R0)
    pg.select_option('#filter-type-select', 'beneficiario'); pg.wait_for_timeout(500)
    foto(pg, 'filtros_1', {'selector': '#filter-type-select', 'lista': '#filter-value-container',
                           'buscador': '#fv-select-search', 'anadir': '#fv-add-btn'})
    pg.select_option('#fv-select', label='PYME'); pg.click('#fv-add-btn'); pg.wait_for_timeout(1500)
    ir_a(pg, '.col-md-3 > .card', 80)
    foto(pg, 'filtros_2', {'etiqueta': '#active-filters-tags .filter-tag', 'area': '#active-filters-area',
                           'tarjetas': '.programa-card', 'selector': '#filter-type-select'})
    pg.select_option('#filter-type-select', 'estado'); pg.wait_for_timeout(500)
    pg.select_option('#fv-select', label='Abierta'); pg.click('#fv-add-btn'); pg.wait_for_timeout(1500)
    ir_a(pg, '.col-md-3 > .card', 80)
    foto(pg, 'filtros_3', {'etiquetas': '#active-filters-tags .filter-tag', 'quitar': '#active-filters-tags .filter-tag-remove',
                           'limpiar': '#reset-filters', 'tarjetas': '.programa-card'})

    # ---- ordenar
    abrir(pg, '/financiacion/dashboard'); ir_a(pg, '#view-tabs', 70)
    pg.click('#dropdownSortButton'); pg.wait_for_timeout(400)
    foto(pg, 'orden_0', {'boton': '#dropdownSortButton', 'menu': '.dropdown-menu.show',
                         'op_cierre': '.sort-option[data-sort="fecha_cierre"]',
                         'op_bdns': '.sort-option[data-sort="fecha_publicacion_bdns"]'})
    pg.click('.sort-option[data-sort="fecha_publicacion_bdns"]'); pg.wait_for_timeout(900)
    ir_a(pg, '#view-tabs', 70)
    foto(pg, 'orden_1', {'boton': '#dropdownSortButton', 'fechas': '.programa-fecha-bdns-badge'})

    # ---- comparar
    abrir(pg, '/financiacion/dashboard'); ir_a(pg, '#view-tabs', 70)
    pg.locator('.programa-comparar').nth(0).check(); pg.locator('.programa-comparar').nth(1).check(); pg.wait_for_timeout(500)
    foto(pg, 'comparar_0', {'casillas': '.programa-comparar', 'barra': '#compare-bar', 'chips': '#compare-preview',
                            'boton': '#compare-button', 'limpiar': '#compare-clear'})
    pg.click('#compare-button'); pg.wait_for_selector('#compare-modal.show'); pg.wait_for_timeout(600)
    foto(pg, 'comparar_1', {'modal': '#compare-modal .modal-content', 'cabecera': '#compare-table thead',
                            'tabla': '#compare-table'})

    # ---- vista previa
    abrir(pg, '/financiacion/dashboard'); info = etiqueta_tarjeta_limpia(pg) or info
    ir_a(pg, '[data-guia]', 120)
    pg.locator('[data-guia] .programa-preview').click(); pg.wait_for_selector('#preview-modal.show'); pg.wait_for_timeout(500)
    foto(pg, 'preview', {'modal': '#preview-modal .modal-content'})

    # ---- estadísticas
    abrir(pg, '/financiacion/dashboard'); pg.click('#visualizations-tab'); pg.wait_for_timeout(2500)
    ir_a(pg, '#stats-kpi-row', 80)
    foto(pg, 'stats_0', {'kpis': '#stats-kpi-row', 'estado': h('Estado de convocatorias'), 'tipo': h('Tipo de ayuda')})
    ir_a(pg, h('Distribución por Organismo'), 80)
    pg.wait_for_timeout(500)
    foto(pg, 'stats_1', {'organismo': h('Distribución por Organismo'), 'ambito': h('Ámbito geográfico')})
    ir_a(pg, h('Cronograma'), 80)
    pg.wait_for_timeout(500)
    foto(pg, 'stats_2', {'cronograma': h('Cronograma')})
    ir_a(pg, h('Distribución por Sector'), 80)
    pg.wait_for_timeout(500)
    foto(pg, 'stats_3', {'sector': h('Distribución por Sector'), 'beneficiarios': h('Beneficiarios más frecuentes')})
    pg.close()
    return info, kpis


def escena_listado(ctx):
    pg = ctx.new_page(); pg.set_viewport_size({'width': 1600, 'height': ALTO})
    abrir(pg, '/financiacion/dashboard'); pg.click('#listado-tab'); pg.wait_for_timeout(700)
    ir_a(pg, '#view-tabs', 70)
    foto(pg, 'listado_0', {'estado': '#listado-table thead th:nth-child(1)', 'cabecera': '#listado-table thead',
                           'orden': '.listado-th-sort[data-col="fecha_cierre"]',
                           'filas': '#listado-tbody tr:nth-child(-n+4)', 'excel': '#listado-export'})
    pg.evaluate("document.getElementById('listado-table-wrap').scrollLeft = 99999"); pg.wait_for_timeout(400)
    foto(pg, 'listado_1', {'presupuesto': '.listado-th-sort[data-col="importe_maximo"]',
                           'acciones': '#listado-tbody tr:nth-child(-n+4) td:last-child',
                           'ojo': '#listado-tbody .listado-preview-btn', 'comparar': '#listado-tbody .listado-comparar-cb',
                           'cierre': '.listado-th-sort[data-col="fecha_cierre"]'})
    pg.close()


def escena_ficha(ctx, href):
    pg = ctx.new_page(); pg.set_viewport_size({'width': ANCHO, 'height': ALTO})
    abrir(pg, href, esperar='.card-header-gradient')
    foto(pg, 'ficha_0', {'volver': 'a.btn:has-text("Volver al Dashboard") >> nth=0', 'cabecera': '.card-header-gradient',
                         'resumen': h('Resumen', 'card-section'), 'basica': h('Información Básica')})
    ir_a(pg, h('Fechas de la Convocatoria'), 80)
    foto(pg, 'ficha_1', {'fechas': h('Fechas de la Convocatoria'), 'financiera': h('Información Financiera'),
                         'intensidad': 'xpath=//*[contains(normalize-space(.),"Intensidad de Financiación")][last()]/ancestor::div[contains(@class,"border-start") or contains(@class,"financial") or contains(@class,"col-md-6")][1]',
                         'presupuesto': 'xpath=//*[contains(normalize-space(.),"Presupuesto Total de la Convocatoria")][last()]/ancestor::div[contains(@class,"col-md-6")][1]'})
    ir_a(pg, h('Beneficiarios Elegibles'), 80)
    foto(pg, 'ficha_2', {'beneficiarios': h('Beneficiarios Elegibles'), 'sectores': h('Sectores Aplicables'),
                         'proyectos': h('Tipos de Proyecto Financiables'), 'requisitos': h('Requisitos')})
    ir_a(pg, h('Requisitos'), 80)
    foto(pg, 'ficha_3', {'requisitos': h('Requisitos'), 'gastos': h('Gastos Subvencionables'), 'enlaces': h('Enlaces'),
                         'bdns': 'a.btn:has-text("Página BDNS")'})
    pg.close()


def escena_resuelta(ctx):
    progs = requests.get(BASE + '/api/programas-financiacion', timeout=30).json()['programas']
    cand = [p for p in progs if p.get('resuelta') and len(p.get('concesiones') or []) >= 5
            and ((p.get('financiacion') or {}).get('presupuesto_total'))]
    cand.sort(key=lambda p: len(p['concesiones']))
    if not cand:
        AVISOS.append('resuelta: no hay convocatorias resueltas con concesiones y presupuesto'); return None
    p = cand[0]
    nombre = p.get('nombre_coloquial') or p.get('nombre')
    pg = ctx.new_page(); pg.set_viewport_size({'width': ANCHO, 'height': 1000})
    abrir(pg, '/financiacion/dashboard')
    pg.fill('#search', nombre[:28]); pg.click('#filter-form button[type=submit]'); pg.wait_for_timeout(1500)
    ir_a(pg, '.programa-card', 90)
    foto(pg, 'resuelta_0', {'insignia': '.programa-card .card-header span.badge.bg-dark', 'tarjeta': '.programa-card'},
         clip={'sel': '.programa-card'}, pad_clip=16)
    pg.set_viewport_size({'width': ANCHO, 'height': ALTO})
    abrir(pg, f"/financiacion/programa/{p['id']}", esperar='.card-header-gradient')
    ir_a(pg, 'div.card.border-dark', 80)
    foto(pg, 'resuelta_1', {'titulo': 'div.card.border-dark .card-header', 'total': 'div.card.border-dark .bg-light',
                            'barra': 'div.card.border-dark .progress', 'tabla': 'div.card.border-dark table'})
    pg.close()
    return {'nombre': nombre, 'concesiones': len(p['concesiones'])}


def escena_busca(ctx):
    pg = ctx.new_page(); pg.set_viewport_size({'width': ANCHO, 'height': ALTO})
    abrir(pg, '/financiacion/busca-tu-convocatoria', esperar='#form-busca'); pg.evaluate('window.scrollTo(0,0)')
    foto(pg, 'bc_0', {'titulo': 'h1:has-text("Busca tu convocatoria")', 'perfiles': '.bc-perfil', 'pregunta1': h('1¿Quién eres?', 'card')})
    pg.locator('label[for="entidad-pyme"]').click(); pg.wait_for_timeout(300)
    pg.evaluate('window.scrollTo(0, 120)'); pg.wait_for_timeout(300)
    foto(pg, 'bc_1', {'elegida': 'label[for="entidad-pyme"]', 'perfiles': '.bc-perfil',
                      'sector': 'xpath=//h5[contains(.,"¿En qué sector trabajas?")]/ancestor::div[contains(@class,"card")][1]'})
    pg.locator('label[for="gasto-personal"]').click()
    pg.locator('label[for="presupuesto-10-50k"]').click(); pg.wait_for_timeout(300)
    ir_a(pg, 'xpath=//h5[contains(.,"¿Qué quieres financiar?")]/ancestor::div[contains(@class,"card")][1]', 80)
    foto(pg, 'bc_2', {'financiar': 'xpath=//h5[contains(.,"¿Qué quieres financiar?")]/ancestor::div[contains(@class,"card")][1]',
                      'gasto': 'label[for="gasto-personal"]',
                      'presupuesto': 'xpath=//h5[contains(.,"presupuesto de tu proyecto")]/ancestor::div[contains(@class,"card")][1]',
                      'presu_elegido': 'label[for="presupuesto-10-50k"]'})
    pg.locator('label[for="plazo-ya"]').click(); pg.wait_for_timeout(300)
    ir_a(pg, 'xpath=//h5[contains(.,"¿Dónde?")]/ancestor::div[contains(@class,"card")][1]', 80)
    foto(pg, 'bc_3', {'donde': 'xpath=//h5[contains(.,"¿Dónde?")]/ancestor::div[contains(@class,"card")][1]',
                      'cuando': 'xpath=//h5[contains(.,"¿Cuándo lo necesitas?")]/ancestor::div[contains(@class,"card")][1]',
                      'buscar': 'button[name="buscar"]', 'limpiar': 'a.btn:has-text("Limpiar")'})
    pg.locator('button[name="buscar"]').click(); pg.wait_for_load_state('networkidle'); pg.add_style_tag(content=CSS)
    pg.wait_for_selector('#resultados'); pg.wait_for_timeout(500)
    ir_a(pg, '#resultados .alert-primary', 80)
    foto(pg, 'res_0', {'resumen': '#resultados .alert-primary', 'pestanas': '#bc-tabs',
                       'tarjetas': '.tab-pane.active .bc-resultado-card'})
    # tarjeta con ayuda orientativa (o la primera)
    idx = pg.evaluate("""() => { const c = [...document.querySelectorAll('.tab-pane.active .bc-resultado-card')];
        let i = c.findIndex(x => x.querySelector('.bc-ayuda')); return i < 0 ? 0 : i; }""")
    base = f'.tab-pane.active .bc-resultado-card >> nth={idx}'
    S = lambda extra: f'{base} >> {extra}'
    pg.set_viewport_size({'width': ANCHO, 'height': 1100})
    for _ in range(2):
        pg.evaluate(f"""() => {{ const c = [...document.querySelectorAll('.tab-pane.active .bc-resultado-card')][{idx}];
            window.scrollTo({{top: c.getBoundingClientRect().top + window.scrollY - 80, behavior: 'instant'}}); }}""")
        pg.wait_for_timeout(220)
    foto(pg, 'res_1', {'estado': S('.badge'), 'afinidad': S('.bc-afinidad'), 'titulo': S('.bc-nombre'),
                       'chips': S('.bc-chip'), 'ayuda': S('.bc-ayuda'), 'motivos': S('.bc-motivos li.ok'),
                       'avisos': S('.bc-motivos li.aviso'), 'ficha': S('a.btn')},
         clip={'sel': base}, pad_clip=16)
    pg.set_viewport_size({'width': ANCHO, 'height': ALTO})
    # otras pestañas
    for etiqueta, nombre in (('Revisa las bases', 'res_2'), ('Financian otros gastos', 'res_3')):
        t = pg.locator(f'#bc-tabs button:has-text("{etiqueta}")')
        if t.count() == 0:
            AVISOS.append(f'{nombre}: no hay pestaña "{etiqueta}" con estos datos'); continue
        t.first.click(); pg.wait_for_timeout(500)
        ir_a(pg, '#bc-tabs', 80)
        foto(pg, nombre, {'pestanas': '#bc-tabs', 'activa': '#bc-tabs .nav-link.active',
                          'nota': '.tab-pane.active > p', 'tarjetas': '.tab-pane.active .bc-resultado-card',
                          'avisos': '.tab-pane.active .bc-motivos li.aviso'})
    pg.close()


def main():
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True)
        ctx = b.new_context(viewport={'width': ANCHO, 'height': ALTO}, device_scale_factor=ESCALA,
                            locale='es-ES', timezone_id='Europe/Madrid')
        print('Dashboard …'); info, kpis = escena_dashboard(ctx)
        print('Listado …'); escena_listado(ctx)
        print('Ficha …'); escena_ficha(ctx, info['href'])
        print('Resuelta …'); resuelta = escena_resuelta(ctx)
        print('Busca tu convocatoria …'); escena_busca(ctx)
        b.close()
    meta = {'fecha': datetime.now().strftime('%d/%m/%Y'), 'base': BASE, 'tarjeta_ejemplo': info['nombre'],
            'kpis': kpis, 'resuelta': resuelta, 'escala': ESCALA, 'ancho': ANCHO, 'alto': ALTO}
    with open(os.path.join(AQUI, 'regiones.json'), 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'capturas': REGIONES}, f, ensure_ascii=False, indent=1)
    total = sum(v['kb'] for v in REGIONES.values())
    print(f'\n{len(REGIONES)} capturas · {total} KB · {time.time() - t0:.0f} s')
    if AVISOS:
        print('\nAVISOS:'); [print('  -', a) for a in AVISOS]


if __name__ == '__main__':
    main()
