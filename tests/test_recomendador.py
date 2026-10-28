"""
Tests del recomendador. Se ejecutan con la librería estándar:

    python -m unittest tests.test_recomendador -v

La clase TestConDatosReales usa data/programas_financiacion.json si existe
(en el servidor) y se omite si no.
"""

import json
import os
import unittest
from datetime import date

from utils import recomendador as rec

HOY = date(2026, 10, 15)


def prog(id, benef=('PYME',), sectores=('General/Multisectorial',), proyectos=('General',),
         ambito='Autonómico', apertura='2026-09-01', cierre='2026-12-31', **extra):
    p = {'id': id, 'nombre': f'Convocatoria {id}', 'beneficiarios': list(benef),
         'sectores': list(sectores), 'tipo_proyecto': list(proyectos), 'ambito': ambito,
         'convocatoria': {'fecha_apertura': apertura, 'fecha_cierre': cierre}}
    p.update(extra)
    return p


def ids(lista):
    return [r['id'] for r in lista]


class TestBeneficiario(unittest.TestCase):
    def test_pyme_exacta_y_gran_empresa_descartada(self):
        progs = [prog('a', benef=['PYME']), prog('b', benef=['Gran Empresa'])]
        r = rec.recomendar(progs, 'pyme', hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['a'])
        self.assertEqual(r['descartadas']['beneficiario'], 1)

    def test_todas_las_empresas_vale_para_pyme_y_gran_empresa(self):
        progs = [prog('a', benef=['Todas las empresas'])]
        self.assertEqual(ids(rec.recomendar(progs, 'pyme', hoy=HOY)['recomendadas']), ['a'])
        self.assertEqual(ids(rec.recomendar(progs, 'gran_empresa', hoy=HOY)['recomendadas']), ['a'])

    def test_variante_pymes_equivale_a_pyme(self):
        r = rec.recomendar([prog('a', benef=['PYMES'])], 'pyme', hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['a'])

    def test_encaje_parcial_va_a_revisar_con_aviso(self):
        # Una persona autónoma en una convocatoria solo para PYME: puede encajar, hay que revisar
        r = rec.recomendar([prog('a', benef=['PYME'])], 'autonomo', hoy=HOY)
        self.assertEqual(ids(r['revisar']), ['a'])
        self.assertTrue(r['revisar'][0]['avisos'])

    def test_sin_beneficiarios_se_muestra_con_aviso(self):
        r = rec.recomendar([prog('a', benef=[])], 'pyme', hoy=HOY)
        self.assertEqual(ids(r['revisar']), ['a'])

    def test_cada_figura_encuentra_su_etiqueta(self):
        etiquetas = {'pyme': 'PYME', 'autonomo': 'Autónomos', 'gran_empresa': 'Gran Empresa',
                     'startup': 'Startups', 'emprendedor': 'Emprendedores',
                     'cooperativa': 'Sociedades Laborales y Cooperativas', 'ong': 'ONG',
                     'asoc_empresarial': 'Asociaciones Empresariales',
                     'sector_publico': 'Sector Público', 'investigador': 'Investigadores',
                     'particular': 'Particulares'}
        self.assertEqual(set(etiquetas), set(rec.PERFIL_POR_ID), 'falta alguna figura en el test')
        for figura, etiqueta in etiquetas.items():
            r = rec.recomendar([prog('x', benef=[etiqueta])], figura, hoy=HOY)
            self.assertEqual(ids(r['recomendadas']), ['x'], figura)


class TestSectorYProyecto(unittest.TestCase):
    def test_sector_especifico_no_coincidente_se_descarta(self):
        progs = [prog('agro', sectores=['Agricultura/Ganadería/Silvicultura/Pesca']),
                 prog('turismo', sectores=['Turismo/Hostelería'])]
        r = rec.recomendar(progs, 'pyme', sectores=['Turismo/Hostelería'], hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['turismo'])
        self.assertEqual(r['descartadas']['sector'], 1)

    def test_multisectorial_vale_para_cualquier_sector_pero_puntua_menos(self):
        progs = [prog('general'), prog('turismo', sectores=['Turismo/Hostelería'])]
        r = rec.recomendar(progs, 'pyme', sectores=['Turismo/Hostelería'], hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['turismo', 'general'])

    def test_sin_sector_elegido_no_filtra_por_sector(self):
        progs = [prog('agro', sectores=['Agricultura/Ganadería/Silvicultura/Pesca'])]
        self.assertEqual(ids(rec.recomendar(progs, 'pyme', hoy=HOY)['recomendadas']), ['agro'])



