"""
Recomendador de convocatorias ("Busca tu convocatoria").

Motor determinista basado en reglas sobre los datos que ya tienen las
convocatorias (beneficiarios, sectores, gastos subvencionables, tipo de
proyecto, ámbito, fechas e importes).
No usa IA ni red: la misma entrada da siempre el mismo resultado, y no
depende de cuotas externas.

Es una primera guía orientativa: no sustituye a leer las bases de cada
convocatoria. Por eso, cuando el encaje no es seguro, se avisa en lugar de
decidir por la persona.

Uso:
    resultado = recomendar(programas, entidad='pyme', sectores=['Turismo/Hostelería'],
                           gastos=['software'], ubicacion='asturias', plazo='pronto',
                           presupuesto='10-50k')
"""

import re
import unicodedata
from datetime import date, datetime

# ---------------------------------------------------------------------------
# Figuras que puede elegir la persona y qué etiquetas de "beneficiarios" de la
# convocatoria las cubren. 'exactos' = encaje claro; 'parciales' = puede
# encajar, hay que revisar las bases.
# Las etiquetas se comparan normalizadas (sin tildes, minúsculas).
# ---------------------------------------------------------------------------
PERFILES = [
    {'id': 'pyme', 'label': 'PYME', 'icono': 'fa-store',
     'desc': 'Micro, pequeña o mediana empresa (menos de 250 personas)',
     'exactos': {'pyme', 'todas las empresas'}, 'parciales': set()},
    {'id': 'autonomo', 'label': 'Persona autónoma', 'icono': 'fa-user-tie',
     'desc': 'Trabajador/a por cuenta propia',
     'exactos': {'autonomos'}, 'parciales': {'todas las empresas', 'emprendedores', 'pyme'}},
    {'id': 'gran_empresa', 'label': 'Gran empresa', 'icono': 'fa-building',
     'desc': 'Empresa de 250 o más personas',
     'exactos': {'gran empresa', 'todas las empresas'}, 'parciales': set()},
    {'id': 'startup', 'label': 'Startup', 'icono': 'fa-rocket',
     'desc': 'Empresa nueva de base tecnológica o innovadora',
     'exactos': {'startups', 'todas las empresas'}, 'parciales': {'emprendedores', 'pyme'}},
    {'id': 'emprendedor', 'label': 'Persona emprendedora', 'icono': 'fa-lightbulb',
     'desc': 'Tienes una idea o proyecto, pero aún no has constituido la empresa',
     'exactos': {'emprendedores'}, 'parciales': {'autonomos', 'startups'}},
    {'id': 'cooperativa', 'label': 'Cooperativa o sociedad laboral', 'icono': 'fa-handshake',
     'desc': 'Economía social',
     'exactos': {'sociedades laborales y cooperativas', 'todas las empresas'}, 'parciales': {'pyme'}},
    {'id': 'ong', 'label': 'Asociación, fundación u ONG', 'icono': 'fa-hands-helping',
     'desc': 'Entidad sin ánimo de lucro',
     'exactos': {'ong'}, 'parciales': set()},
    {'id': 'asoc_empresarial', 'label': 'Asociación empresarial', 'icono': 'fa-users',
     'desc': 'Federación, cámara, clúster u organización empresarial',
     'exactos': {'asociaciones empresariales'}, 'parciales': {'ong'}},
    {'id': 'sector_publico', 'label': 'Entidad pública', 'icono': 'fa-landmark',
     'desc': 'Ayuntamiento, mancomunidad u otro organismo público',
     'exactos': {'sector publico'}, 'parciales': set()},
    {'id': 'investigador', 'label': 'Investigador/a o centro de investigación', 'icono': 'fa-flask',
     'desc': 'Personal investigador, universidad u organismo de I+D',
     'exactos': {'investigadores'}, 'parciales': {'sector publico'}},
    {'id': 'particular', 'label': 'Particular', 'icono': 'fa-user',
     'desc': 'Persona física sin actividad económica',
     'exactos': {'particulares'}, 'parciales': set()},
]
PERFIL_POR_ID = {p['id']: p for p in PERFILES}

UBICACIONES = {
    'asturias': 'Mi actividad o centro de trabajo está en Asturias',
    'otra': 'Estoy fuera de Asturias',
}

