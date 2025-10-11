"""
Utilidades mejoradas para el dashboard de financiación
Incluye mejoras en el buscador y simplificación de filtros
"""
import os
import json
from datetime import datetime

# Mapeos para simplificar los filtros
ORGANISMO_GRUPOS = {
    'CDTI': ['CDTI', 'CDTI E.P.E', 'CDTI Innovación', 'CDTI (con fondos FEMPA)', 'CDTI (en colaboración con AEI)'],
    'IDEPA/Asturias': ['SEKUENS', 'SEPEPA', 'Consejería', 'Principado de Asturias', 'IDEPA', 
                       'Ayuntamiento de Gijón', 'Ayuntamiento de Avilés', 'Sociedad de Desarrollo'],
    'Europea': ['EUIPO'],
    'Financieras': ['Asturgar', 'SRP', 'MicroBank', 'TORSA CAPITAL'],
    'Red.es': ['Red.es'],
    'Ministerios': ['Ministerio de Hacienda', 'Ministerio'],
    'EOI': ['EOI', 'Escuela de Organización Industrial'],
    'Otros': []
}

TIPO_AYUDA_GRUPOS = {
    'Subvención': ['Subvención', 'Subvención a fondo perdido', 'Subvención (concesión directa)', 
                   'Subvención (Bono Digital)', 'Subvención (Reembolso/Bonos)', 
                   'Entregas dinerarias sin contraprestación'],
    'Préstamo/Crédito': ['Préstamo', 'Préstamo participativo', 'Préstamo (con aval)', 
                         'Ayuda Parcialmente Reembolsable'],
    'Capital Riesgo/Inversión': ['Capital Riesgo', 'Capital Riesgo / Coinversión', 
                                 'Capital Riesgo, Préstamos Participativos', 
                                 'Capital Semilla, Préstamo Participativo, Capital Riesgo'],
    'Aval/Garantía': ['Aval', 'Aval (para anticipo de subvención)'],
    'Ayuda en especie': ['Ayuda en especie', 'Ayuda en especie (Asesoramiento)', 
                        'Ayuda en especie (Plan de Aceleración)']
}

SECTOR_GRUPOS = {
    'General/Multisectorial': ['General', 'Multisectorial', 'General (con exclusiones)', 
                               'Tecnológico / Innovador (Multisectorial)', 
                               'Multisectorial (con exclusiones)', 'Multisectorial (Base Tecnológica)',
                               'General (Propiedad Intelectual)', 'General (Proyectos viables)'],
    'I+D+i / Tecnología': ['Tecnologías prioritarias Cervera', 'Base Tecnológica', 'TIC', 
                           'Biotecnología', 'Biomedicina', 'Nanotecnología', 'Fotónica',
                           'Tecnología avanzada', 'Innovación', 'Industrias culturales',
                           'Servicios avanzados', 'I+D'],
    'Industria/Manufactura': ['Industrial', 'Servicios conexos a la industria', 
                              'Industrias transformadoras', 'Infraestructura Industrial',
                              'Industria Alimentaria', 'Industria Manufacturera'],
    'Salud/Sanidad': ['Salud', 'Salud de Vanguardia', 'Salud Digital', 'Salud Animal'],
    'Agroalimentación/Pesca': ['Pesca', 'Acuicultura', 'Agroecología', 'Mejora genética',
                               'Transformación y Comercialización Pesca/Acuicultura',
                               'Sanidad animal'],
    'Energía/Sostenibilidad': ['Energías renovables', 'Movilidad Sostenible', 'Energía Limpia',
                                'Economía Circular', 'Descontaminación', 'Construcción Sostenible'],
    'Aeroespacial': ['Aeroespacial'],
    'Turismo/Hostelería': ['Turismo', 'Establecimientos turísticos innovadores'],
    'Cultura/Creativo': ['Artesanía', 'Ejes Estratégicos Gijón Transforma (Creativo'],
    'Transporte/Logística': ['Transporte Aéreo', 'Logística Inteligente', 'Electromovilidad',
                             'Vehículos Autónomos'],
    'Otros': []
}

