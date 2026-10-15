"""
Recomendador de convocatorias ("Busca tu convocatoria").

Motor determinista basado en reglas sobre las etiquetas que ya tienen las
convocatorias (beneficiarios, sectores, tipo de proyecto, ámbito y fechas).
No usa IA ni red: la misma entrada da siempre el mismo resultado, y no
depende de cuotas externas.

Es una primera guía orientativa: no sustituye a leer las bases de cada
convocatoria. Por eso, cuando el encaje no es seguro, se avisa en lugar de
decidir por la persona.

Uso:
    resultado = recomendar(programas, entidad='pyme', sectores=['Turismo/Hostelería'],
                           proyectos=['Digitalización'], ubicacion='asturias')
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

# Etiquetas "comodín": la convocatoria vale para cualquier sector / tipo de proyecto
SECTORES_COMODIN = {'general/multisectorial', 'general', 'multisectorial', 'todos los sectores'}
PROYECTOS_COMODIN = {'general'}

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
    """Sectores y tipos de proyecto disponibles, tomados de los datos (sin los comodines)."""
    sectores, proyectos = {}, {}
    for p in programas:
        for k, v in _etiquetas(p.get('sectores')).items():
            if k not in SECTORES_COMODIN:
                sectores.setdefault(k, v)
        for k, v in _etiquetas(p.get('tipo_proyecto')).items():
            if k not in PROYECTOS_COMODIN:
                proyectos.setdefault(k, v)
    ordenar = lambda d: sorted(d.values(), key=_n)
    return ordenar(sectores), ordenar(proyectos)


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
def _evaluar(p, perfil, S, R, ubicacion, incluir_cerradas, hoy):
    """Devuelve un motivo de descarte (str) o un dict con el resultado."""
    estado, dias = _estado(p, hoy)
    if estado == 'cerrada' and not incluir_cerradas:
        return 'cerradas'

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

    # 3) Tipo de proyecto (si la persona ha elegido alguno)
    proyectos = _etiquetas(p.get('tipo_proyecto'))
    proy_coinc = [proyectos[t] for t in proyectos if t in R]
    if not R:
        proy, proy_pts = 'neutro', 12
    elif proy_coinc:
        proy, proy_pts = 'match', min(22, 14 + 8 * (len(proy_coinc) - 1))
    elif not proyectos or any(t in PROYECTOS_COMODIN for t in proyectos):
        proy, proy_pts = 'general', 12
    else:
        proy, proy_pts = 'no', 0

    score = _P_BENEF[benef] + sector_pts + proy_pts + _P_ESTADO[estado]

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
    if proy == 'match':
        motivos.append('Tipo de proyecto: ' + ', '.join(proy_coinc))
    elif proy == 'general' and R:
        motivos.append('Admite proyectos de cualquier tipo')
    elif proy == 'no':
        avisos.append('Está pensada para otro tipo de proyecto ('
                      + (', '.join(_lista(p.get('tipo_proyecto'))) or 'sin especificar') + ').')

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
    elif proy == 'no':
        grupo = 'otro_proyecto'
    elif benef == 'exacto' and ambito != 'local':
        grupo = 'recomendadas'
    else:
        grupo = 'revisar'

    fin = p.get('financiacion') or {}
    conv = p.get('convocatoria') or {}
    return {
        'id': p.get('id'),
        'nombre': _nombre(p),
        'organismo': p.get('organismo'),
        'resumen': p.get('resumen_breve'),
        'tipo_ayuda': ', '.join(_lista(p.get('tipo_ayuda'))),
        'ambito': p.get('ambito'),
        'presupuesto': fin.get('presupuesto_total') or fin.get('importe_maximo'),
        'intensidad': fin.get('intensidad'),
        'estado': estado,
        'dias': dias,
        'fecha_cierre': _fecha(conv.get('fecha_cierre')),
        'score': score,
        'grupo': grupo,
        'motivos': motivos,
        'avisos': avisos,
    }


def recomendar(programas, entidad, sectores=(), proyectos=(), ubicacion='asturias',
               incluir_cerradas=False, hoy=None):
    """
    Evalúa todas las convocatorias para el perfil indicado.

    Devuelve {'recomendadas', 'revisar', 'otro_proyecto', 'cerradas' (listas
    ordenadas), 'descartadas' ({motivo: nº}), 'total'}.
    Lanza ValueError si la entidad no es válida.
    """
    perfil = PERFIL_POR_ID.get(entidad)
    if perfil is None:
        raise ValueError(f'Figura no válida: {entidad!r}')
    if ubicacion not in UBICACIONES:
        ubicacion = 'asturias'
    hoy = hoy or date.today()
    S = {_n(s) for s in _lista(list(sectores))}
    R = {_n(r) for r in _lista(list(proyectos))}

    salida = {'recomendadas': [], 'revisar': [], 'otro_proyecto': [], 'cerradas': [],
              'descartadas': {'beneficiario': 0, 'sector': 0, 'ubicacion': 0, 'cerradas': 0},
              'total': len(programas)}
    for p in programas:
        try:
            r = _evaluar(p, perfil, S, R, ubicacion, incluir_cerradas, hoy)
        except Exception:
            # Una convocatoria con datos raros no debe tumbar toda la búsqueda
            continue
        if isinstance(r, str):
            salida['descartadas'][r] += 1
        else:
            salida[r['grupo']].append(r)

    clave = lambda r: (-r['score'], r['dias'] if r['dias'] is not None else 9999, r['nombre'].casefold())
    for g in ('recomendadas', 'revisar', 'otro_proyecto', 'cerradas'):
        salida[g].sort(key=clave)
    return salida