# Plazo: qué convocatorias se muestran según cuándo necesita la persona la ayuda
PLAZOS = {
    'ya': 'Ahora: solo convocatorias abiertas',
    'pronto': 'En los próximos meses: también las que abrirán pronto',
    'todas': 'Estoy planificando: también las cerradas, que suelen repetirse cada año',
}

# Presupuesto del proyecto, por rangos (euros; None = sin límite superior)
PRESUPUESTOS = [
    {'id': 'hasta10k', 'label': 'Menos de 10.000 €', 'min': 0, 'max': 10_000},
    {'id': '10-50k', 'label': 'De 10.000 a 50.000 €', 'min': 10_000, 'max': 50_000},
    {'id': '50-200k', 'label': 'De 50.000 a 200.000 €', 'min': 50_000, 'max': 200_000},
    {'id': '200k-1m', 'label': 'De 200.000 € a 1 millón', 'min': 200_000, 'max': 1_000_000},
    {'id': 'mas1m', 'label': 'Más de 1 millón de €', 'min': 1_000_000, 'max': None},
]
PRESUPUESTO_POR_ID = {r['id']: r for r in PRESUPUESTOS}

# ---------------------------------------------------------------------------
# Qué quiere financiar la persona. Cada grupo se detecta en la convocatoria por
# palabras clave en sus gastos subvencionables (texto libre) y por su tipo de
# proyecto (etiqueta ya normalizada). Las claves se buscan sin tildes y en
# minúsculas, al principio de palabra.
# ---------------------------------------------------------------------------
GASTOS = [
    {'id': 'personal', 'label': 'Contratar o pagar personal', 'icono': 'fa-user-plus',
     'claves': ['personal', 'salari', 'contratacion de', 'contratar', 'retribuc', 'nomina',
                'costes laborales', 'seguridad social'],
     'proyectos': {'contratacion', 'formacion y empleo'}},
    {'id': 'maquinaria', 'label': 'Maquinaria y equipos', 'icono': 'fa-cogs',
     'claves': ['maquinaria', 'bienes de equipo', 'equipamiento', 'equipos', 'utillaje', 'instrumental',
                'herramientas', 'vehiculo'],
     'proyectos': {'inversion productiva'}},
    {'id': 'software', 'label': 'Software y digitalización', 'icono': 'fa-laptop-code',
     'claves': ['software', 'informatic', 'digital', 'web', r'tic\b', 'ciberseguridad', 'hardware',
                'comercio electronico'],
     'proyectos': {'digitalizacion'}},
    {'id': 'consultoria', 'label': 'Consultoría y servicios externos', 'icono': 'fa-handshake',
     'claves': ['consultor', 'asesor', 'colaboraciones externas', 'servicios externos', 'subcontrat',
                'asistencia tecnica', 'auditor', 'servicios tecnologicos'],
     'proyectos': set()},
    {'id': 'idi', 'label': 'I+D e innovación', 'icono': 'fa-flask',
     'claves': ['investigacion', r'i\+d', 'desarrollo experimental', 'innovacion', 'prototipo'],
     'proyectos': {'i+d+i'}},
    {'id': 'promocion', 'label': 'Promoción, ferias e internacionalización', 'icono': 'fa-globe-europe',
     'claves': ['feria', 'promocion', 'marketing', 'publicidad', 'viaje', 'difusion', 'comercializacion',
                'internacional', 'mision', 'exportac'],
     'proyectos': {'internacionalizacion', 'marketing/comercializacion'}},
    {'id': 'obras', 'label': 'Obras, naves e instalaciones', 'icono': 'fa-hard-hat',
     'claves': ['obra civil', 'obras', 'edific', 'construccion', 'nave', 'acondicionamiento', 'reforma',
                'terreno', 'urbanizacion', 'instalaciones'],
     'proyectos': {'inversion productiva'}},
    {'id': 'energia', 'label': 'Energía y sostenibilidad', 'icono': 'fa-leaf',
     'claves': ['energ', 'renovable', 'fotovolt', 'autoconsumo', 'emisiones', 'residuo',
                'economia circular', 'descarboniz', 'sostenib'],
     'proyectos': {'sostenibilidad'}},
    {'id': 'formacion', 'label': 'Formación', 'icono': 'fa-chalkboard-teacher',
     'claves': ['formacion', 'curso', 'capacitacion', 'formativ'],
     'proyectos': {'formacion y empleo'}},
    {'id': 'patentes', 'label': 'Patentes y propiedad industrial', 'icono': 'fa-certificate',
     'claves': ['patente', 'propiedad industrial', 'propiedad intelectual', r'marcas?\b'],
     'proyectos': {'propiedad intelectual'}},
    {'id': 'creacion', 'label': 'Crear o poner en marcha una empresa', 'icono': 'fa-seedling',
     'claves': ['constitucion', 'puesta en marcha', 'inicio de actividad', 'creacion de empresa',
                'autoempleo', 'establecimiento como'],
     'proyectos': {'creacion de empresas'}},
]
GASTO_POR_ID = {g['id']: g for g in GASTOS}
_RE_EXCLUSION = re.compile(r'\b(?:excluy|excluid|excepto|salvo|no se incluy|no subvencionable|no son subvencionable)')
_RE_GASTO = {g['id']: re.compile(r'\b(?:' + '|'.join(g['claves']) + ')') for g in GASTOS}