class TestGastos(unittest.TestCase):
    def test_detecta_gastos_por_texto_y_por_tipo_de_proyecto(self):
        p = prog('a', proyectos=['Digitalización'],
                 gastos_subvencionables=['Adquisición de maquinaria y bienes de equipo', 'Costes salariales del personal'])
        self.assertEqual(rec.gastos_de_programa(p), {'maquinaria', 'personal', 'software'})

    def test_lo_excluido_no_cuenta(self):
        p = prog('a', gastos_subvencionables=['Otros gastos del proyecto (excluyendo terrenos y obras)'])
        self.assertNotIn('obras', rec.gastos_de_programa(p))

    def test_palabras_parecidas_no_confunden(self):
        # «tic» no debe saltar dentro de «práctica» ni «estadística»
        p = prog('a', gastos_subvencionables=['Prácticas y estadística'])
        self.assertNotIn('software', rec.gastos_de_programa(p))

    def test_gasto_distinto_va_al_grupo_otro_gasto(self):
        progs = [prog('dig', proyectos=['Digitalización']), prog('sost', proyectos=['Sostenibilidad'])]
        r = rec.recomendar(progs, 'pyme', gastos=['software'], hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['dig'])
        self.assertEqual(ids(r['otro_gasto']), ['sost'])

    def test_sin_datos_de_gastos_se_muestra_con_aviso(self):
        r = rec.recomendar([prog('a', proyectos=['General'])], 'pyme', gastos=['software'], hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['a'])
        self.assertTrue(any('gastos' in a for a in r['recomendadas'][0]['avisos']))

    def test_mas_coincidencias_puntuan_mas(self):
        progs = [prog('uno', proyectos=['Digitalización']),
                 prog('dos', proyectos=['Digitalización', 'I+D+i'])]
        r = rec.recomendar(progs, 'pyme', gastos=['software', 'idi'], hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['dos', 'uno'])

    def test_ids_de_gasto_desconocidos_se_ignoran(self):
        r = rec.recomendar([prog('a', proyectos=['Digitalización'])], 'pyme', gastos=['inventado'], hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['a'])


class TestPresupuesto(unittest.TestCase):
    def test_proyecto_menor_que_el_minimo_se_descarta(self):
        p = prog('a', financiacion={'presupuesto_minimo': 50000})
        r = rec.recomendar([p], 'pyme', presupuesto='10-50k', hoy=HOY)
        self.assertEqual(r['descartadas']['presupuesto'], 0)  # 50.000 entra en el rango
        r = rec.recomendar([p], 'pyme', presupuesto='hasta10k', hoy=HOY)
        self.assertEqual(r['descartadas']['presupuesto'], 1)

    def test_minimo_dentro_del_rango_avisa(self):
        p = prog('a', financiacion={'presupuesto_minimo': '20000'})
        r = rec.recomendar([p], 'pyme', presupuesto='10-50k', hoy=HOY)
        self.assertTrue(any('mínimo de 20.000 €' in a for a in r['recomendadas'][0]['avisos']))

    def test_sin_presupuesto_no_filtra_ni_estima(self):
        p = prog('a', financiacion={'presupuesto_minimo': 500000, 'intensidad': '50%'})
        r = rec.recomendar([p], 'pyme', hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['a'])
        self.assertIsNone(r['recomendadas'][0]['ayuda_estimada'])

    def test_ayuda_orientativa_con_tope(self):
        p = prog('a', financiacion={'intensidad': 'Hasta el 50 % de los gastos', 'importe_maximo_subvencionable': 75000})
        e = rec.recomendar([p], 'pyme', presupuesto='50-200k', hoy=HOY)['recomendadas'][0]['ayuda_estimada']
        self.assertEqual(e['texto'], 'entre 25.000 € y 75.000 €')
        self.assertIn('máximo de 75.000 €', e['detalle'])

    def test_ayuda_orientativa_rango_abierto(self):
        p = prog('a', financiacion={'intensidad': '70%'})
        r = rec.recomendar([p], 'pyme', presupuesto='hasta10k', hoy=HOY)
        self.assertEqual(r['recomendadas'][0]['ayuda_estimada']['texto'], 'hasta 7.000 €')
        r = rec.recomendar([p], 'pyme', presupuesto='mas1m', hoy=HOY)
        self.assertEqual(r['recomendadas'][0]['ayuda_estimada']['texto'], 'desde 700.000 €')

    def test_ayuda_orientativa_respeta_presupuesto_maximo_y_minimo(self):
        p = prog('a', financiacion={'intensidad': '50%', 'presupuesto_minimo': 20000, 'presupuesto_maximo': 40000})
        r = rec.recomendar([p], 'pyme', presupuesto='10-50k', hoy=HOY)
        self.assertEqual(r['recomendadas'][0]['ayuda_estimada']['texto'], 'entre 10.000 € y 20.000 €')

    def test_varias_intensidades_no_se_estiman(self):
        p = prog('a', financiacion={'intensidad': 'Pequeñas empresas: hasta 35%. Medianas: hasta 25%.'})
        r = rec.recomendar([p], 'pyme', presupuesto='10-50k', hoy=HOY)
        self.assertIsNone(r['recomendadas'][0]['ayuda_estimada'])

    def test_importes_en_el_resultado(self):
        p = prog('a', financiacion={'presupuesto_total': 1250000, 'importe_maximo_subvencionable': 'nan'})
        res = rec.recomendar([p], 'pyme', hoy=HOY)['recomendadas'][0]
        self.assertEqual(res['dotacion'], 1250000)
        self.assertIsNone(res['ayuda_max'])