BENEFICIARIO_GRUPOS = {
    'Todas las empresas': ['Empresas', 'Empresas (individualmente)', 'Sociedades', 'Cooperativas'],
    'PYME': ['PYMES', 'PYMES Españolas', 'Pequeñas empresas', 'Medianas Empresas', 
             'MIDCAPS', 'Microempresas', 'Micropymes'],
    'Gran Empresa': ['Gran Empresa', 'Grandes Empresas'],
    'Startups/EBT': ['Startups', 'Empresas de Base Tecnológica', 'EBT', 
                     'Pequeñas empresas innovadoras', 'Empresas emergentes'],
    'Autónomos': ['Autónomos', 'Personas físicas emprendedoras'],
    'Emprendedores': ['Emprendedores', 'Emprendedores innovadores', 
                      'Mujeres emprendedoras y empresarias'],
    'Agrupaciones': ['Agrupaciones de empresas', 'Agrupaciones de 2-6 empresas', 
                     'Agrupaciones de 3-8 empresas'],
    'Sector Público': ['Ayuntamientos', 'Entidades Locales', 'Sector Público', 
                       'Corporaciones', 'Sociedades públicas'],
    'Otros': ['Particulares', 'Comunidades Propietarios', 'Entidades sin ánimo de lucro',
              'Asociaciones', 'Artesanos']
}

def normalizar_organismo(organismo):
    """Normaliza un organismo a su grupo simplificado"""
    if not organismo:
        return 'Otros'
    
    for grupo, valores in ORGANISMO_GRUPOS.items():
        for valor in valores:
            if valor.lower() in organismo.lower():
                return grupo
    return 'Otros'

def normalizar_tipo_ayuda(tipo_ayuda):
    """Normaliza un tipo de ayuda a su grupo simplificado"""
    if not tipo_ayuda:
        return 'Otros'
    
    for grupo, valores in TIPO_AYUDA_GRUPOS.items():
        for valor in valores:
            if valor.lower() in tipo_ayuda.lower():
                return grupo
    return 'Otros'

def normalizar_sector(sector):
    """Normaliza un sector a su macro-sector"""
    if not sector:
        return 'Otros'
    
    sector_lower = sector.lower()
    
    for grupo, valores in SECTOR_GRUPOS.items():
        for valor in valores:
            if valor.lower() in sector_lower or sector_lower in valor.lower():
                return grupo
    return 'Otros'

def normalizar_beneficiario(beneficiario):
    """Normaliza un beneficiario a su grupo simplificado"""
    if not beneficiario:
        return 'Otros'
    
    beneficiario_lower = beneficiario.lower()
    
    for grupo, valores in BENEFICIARIO_GRUPOS.items():
        for valor in valores:
            if valor.lower() in beneficiario_lower or beneficiario_lower in valor.lower():
                return grupo
    return 'Otros'

def buscar_en_programa(programa, search_term):
    """
    Busca un término en todos los campos relevantes de un programa
    
    Args:
        programa: Diccionario con los datos del programa
        search_term: Término a buscar (en minúsculas)
    
    Returns:
        True si se encuentra el término, False en caso contrario
    """
    search_term = search_term.lower()
    
    # Buscar en campos de texto principales
    campos_texto = ['nombre', 'organismo', 'tipo_proyecto', 'resumen_breve', 'descripcion_detallada']
    for campo in campos_texto:
        if campo in programa and programa[campo] and search_term in str(programa[campo]).lower():
            return True
    
    # Buscar en listas (arrays)
    campos_lista = ['beneficiarios', 'sectores', 'requisitos', 'tags']
    for campo in campos_lista:
        if campo in programa and isinstance(programa[campo], list):
            for item in programa[campo]:
                if search_term in str(item).lower():
                    return True
    
    # Buscar en BDNS si es numérico
    if 'codigo_bdns' in programa and programa['codigo_bdns']:
        bdns_str = str(programa['codigo_bdns']).lower()
        if search_term in bdns_str or bdns_str.startswith(search_term):
            return True
    
    return False