# Etiquetas "comodín": la convocatoria vale para cualquier sector
SECTORES_COMODIN = {'general/multisectorial', 'general', 'multisectorial', 'todos los sectores'}

# Variantes de escritura que deben tratarse como la misma etiqueta
_ALIAS = {'pymes': 'pyme', 'autonomo': 'autonomos', 'startup': 'startups',
          'emprendedor': 'emprendedores', 'ongs': 'ong'}

# Pesos de la puntuación (suman 100 como máximo)
_P_BENEF = {'exacto': 40, 'parcial': 20, 'sin_datos': 12}
_P_ESTADO = {'abierta': 16, 'cierre_proximo': 16, 'sin_fechas': 12, 'proxima': 10, 'cerrada': 0}

URGENTE_DIAS = 15


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def _n(valor):
    """Normaliza una etiqueta para compararla: sin tildes, minúsculas, sin espacios de más."""
    s = unicodedata.normalize('NFKD', str(valor)).encode('ascii', 'ignore').decode()
    s = re.sub(r'\s+', ' ', s).strip().casefold()
    return _ALIAS.get(s, s)


def _lista(valor):
    """Convierte None / texto / lista en una lista de textos no vacíos."""
    if valor is None:
        return []
    if isinstance(valor, str):
        valor = [valor]
    try:
        return [str(v).strip() for v in valor if v is not None and str(v).strip()]
    except TypeError:
        return []


def _etiquetas(valor):
    """{etiqueta_normalizada: etiqueta_original} de un campo de etiquetas."""
    return {_n(v): v for v in _lista(valor)}


def _fecha(valor):
    if not valor or str(valor).lower() in ('null', 'none', 'nan'):
        return None
    texto = str(valor).strip().replace('Z', '')
    for recorte in (texto, texto[:10]):
        try:
            return datetime.fromisoformat(recorte).date()
        except ValueError:
            continue
    return None


def _num(valor):
    """Importe como float, o None si falta o no es un número."""
    if valor is None or isinstance(valor, bool):
        return None
    try:
        x = float(str(valor).replace('€', '').strip())
    except ValueError:
        return None
    return x if x == x and x > 0 else None  # descarta NaN, 0 y negativos


def _euros(x):
    """1234567.8 -> '1.234.600 €' (redondeado: es una cifra orientativa)."""
    x = round(x, -2) if x >= 1000 else round(x)
    return f'{int(x):,}'.replace(',', '.') + ' €'


def _porcentaje_unico(texto):
    """Si la intensidad indica un único porcentaje (p. ej. «Hasta el 50 %»), lo devuelve.
    Si hay varios (según tamaño de empresa, fase...) devuelve None: no se puede estimar."""
    valores = {float(v.replace(',', '.')) for v in re.findall(r'(\d{1,3}(?:[.,]\d+)?)\s*%', str(texto or ''))}
    if len(valores) == 1:
        pct = valores.pop()
        return pct if 0 < pct <= 100 else None
    return None