class TestEstadoYUbicacion(unittest.TestCase):
    def test_cerradas_ocultas_por_defecto_y_en_su_grupo_si_se_planifica(self):
        progs = [prog('abierta'), prog('cerrada', cierre='2026-05-01')]
        r = rec.recomendar(progs, 'pyme', hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['abierta'])
        self.assertEqual(r['descartadas']['cerradas'], 1)
        r = rec.recomendar(progs, 'pyme', plazo='todas', hoy=HOY)
        self.assertEqual(ids(r['cerradas']), ['cerrada'])
        self.assertEqual(ids(r['recomendadas']), ['abierta'])

    def test_plazo_ya_excluye_las_proximas(self):
        progs = [prog('abierta'), prog('proxima', apertura='2026-11-01', cierre='2026-12-01')]
        r = rec.recomendar(progs, 'pyme', plazo='ya', hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['abierta'])
        self.assertEqual(r['descartadas']['plazo'], 1)
        r = rec.recomendar(progs, 'pyme', plazo='pronto', hoy=HOY)
        self.assertEqual(len(r['recomendadas']), 2)

    def test_el_dia_de_cierre_sigue_abierta(self):
        r = rec.recomendar([prog('hoy', cierre='2026-10-15')], 'pyme', hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['hoy'])
        self.assertIn('¡Cierra hoy!', r['recomendadas'][0]['motivos'])

    def test_resuelta_cuenta_como_cerrada(self):
        r = rec.recomendar([prog('a', resuelta=True)], 'pyme', hoy=HOY)
        self.assertEqual(r['descartadas']['cerradas'], 1)

    def test_proxima_apertura(self):
        r = rec.recomendar([prog('a', apertura='2026-11-01', cierre='2026-12-01')], 'pyme', hoy=HOY)
        self.assertEqual(r['recomendadas'][0]['estado'], 'proxima')

    def test_sin_fechas_se_trata_como_abierta(self):
        p = prog('a')
        p['convocatoria'] = {'estado': 'Abierta'}
        self.assertEqual(ids(rec.recomendar([p], 'pyme', hoy=HOY)['recomendadas']), ['a'])

    def test_ordena_primero_las_que_cierran_antes_a_igual_puntuacion(self):
        progs = [prog('lejos', cierre='2026-12-31'), prog('cerca', cierre='2026-11-20')]
        r = rec.recomendar(progs, 'pyme', hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['cerca', 'lejos'])

    def test_fuera_de_asturias_solo_nacionales(self):
        progs = [prog('ast', ambito='Autonómico'), prog('nac', ambito='Nacional')]
        r = rec.recomendar(progs, 'pyme', ubicacion='otra', hoy=HOY)
        self.assertEqual(ids(r['recomendadas']), ['nac'])
        self.assertEqual(r['descartadas']['ubicacion'], 1)

    def test_local_va_a_revisar_con_aviso(self):
        r = rec.recomendar([prog('av', ambito='Local')], 'pyme', hoy=HOY)
        self.assertEqual(ids(r['revisar']), ['av'])
        self.assertTrue(any('local' in a.lower() for a in r['revisar'][0]['avisos']))


