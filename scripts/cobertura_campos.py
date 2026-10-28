"""
Cobertura de campos de las convocatorias: cuántas tienen cada dato relleno y
qué valores aparecen. Sirve para decidir qué preguntas puede usar el
recomendador ("Busca tu convocatoria") sin dejar fuera convocatorias por
falta de datos.

Solo lee el fichero, no modifica nada. En el servidor:
    python3 scripts/cobertura_campos.py [data/programas_financiacion.json]
"""

import json
import sys
from collections import Counter

VACIOS = (None, '', 'nan', 'null', 'None', 'No especificado', [], {})

CAMPOS_LISTA = ['beneficiarios', 'sectores', 'tipo_proyecto', 'tipo_ayuda', 'fondos_europeos',
                'requisitos', 'gastos_subvencionables']
CAMPOS_FINANCIACION = ['intensidad', 'presupuesto_total', 'presupuesto_minimo', 'presupuesto_maximo',
                       'importe_minimo_subvencionable', 'importe_maximo_subvencionable', 'importe_maximo']


def relleno(v):
    return v not in VACIOS and str(v).strip() not in ('', 'nan', 'null', 'None', 'No especificado')


def numero(v):
    try:
        x = float(str(v).replace('€', '').replace(' ', ''))
    except (TypeError, ValueError):
        return None
    return x if x == x else None  # descarta NaN


def lista(v):
    if isinstance(v, list):
        return [str(x).strip() for x in v if relleno(x)]
    return [str(v).strip()] if relleno(v) else []


def pct(n, total):
    return f'{n:4d} ({100 * n / total:3.0f} %)' if total else '0'


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else 'data/programas_financiacion.json'
    with open(ruta, encoding='utf-8') as f:
        programas = json.load(f)
    total = len(programas)
    print(f'Convocatorias: {total}\n')

    print('== Campos de lista ==')
    for c in CAMPOS_LISTA:
        print(f'  {c:30s} {pct(sum(1 for p in programas if lista(p.get(c))), total)}')

    print('\n== Fechas y ámbito ==')
    for c in ('fecha_apertura', 'fecha_cierre'):
        n = sum(1 for p in programas if relleno((p.get('convocatoria') or {}).get(c)))
        print(f'  {c:30s} {pct(n, total)}')
    print(f"  {'ambito':28s} {pct(sum(1 for p in programas if relleno(p.get('ambito'))), total)}")

    print('\n== Financiación ==')
    for c in CAMPOS_FINANCIACION:
        valores = [(p.get('financiacion') or {}).get(c) for p in programas]
        n = sum(1 for v in valores if relleno(v))
        nums = sorted(x for x in (numero(v) for v in valores) if x is not None)
        rango = f'  min {nums[0]:,.0f} · mediana {nums[len(nums) // 2]:,.0f} · max {nums[-1]:,.0f}' if nums else ''
        print(f'  {c:30s} {pct(n, total)}{rango}')

    print('\n== Valores más frecuentes ==')
    for c in ('ambito', 'tipo_ayuda', 'tipo_proyecto', 'beneficiarios', 'gastos_subvencionables'):
        cuenta = Counter(v for p in programas for v in lista(p.get(c)))
        print(f'\n  {c} ({len(cuenta)} valores distintos):')
        for v, n in cuenta.most_common(25):
            print(f'    {n:4d}  {v[:90]}')

    print('\n== Ejemplos de intensidad (texto libre) ==')
    for v in Counter(str((p.get('financiacion') or {}).get('intensidad')) for p in programas
                     if relleno((p.get('financiacion') or {}).get('intensidad'))).most_common(15):
        print(f'    {v[1]:4d}  {v[0][:90]}')


if __name__ == '__main__':
    main()