def gastos_de_programa(p):
    """Ids de GASTOS que financia la convocatoria (por sus gastos y su tipo de proyecto)."""
    # Lo que va tras «excluyendo», «salvo»... son gastos que NO cubre: no cuenta
    texto = ' · '.join(_RE_EXCLUSION.split(_n(g))[0] for g in _lista(p.get('gastos_subvencionables')))
    proyectos = set(_etiquetas(p.get('tipo_proyecto')))
    return {g['id'] for g in GASTOS
            if (texto and _RE_GASTO[g['id']].search(texto)) or (proyectos & g['proyectos'])}


def _nombre(p):
    return p.get('nombre_coloquial') or p.get('nombre') or 'Convocatoria sin nombre'


def _clase_ambito(p):
    a = _n(p.get('ambito') or '')
    if 'nacional' in a or 'estatal' in a:
        return 'nacional'
    if 'europe' in a:
        return 'europeo'
    if 'autonom' in a or 'asturias' in a or 'principado' in a:
        return 'autonomico'
    return 'local' if a else 'autonomico'


def _estado(p, hoy):
    """Devuelve (estado, dias_hasta_cierre) calculado con las fechas, con el día de cierre incluido."""
    conv = p.get('convocatoria') or {}
    if p.get('resuelta'):
        return 'cerrada', None
    cierre, apertura = _fecha(conv.get('fecha_cierre')), _fecha(conv.get('fecha_apertura'))
    if cierre and cierre < hoy:
        return 'cerrada', None
    if apertura and apertura > hoy:
        return 'proxima', None
    if cierre:
        dias = (cierre - hoy).days
        return ('cierre_proximo' if dias <= URGENTE_DIAS else 'abierta'), dias
    texto = _n(conv.get('estado') or '')
    if 'cerrada' in texto:
        return 'cerrada', None
    if 'proxima' in texto or 'pendiente' in texto:
        return 'proxima', None
    return 'sin_fechas', None


def opciones_formulario(programas):
    """Sectores disponibles, tomados de los datos (sin los comodines)."""
    sectores = {}
    for p in programas:
        for k, v in _etiquetas(p.get('sectores')).items():
            if k not in SECTORES_COMODIN:
                sectores.setdefault(k, v)
    return sorted(sectores.values(), key=_n)


def filtrar_validos(seleccion, opciones):
    """Se queda solo con los valores del formulario que existen en 'opciones' (sin duplicados,
    con la escritura original de la opción). Ignora cualquier valor inventado."""
    por_norma = {_n(o): o for o in opciones}
    salida = []
    for s in _lista(list(seleccion)):
        o = por_norma.get(_n(s))
        if o and o not in salida:
            salida.append(o)
    return salida


# ---------------------------------------------------------------------------
# Evaluación de una convocatoria
# ---------------------------------------------------------------------------
def _encaje_presupuesto(fin, rango):
    """
    Compara el rango de presupuesto del proyecto con los límites de la convocatoria.
    Devuelve (descartar, avisos, ayuda_estimada). Solo se descarta cuando el proyecto
    es entero más pequeño que el presupuesto mínimo exigido.
    """
    pmin, pmax = _num(fin.get('presupuesto_minimo')), _num(fin.get('presupuesto_maximo'))
    tope = _num(fin.get('importe_maximo_subvencionable')) or _num(fin.get('importe_maximo'))
    lo, hi = rango['min'], rango['max']
    avisos = []

    if pmin and hi is not None and hi < pmin:
        return True, [], None
    if pmin and lo < pmin:
        avisos.append(f'Exige un presupuesto mínimo de {_euros(pmin)}.')
    if pmax and lo > pmax:
        avisos.append(f'Solo subvenciona proyectos de hasta {_euros(pmax)}: tu proyecto se cubriría en parte.')

    # Ayuda orientativa: presupuesto subvencionable x intensidad, con el tope por solicitante
    pct = _porcentaje_unico(fin.get('intensidad'))
    if pct is None:
        return False, avisos, None
    base_lo = max(lo, pmin or 0)
    base_hi = hi
    if pmax:
        base_lo, base_hi = min(base_lo, pmax), min(hi, pmax) if hi is not None else pmax
    a_lo = base_lo * pct / 100
    a_hi = base_hi * pct / 100 if base_hi is not None else None
    if tope:
        a_lo = min(a_lo, tope)
        a_hi = min(a_hi, tope) if a_hi is not None else tope
    pct_txt = f'{pct:g} %'.replace('.', ',')
    if a_hi is None:
        texto = f'desde {_euros(a_lo)}'
    elif a_lo < 1 or _euros(a_lo) == _euros(a_hi):
        texto = f'hasta {_euros(a_hi)}'
    else:
        texto = f'entre {_euros(a_lo)} y {_euros(a_hi)}'
    detalle = f'{pct_txt} del presupuesto' + (f', con un máximo de {_euros(tope)} por solicitante' if tope else '')
    return False, avisos, {'texto': texto, 'detalle': detalle}