class TestRobustez(unittest.TestCase):
    def test_entidad_invalida(self):
        with self.assertRaises(ValueError):
            rec.recomendar([], 'marciano')

    def test_lista_vacia(self):
        r = rec.recomendar([], 'pyme', hoy=HOY)
        self.assertEqual(r['total'], 0)
        self.assertEqual(r['recomendadas'], [])

    def test_datos_raros_no_rompen_nada(self):
        raros = [
            {}, {'id': 'x'}, {'id': 'y', 'beneficiarios': None, 'sectores': 'Turismo', 'tipo_proyecto': 5},
            {'id': 'z', 'beneficiarios': 'PYME', 'convocatoria': {'fecha_cierre': 'null', 'fecha_apertura': 'basura'}},
            {'id': 'w', 'convocatoria': None, 'financiacion': None, 'ambito': None},
            {'id': 'v', 'beneficiarios': [None, '', 'PYME'], 'convocatoria': {'fecha_cierre': '2026-12-31 00:00:00'}},
        ]
        for p in raros[1:]:
            p['gastos_subvencionables'] = [None, 5, 'Maquinaria']
            p['financiacion'] = {'intensidad': 'nan', 'presupuesto_minimo': 'basura', 'importe_maximo_subvencionable': True}
        r = rec.recomendar(raros, 'pyme', sectores=['Turismo'], gastos=['x', 'maquinaria'], plazo='todas',
                           presupuesto='10-50k', hoy=HOY)
        self.assertEqual(r['total'], len(raros))

    def test_valores_de_formulario_desconocidos_se_ignoran(self):
        r = rec.recomendar([prog('a')], 'pyme', sectores=['Inventado'], ubicacion='marte', hoy=HOY)
        # sector inventado: la convocatoria es multisectorial, así que sigue valiendo
        self.assertEqual(ids(r['recomendadas']), ['a'])

    def test_filtrar_validos(self):
        opciones = ['Turismo/Hostelería', 'I+D+i']
        self.assertEqual(rec.filtrar_validos(['turismo/hostelería', 'Inventado', 'I+D+i', 'i+d+i', ''], opciones),
                         ['Turismo/Hostelería', 'I+D+i'])
        self.assertEqual(rec.filtrar_validos([], opciones), [])
        self.assertEqual(rec.filtrar_validos(['<script>alert(1)</script>'], opciones), [])

    def test_opciones_sin_comodines_ni_duplicados(self):
        progs = [prog('a', sectores=['General/Multisectorial', 'Turismo/Hostelería']),
                 prog('b', sectores=['turismo/hostelería'])]
        self.assertEqual(rec.opciones_formulario(progs), ['Turismo/Hostelería'])


DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'data', 'programas_financiacion.json')


@unittest.skipUnless(os.path.exists(DATOS), 'no hay datos reales en este entorno')
class TestConDatosReales(unittest.TestCase):
    """Prueba de estabilidad: todas las figuras x todas las opciones, sobre los datos de producción."""

    @classmethod
    def setUpClass(cls):
        with open(DATOS, encoding='utf-8') as f:
            cls.programas = json.load(f)['programas']

    def test_todas_las_combinaciones_funcionan(self):
        sectores = rec.opciones_formulario(self.programas)
        self.assertTrue(sectores)
        presupuestos = [None] + list(rec.PRESUPUESTO_POR_ID)
        n = 0
        for figura in rec.PERFIL_POR_ID:
            for ubic in rec.UBICACIONES:
                for plazo in rec.PLAZOS:
                    for S in [[]] + [[s] for s in sectores]:
                        for G in [[]] + [[g] for g in rec.GASTO_POR_ID]:
                            presupuesto = presupuestos[n % len(presupuestos)]
                            r = rec.recomendar(self.programas, figura, S, G, ubic, plazo, presupuesto, hoy=HOY)
                            self.assertEqual(r['total'], len(self.programas))
                            # cada convocatoria acaba en un grupo o descartada, nunca en dos sitios
                            vistas = sum(len(r[g]) for g in rec.GRUPOS)
                            self.assertEqual(vistas + sum(r['descartadas'].values()), len(self.programas))
                            n += 1
        print(f'\n   {n} combinaciones probadas sobre {len(self.programas)} convocatorias reales')

    def test_cada_figura_con_datos_reales_tiene_alguna_opcion_o_se_explica(self):
        # Informativo: las figuras sin ninguna convocatoria abierta no deben dar error
        for figura in rec.PERFIL_POR_ID:
            r = rec.recomendar(self.programas, figura, hoy=HOY)
            self.assertIsInstance(r['recomendadas'], list)


if __name__ == '__main__':
    unittest.main()