def load_all_financing_programs():
    """Carga todos los programas de financiación desde el archivo JSON"""
    try:
        # Obtener la ruta al archivo JSON
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, 'data', 'programas_financiacion.json')
        
        # Verificar que el archivo existe
        if not os.path.exists(json_path):
            print(f"ERROR: El archivo de programas de financiación no existe en la ruta: {json_path}")
            return []
            
        # Cargar el JSON
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Verificar la estructura del JSON
        if 'programas' not in data:
            print("ERROR: El archivo JSON no contiene la clave 'programas'")
            return []
            
        programas = data['programas']
        
        # Procesar fechas para cada programa
        for programa in programas:
            # Procesar estado de convocatoria
            if 'convocatoria' in programa:
                # Si no hay fechas, establecer estado basado en el campo 'estado'
                if not programa['convocatoria'].get('fecha_apertura') and not programa['convocatoria'].get('fecha_cierre'):
                    pass
                else:
                    fecha_apertura = programa['convocatoria'].get('fecha_apertura')
                    fecha_cierre = programa['convocatoria'].get('fecha_cierre')
                    
                    fecha_apertura_dt = None
                    fecha_cierre_dt = None
                    
                    if fecha_apertura:
                        try:
                            fecha_apertura_dt = datetime.strptime(fecha_apertura, '%Y-%m-%d %H:%M:%S')
                        except (ValueError, TypeError):
                            fecha_apertura_dt = None
                    
                    if fecha_cierre:
                        try:
                            fecha_cierre_dt = datetime.strptime(fecha_cierre, '%Y-%m-%d %H:%M:%S')
                        except (ValueError, TypeError):
                            fecha_cierre_dt = None
                    
                    now = datetime.now()
                    
                    if fecha_cierre_dt and fecha_cierre_dt < now:
                        programa['convocatoria']['estado'] = 'Cerrada'
                    elif fecha_apertura_dt and fecha_apertura_dt > now:
                        programa['convocatoria']['estado'] = 'Pendiente'
                    else:
                        programa['convocatoria']['estado'] = 'Abierta'
            
            # Añadir campos normalizados para los filtros
            programa['organismo_grupo'] = normalizar_organismo(programa.get('organismo'))
            programa['tipo_ayuda_grupo'] = normalizar_tipo_ayuda(programa.get('tipo_ayuda'))
            
            if 'sectores' in programa:
                programa['sectores_grupos'] = list(set([normalizar_sector(s) for s in programa['sectores']]))
            else:
                programa['sectores_grupos'] = []
            
            if 'beneficiarios' in programa:
                programa['beneficiarios_grupos'] = list(set([normalizar_beneficiario(b) for b in programa['beneficiarios']]))
            else:
                programa['beneficiarios_grupos'] = []
                    
            for key in ['presupuesto_minimo', 'presupuesto_maximo', 'importe_maximo']:
                if key in programa.get('financiacion', {}) and programa['financiacion'][key] not in [None, '', 'nan', 'No especificado']:
                    try:
                        programa['financiacion'][key] = float(programa['financiacion'][key])
                    except (ValueError, TypeError):
                        programa['financiacion'][key] = None
            
            if 'codigo_bdns' in programa and programa['codigo_bdns'] not in [None, '', 'nan', 'No especificado']:
                try:
                    if isinstance(programa['codigo_bdns'], (int, float)):
                        programa['codigo_bdns'] = int(programa['codigo_bdns'])
                    elif isinstance(programa['codigo_bdns'], str) and '.' in programa['codigo_bdns']:
                        programa['codigo_bdns'] = int(float(programa['codigo_bdns']))
                except (ValueError, TypeError):
                    pass
        
        return programas
    except Exception as e:
        print(f"Error al cargar programas de financiación: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def load_financing_programs(organismo=None, tipo_ayuda=None, ambito=None, beneficiario=None, 
                           sector=None, estado=None, presupuesto_min=None, presupuesto_max=None, 
                           search_term=None, bdns=None):
    """Carga y filtra programas de financiación según los criterios especificados"""
    try:
        programas = load_all_financing_programs()
        
        if organismo:
            programas = [p for p in programas if p.get('organismo_grupo') == organismo]
        
        if tipo_ayuda:
            programas = [p for p in programas if p.get('tipo_ayuda_grupo') == tipo_ayuda]
        
        if ambito:
            programas = [p for p in programas if p.get('ambito') and ambito.lower() in p['ambito'].lower()]
        
        if beneficiario:
            programas = [p for p in programas if beneficiario in p.get('beneficiarios_grupos', [])]
        
        if sector:
            programas = [p for p in programas if sector in p.get('sectores_grupos', [])]
        
        if estado:
            programas = [p for p in programas if 'convocatoria' in p and p['convocatoria'].get('estado') and estado.lower() in p['convocatoria']['estado'].lower()]
        
        if presupuesto_min is not None:
            programas = [p for p in programas if 'financiacion' in p and 
                         p['financiacion'].get('presupuesto_minimo') is not None and 
                         p['financiacion']['presupuesto_minimo'] != 'nan' and
                         float(p['financiacion']['presupuesto_minimo']) >= presupuesto_min]
        
        if presupuesto_max is not None:
            programas = [p for p in programas if 'financiacion' in p and 
                         p['financiacion'].get('presupuesto_maximo') is not None and 
                         p['financiacion']['presupuesto_maximo'] != 'nan' and
                         float(p['financiacion']['presupuesto_maximo']) <= presupuesto_max]
        
        if bdns:
            bdns_str = str(bdns).lower()
            programas = [p for p in programas if p.get('codigo_bdns') and 
                        str(p['codigo_bdns']).lower().startswith(bdns_str)]
        
        if search_term:
            programas = [p for p in programas if buscar_en_programa(p, search_term)]
        
        return programas
    except Exception as e:
        print(f"Error al filtrar programas de financiación: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def get_financing_program_by_id(programa_id):
    """Obtiene un programa de financiación por su ID"""
    try:
        programas = load_all_financing_programs()
        for programa in programas:
            if programa.get('id') == programa_id:
                if 'codigo_bdns' in programa and programa['codigo_bdns']:
                    try:
                        if isinstance(programa['codigo_bdns'], (int, float)):
                            programa['codigo_bdns'] = int(programa['codigo_bdns'])
                        elif isinstance(programa['codigo_bdns'], str) and '.' in programa['codigo_bdns']:
                            programa['codigo_bdns'] = int(float(programa['codigo_bdns']))
                    except (ValueError, TypeError):
                        pass
                return programa
        return None
    except Exception as e:
        print(f"Error al buscar programa por ID: {e}")
        return None

def get_financing_stats():
    """Obtiene estadísticas generales sobre los programas de financiación"""
    try:
        programas = load_all_financing_programs()
        
        total_programas = len(programas)
        
        estados = {'Abierta': 0, 'Cerrada': 0, 'Pendiente': 0}
        for p in programas:
            if 'convocatoria' in p and 'estado' in p['convocatoria']:
                estado = p['convocatoria']['estado']
                if 'Abierta' in estado:
                    estados['Abierta'] += 1
                elif 'Cerrada' in estado:
                    estados['Cerrada'] += 1
                elif 'Pendiente' in estado:
                    estados['Pendiente'] += 1
        
        tipos_ayuda = {}
        for p in programas:
            grupo = p.get('tipo_ayuda_grupo', 'Otros')
            tipos_ayuda[grupo] = tipos_ayuda.get(grupo, 0) + 1
        
        ambitos = {}
        for p in programas:
            if 'ambito' in p:
                ambito = p['ambito']
                ambitos[ambito] = ambitos.get(ambito, 0) + 1
        
        organismos = {}
        for p in programas:
            grupo = p.get('organismo_grupo', 'Otros')
            organismos[grupo] = organismos.get(grupo, 0) + 1
        
        return {
            'total': total_programas,
            'estados': estados,
            'tipos_ayuda': tipos_ayuda,
            'ambitos': ambitos,
            'organismos': organismos
        }
    except Exception as e:
        print(f"Error al generar estadísticas de financiación: {e}")
        import traceback
        print(traceback.format_exc())
        return {
            'total': 0,
            'estados': {},
            'tipos_ayuda': {},
            'ambitos': {},
            'organismos': {}
        }

def get_financing_filter_options():
    """Obtiene las opciones SIMPLIFICADAS disponibles para los filtros del dashboard"""
    try:
        programas = load_all_financing_programs()
        
        organismos = set()
        tipos_ayuda = set()
        ambitos = set()
        beneficiarios = set()
        sectores = set()
        estados = set()
        
        for p in programas:
            if 'organismo_grupo' in p:
                organismos.add(p['organismo_grupo'])
            
            if 'tipo_ayuda_grupo' in p:
                tipos_ayuda.add(p['tipo_ayuda_grupo'])
            
            if 'ambito' in p:
                ambitos.add(p['ambito'])
            
            if 'beneficiarios_grupos' in p:
                for b in p['beneficiarios_grupos']:
                    beneficiarios.add(b)
            
            if 'sectores_grupos' in p:
                for s in p['sectores_grupos']:
                    sectores.add(s)
            
            if 'convocatoria' in p and 'estado' in p['convocatoria']:
                estados.add(p['convocatoria']['estado'])
        
        def ordenar_con_otros_al_final(lista):
            lista_ordenada = sorted([x for x in lista if x != 'Otros'])
            if 'Otros' in lista:
                lista_ordenada.append('Otros')
            return lista_ordenada
        
        return {
            'organismos': ordenar_con_otros_al_final(list(organismos)),
            'tipos_ayuda': ordenar_con_otros_al_final(list(tipos_ayuda)),
            'ambitos': sorted(list(ambitos)),
            'beneficiarios': ordenar_con_otros_al_final(list(beneficiarios)),
            'sectores': ordenar_con_otros_al_final(list(sectores)),
            'estados': sorted(list(estados))
        }
    except Exception as e:
        print(f"Error al obtener opciones de filtro: {e}")
        import traceback
        print(traceback.format_exc())
        return {
            'organismos': [],
            'tipos_ayuda': [],
            'ambitos': [],
            'beneficiarios': [],
            'sectores': [],
            'estados': []
        }