def _evaluar(p, perfil, S, G, ubicacion, plazo, rango, hoy):
    """Devuelve un motivo de descarte (str) o un dict con el resultado."""
    estado, dias = _estado(p, hoy)
    if estado == 'cerrada' and plazo != 'todas':
        return 'cerradas'
    if estado == 'proxima' and plazo == 'ya':
        return 'plazo'

    ambito = _clase_ambito(p)
    if ubicacion == 'otra' and ambito in ('autonomico', 'local'):
        return 'ubicacion'

    # 1) Beneficiario (obligatorio)
    tags = _etiquetas(p.get('beneficiarios'))
    exactos = [tags[t] for t in tags if t in perfil['exactos']]
    parciales = [tags[t] for t in tags if t in perfil['parciales']]
    if exactos:
        benef, benef_txt = 'exacto', exactos
    elif parciales:
        benef, benef_txt = 'parcial', parciales
    elif not tags:
        benef, benef_txt = 'sin_datos', []
    else:
        return 'beneficiario'

    # 2) Sector (si la persona ha elegido alguno)
    sectores = _etiquetas(p.get('sectores'))
    sector_coinc = [sectores[t] for t in sectores if t in S]
    if not S:
        sector, sector_pts = 'neutro', 12
    elif sector_coinc:
        sector, sector_pts = 'match', min(22, 14 + 8 * (len(sector_coinc) - 1))
    elif not sectores or any(t in SECTORES_COMODIN for t in sectores):
        sector, sector_pts = 'general', 12
    else:
        return 'sector'

    # 3) Presupuesto (si la persona lo ha indicado)
    fin = p.get('financiacion') or {}
    avisos_presupuesto, ayuda_estimada = [], None
    if rango:
        descartar, avisos_presupuesto, ayuda_estimada = _encaje_presupuesto(fin, rango)
        if descartar:
            return 'presupuesto'

    # 4) Qué quiere financiar (si ha elegido algo)
    financia = gastos_de_programa(p)
    gasto_coinc = [GASTO_POR_ID[g]['label'] for g in G if g in financia]
    if not G:
        gasto, gasto_pts = 'neutro', 12
    elif gasto_coinc:
        gasto, gasto_pts = 'match', min(22, 14 + 8 * (len(gasto_coinc) - 1))
    elif not financia:
        gasto, gasto_pts = 'sin_datos', 10
    else:
        gasto, gasto_pts = 'no', 0

    score = _P_BENEF[benef] + sector_pts + gasto_pts + _P_ESTADO[estado]

    # Motivos y avisos legibles
    motivos, avisos = [], []
    if benef == 'exacto':
        motivos.append('Dirigida a: ' + ', '.join(benef_txt))
    elif benef == 'parcial':
        avisos.append('Tu figura no aparece expresamente: la convocatoria admite «' + '», «'.join(benef_txt)
                      + '». Comprueba en las bases si puedes optar.')
    else:
        avisos.append('La convocatoria no indica a quién va dirigida: consulta las bases.')

    if sector == 'match':
        motivos.append('Sector: ' + ', '.join(sector_coinc))
    elif sector == 'general':
        motivos.append('Válida para cualquier sector')
    if gasto == 'match':
        motivos.append('Financia: ' + ', '.join(gasto_coinc).lower())
    elif gasto == 'sin_datos':
        avisos.append('No detallamos qué gastos cubre: consulta las bases.')
    elif gasto == 'no':
        avisos.append('Financia otro tipo de gastos ('
                      + ', '.join(GASTO_POR_ID[g]['label'].lower() for g in GASTOS_ORDEN if g in financia) + ').')
    avisos.extend(avisos_presupuesto)

    if estado == 'cierre_proximo':
        motivos.append(f'¡Cierra en {dias} día{"s" if dias != 1 else ""}!' if dias else '¡Cierra hoy!')
    elif estado == 'abierta':
        motivos.append(f'Abierta: quedan {dias} días')
    elif estado == 'proxima':
        ap = _fecha((p.get('convocatoria') or {}).get('fecha_apertura'))
        motivos.append('Próxima apertura' + (f': {ap.strftime("%d/%m/%Y")}' if ap else ''))
    elif estado == 'sin_fechas':
        motivos.append('Plazo abierto (sin fecha de cierre indicada)')
    else:
        avisos.append('Plazo cerrado: suele repetirse cada año, vigila la próxima edición.')

    if ambito == 'local':
        avisos.append(f'Convocatoria local ({p.get("ambito")}): solo para actividad en ese municipio.')

    # Grupo en el que se muestra
    if estado == 'cerrada':
        grupo = 'cerradas'
    elif gasto == 'no':
        grupo = 'otro_gasto'
    elif benef == 'exacto' and ambito != 'local':
        grupo = 'recomendadas'
    else:
        grupo = 'revisar'

    conv = p.get('convocatoria') or {}
    return {
        'id': p.get('id'),
        'nombre': _nombre(p),
        'organismo': p.get('organismo'),
        'resumen': p.get('resumen_breve'),
        'tipo_ayuda': ', '.join(_lista(p.get('tipo_ayuda'))),
        'ambito': p.get('ambito'),
        'dotacion': _num(fin.get('presupuesto_total')),
        'ayuda_max': _num(fin.get('importe_maximo_subvencionable')) or _num(fin.get('importe_maximo')),
        'ayuda_estimada': ayuda_estimada,
        'intensidad': fin.get('intensidad'),
        'estado': estado,
        'dias': dias,
        'fecha_cierre': _fecha(conv.get('fecha_cierre')),
        'score': score,
        'grupo': grupo,
        'motivos': motivos,
        'avisos': avisos,
    }


GASTOS_ORDEN = [g['id'] for g in GASTOS]
GRUPOS = ('recomendadas', 'revisar', 'otro_gasto', 'cerradas')
MOTIVOS_DESCARTE = ('beneficiario', 'sector', 'ubicacion', 'presupuesto', 'plazo', 'cerradas')


def recomendar(programas, entidad, sectores=(), gastos=(), ubicacion='asturias', plazo='pronto',
               presupuesto=None, hoy=None):
    """
    Evalúa todas las convocatorias para el perfil indicado.

    gastos: ids de GASTOS; plazo: clave de PLAZOS; presupuesto: id de PRESUPUESTOS o None.
    Devuelve {'recomendadas', 'revisar', 'otro_gasto', 'cerradas' (listas ordenadas),
    'descartadas' ({motivo: nº}), 'total'}.
    Lanza ValueError si la entidad no es válida.
    """
    perfil = PERFIL_POR_ID.get(entidad)
    if perfil is None:
        raise ValueError(f'Figura no válida: {entidad!r}')
    if ubicacion not in UBICACIONES:
        ubicacion = 'asturias'
    if plazo not in PLAZOS:
        plazo = 'pronto'
    rango = PRESUPUESTO_POR_ID.get(presupuesto)
    hoy = hoy or date.today()
    S = {_n(s) for s in _lista(list(sectores))}
    G = [g for g in GASTOS_ORDEN if g in set(_lista(list(gastos)))]

    salida = {g: [] for g in GRUPOS}
    salida.update(descartadas={m: 0 for m in MOTIVOS_DESCARTE}, total=len(programas))
    for p in programas:
        try:
            r = _evaluar(p, perfil, S, G, ubicacion, plazo, rango, hoy)
        except Exception:
            # Una convocatoria con datos raros no debe tumbar toda la búsqueda
            continue
        if isinstance(r, str):
            salida['descartadas'][r] += 1
        else:
            salida[r['grupo']].append(r)

    clave = lambda r: (-r['score'], r['dias'] if r['dias'] is not None else 9999, r['nombre'].casefold())
    for g in GRUPOS:
        salida[g].sort(key=clave)
    return salida
