"""
FADE - Herramienta de Financiación (Versión Producción Lite)
Solo incluye: Dashboard Público, Gestión Convocatorias, Análisis Compatibilidad
"""

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import os
import json
from datetime import datetime
import logging

# Importar utilidades necesarias
from utils import financing_dashboard
from utils import pdf_processor
from utils.convocatoria_extractor_updated import ConvocatoriaExtractor
from utils.bdns_scraper import BDNSScraper
from utils.compatibility_analyzer import CompatibilityAnalyzer

# Configuración
from config import Config

# Inicializar Flask
app = Flask(__name__)
app.config.from_object(Config)

# ============================================================================
# FILTROS PERSONALIZADOS DE JINJA2
# ============================================================================

@app.template_filter('format_importe')
def format_importe_filter(valor):
    """
    Filtro Jinja2 para formatear importes al estilo español.
    Formato: 15.000,00 € (punto para miles, coma para decimales, 2 decimales)
    """
    if not valor or valor == 'null' or valor == 'nan':
        return 'No especificado'

    try:
        # Convertir a float
        numero = float(valor)

        # Formatear con separador de miles español (punto) y decimales (coma)
        # Formatear primero con punto decimal estándar
        formatted = f"{numero:,.2f}"

        # Intercambiar coma y punto para formato español
        # En formato US: 1,234.56 -> En formato ES: 1.234,56
        formatted = formatted.replace(',', 'TEMP')  # Guardar comas temporalmente
        formatted = formatted.replace('.', ',')      # Punto decimal → coma
        formatted = formatted.replace('TEMP', '.')   # Comas de miles → puntos

        return f"{formatted} €"
    except (ValueError, TypeError):
        return 'No especificado'

# Crear directorio de logs si no existe
log_dir = app.config.get('LOG_DIR', 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializar componentes
convocatoria_extractor = ConvocatoriaExtractor()
bdns_scraper = BDNSScraper()
compatibility_analyzer = CompatibilityAnalyzer()


# ============================================================================
# DECORADOR DE AUTENTICACIÓN
# ============================================================================

def login_required(f):
    """Decorador para proteger rutas de administración"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# RUTAS DE AUTENTICACIÓN
# ============================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login para administradores"""
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            session.permanent = True
            logger.info("Admin login exitoso")
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('gestionar_convocatorias'))
        else:
            logger.warning("Intento de login fallido")
            return render_template('admin_login.html', error="Contraseña incorrecta")
    
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """Cerrar sesión de administrador"""
    session.pop('admin_logged_in', None)
    logger.info("Admin logout")
    return redirect(url_for('dashboard'))


# ============================================================================
# MÓDULO 1: DASHBOARD PÚBLICO DE PROGRAMAS
# ============================================================================

@app.route('/')
@app.route('/financiacion/dashboard')
def dashboard():
    """Dashboard público de programas de financiación"""
    try:
        # Obtener estadísticas
        stats = financing_dashboard.get_financing_stats()
        
        # Obtener opciones para filtros
        filter_options = financing_dashboard.get_financing_filter_options()
        
        # Obtener todos los programas inicialmente
        programas = financing_dashboard.load_all_financing_programs()
        
        return render_template(
            'financiacion_dashboard.html',
            stats=stats,
            filter_options=filter_options,
            programas=programas
        )
    except Exception as e:
        logger.error(f"Error en dashboard: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/programas-financiacion', methods=['GET'])
def get_programas():
    """API para obtener programas con filtros"""
    try:
        # Obtener parámetros de filtro
        organismo = request.args.get('organismo')
        tipo_ayuda = request.args.get('tipo_ayuda')
        ambito = request.args.get('ambito')
        beneficiario = request.args.get('beneficiario')
        sector = request.args.get('sector')
        tipo_proyecto = request.args.get('tipo_proyecto')
        origen_fondos = request.args.get('origen_fondos')
        estado = request.args.get('estado')
        search_term = request.args.get('search')
        bdns = request.args.get('bdns')

        # Cargar programas con filtros
        programas = financing_dashboard.load_financing_programs(
            organismo=organismo,
            tipo_ayuda=tipo_ayuda,
            ambito=ambito,
            beneficiario=beneficiario,
            sector=sector,
            tipo_proyecto=tipo_proyecto,
            origen_fondos=origen_fondos,
            estado=estado,
            search_term=search_term,
            bdns=bdns
        )
        
        return jsonify({
            'success': True,
            'programas': programas,
            'total': len(programas)
        })
        
    except Exception as e:
        logger.error(f"Error al obtener programas: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/financiacion/programa/<programa_id>')
def detalle_programa(programa_id):
    """Vista de detalle de un programa de financiación"""
    try:
        # Obtener el programa por ID
        programa = financing_dashboard.get_programa_by_id(programa_id)
        
        if not programa:
            return render_template('404.html'), 404
        
        return render_template('programa_detalle.html', programa=programa)
        
    except Exception as e:
        logger.error(f"Error al obtener detalle del programa: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


# ============================================================================
# MÓDULO 2: GESTIÓN DE CONVOCATORIAS (ADMIN)
# ============================================================================

@app.route('/financiacion/gestionar-convocatorias')
@login_required
def gestionar_convocatorias():
    """Panel de gestión de convocatorias (solo admin)"""
    try:
        return render_template('financiacion_gestionar.html')
    except Exception as e:
        logger.error(f"Error en gestión convocatorias: {str(e)}")
        return jsonify({'error': 'Error al cargar gestión'}), 500


@app.route('/financiacion/editar-convocatorias')
@login_required
def editar_convocatorias():
    """Panel de edición manual de convocatorias (solo admin)"""
    try:
        # Obtener opciones para filtros
        filter_options = financing_dashboard.get_financing_filter_options()
        return render_template('financiacion_editar.html', filter_options=filter_options)
    except Exception as e:
        logger.error(f"Error en edición convocatorias: {str(e)}")
        return jsonify({'error': 'Error al cargar edición'}), 500


@app.route('/api/extraer-convocatoria', methods=['POST'])
@login_required
def extraer_convocatoria():
    """Extraer información de convocatoria con Gemini AI"""
    try:
        # Obtener datos adicionales del formulario
        codigo_bdns = None
        fecha_publicacion = None
        url_bdns = None
        convocatoria_url = None
        bases_reguladoras_url = None
        
        # Intentar obtener datos como JSON o como form data
        if request.is_json:
            data = request.get_json()
            texto_convocatoria = data.get('texto')
            codigo_bdns = data.get('codigo_bdns')
            fecha_publicacion = data.get('fecha_publicacion')
            url_bdns = data.get('url_bdns')
            convocatoria_url = data.get('convocatoria_url')
            bases_reguladoras_url = data.get('bases_reguladoras_url')
        else:
            # Datos de formulario
            texto_convocatoria = request.form.get('convocatoria_text')
            codigo_bdns = request.form.get('codigo_bdns')
            fecha_publicacion = request.form.get('fecha_publicacion')
            url_bdns = request.form.get('url_bdns')
            convocatoria_url = request.form.get('convocatoria_url')
            bases_reguladoras_url = request.form.get('bases_reguladoras_url')
            
            # Si viene un PDF, extraer el texto
            if 'convocatoria_pdf' in request.files:
                pdf_file = request.files['convocatoria_pdf']
                if pdf_file and pdf_file.filename:
                    # Guardar temporalmente el PDF
                    import tempfile
                    import os
                    
                    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                    pdf_file.save(temp_pdf.name)
                    temp_pdf.close()
                    
                    # Extraer texto del PDF
                    texto_convocatoria = pdf_processor.extraer_texto_pdf(temp_pdf.name)
                    
                    # Limpiar archivo temporal
                    try:
                        os.unlink(temp_pdf.name)
                    except:
                        pass
        
        if not texto_convocatoria:
            return jsonify({'success': False, 'error': 'No se proporcionó texto de la convocatoria'}), 400
        
        # Extraer información con Gemini, pasando los parámetros adicionales
        resultado = convocatoria_extractor.extract_convocatoria_info(
            texto_convocatoria,
            codigo_bdns=codigo_bdns,
            fecha_publicacion=fecha_publicacion,
            url_bdns=url_bdns,
            convocatoria_url=convocatoria_url,
            bases_reguladoras_url=bases_reguladoras_url
        )
        
        # Verificar si hay error
        if 'error' in resultado:
            return jsonify({
                'success': False,
                'error': resultado.get('error', 'Error desconocido')
            }), 500
        
        # Verificar duplicados
        try:
            programas_existentes = financing_dashboard.load_all_financing_programs()
            duplicados = convocatoria_extractor.verificar_duplicados(resultado, programas_existentes)
        except Exception as e:
            logger.warning(f"Error al verificar duplicados: {str(e)}")
            duplicados = []
        
        logger.info("Extracción de convocatoria exitosa con Gemini")
        return jsonify({
            'success': True,
            'data': resultado,
            'validation': {
                'duplicados': duplicados
            }
        })
        
    except Exception as e:
        logger.error(f"Error en extracción: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/obtener-info-bdns', methods=['POST'])
@login_required
def obtener_info_bdns():
    """Scraping de BDNS con Selenium"""
    try:
        data = request.get_json()
        url_o_codigo = data.get('url_bdns') or data.get('codigo_bdns')
        
        if not url_o_codigo:
            return jsonify({'success': False, 'error': 'No se proporcionó código BDNS o URL'}), 400
        
        # Extraer código BDNS de la URL si es necesario
        from utils.bdns_scraper import BDNSScraper
        codigo_bdns = BDNSScraper.extraer_codigo_bdns(url_o_codigo)
        
        if not codigo_bdns:
            return jsonify({'success': False, 'error': 'No se pudo extraer el código BDNS de la URL proporcionada'}), 400
        
        # Ejecutar scraping
        info_bdns = bdns_scraper.obtener_info_convocatoria(codigo_bdns)
        
        if not info_bdns or not info_bdns.get('success'):
            return jsonify({'success': False, 'error': info_bdns.get('error', 'No se encontró información')}), 404
        
        logger.info(f"Scraping BDNS exitoso para código: {codigo_bdns}")
        return jsonify({
            'success': True,
            'codigo_bdns': info_bdns.get('codigo_bdns'),
            'url_bdns': info_bdns.get('url_bdns'),  # URL de la página BDNS
            'bases_reguladoras_url': info_bdns.get('bases_reguladoras_url'),  # URL del PDF de bases
            'documentos': info_bdns.get('documentos', [])
        })
        
    except Exception as e:
        logger.error(f"Error en scraping BDNS: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/extraer-desde-pdf-bdns', methods=['POST'])
@login_required
def extraer_desde_pdf_bdns():
    """Extraer información desde PDF descargado por el scraper de BDNS"""
    try:
        data = request.get_json()
        pdf_path = data.get('pdf_path')
        
        if not pdf_path:
            return jsonify({'success': False, 'error': 'No se proporcionó la ruta del PDF'}), 400
        
        # Verificar que el archivo existe
        import os
        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'error': 'El archivo PDF no existe'}), 400
        
        # Extraer texto del PDF usando la función del módulo pdf_processor
        texto_pdf = pdf_processor.extraer_texto_pdf(pdf_path)
        
        if not texto_pdf:
            return jsonify({'success': False, 'error': 'No se pudo extraer texto del PDF'}), 400
        
        logger.info(f"Extracción de texto desde PDF exitosa: {len(texto_pdf)} caracteres")
        return jsonify({
            'success': True,
            'texto_extraido': texto_pdf
        })
        
    except Exception as e:
        logger.error(f"Error en extracción PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/guardar-programa', methods=['POST'])
@login_required
def guardar_programa():
    """Guardar nuevo programa de financiación"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        campos_requeridos = ['nombre', 'organismo', 'tipo_ayuda']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({'success': False, 'error': f'Falta el campo: {campo}'}), 400
        
        # Guardar en base de datos
        programa_id = financing_dashboard.agregar_programa(data)
        
        logger.info(f"Programa guardado exitosamente: {programa_id}")
        return jsonify({
            'success': True,
            'programa_id': programa_id,
            'message': 'Programa guardado exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error al guardar programa: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/programa/<programa_id>', methods=['GET'])
@login_required
def obtener_programa(programa_id):
    """Obtener datos de un programa específico"""
    try:
        programa = financing_dashboard.get_programa_by_id(programa_id)
        
        if not programa:
            return jsonify({'success': False, 'error': 'Programa no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'programa': programa
        })
        
    except Exception as e:
        logger.error(f"Error al obtener programa: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/programa/<programa_id>', methods=['PUT'])
@login_required
def actualizar_programa(programa_id):
    """Actualizar un programa existente"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        campos_requeridos = ['nombre', 'organismo', 'tipo_ayuda']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({'success': False, 'error': f'Falta el campo: {campo}'}), 400
        
        # Actualizar en base de datos
        success = financing_dashboard.actualizar_programa(programa_id, data)
        
        if not success:
            return jsonify({'success': False, 'error': 'Programa no encontrado'}), 404
        
        logger.info(f"Programa actualizado exitosamente: {programa_id}")
        return jsonify({
            'success': True,
            'message': 'Programa actualizado exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error al actualizar programa: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/programa/<programa_id>', methods=['DELETE'])
@login_required
def eliminar_programa(programa_id):
    """Eliminar un programa"""
    try:
        # Eliminar de base de datos
        success = financing_dashboard.eliminar_programa(programa_id)
        
        if not success:
            return jsonify({'success': False, 'error': 'Programa no encontrado'}), 404
        
        logger.info(f"Programa eliminado exitosamente: {programa_id}")
        return jsonify({
            'success': True,
            'message': 'Programa eliminado exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error al eliminar programa: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MÓDULO 3: ANÁLISIS DE COMPATIBILIDAD
# ============================================================================

@app.route('/financiacion/analizar-compatibilidad')
def analizar_compatibilidad():
    """Vista para análisis de compatibilidad proyecto-convocatoria"""
    try:
        # Verificar si hay un result_id en la URL
        result_id = request.args.get('result_id')
        
        if result_id:
            # Cargar el resultado del análisis
            result = compatibility_analyzer.get_result(result_id)
            if result:
                return render_template('financiacion_adecuacion.html', result=result)
            else:
                logger.warning(f"No se encontró resultado para ID: {result_id}")
        
        # Si no hay result_id o no se encontró, mostrar el formulario vacío
        return render_template('financiacion_adecuacion.html')
    except Exception as e:
        logger.error(f"Error en análisis compatibilidad: {str(e)}")
        return jsonify({'error': 'Error al cargar análisis'}), 500


@app.route('/api/analizar-compatibilidad', methods=['POST'])
def analizar_compatibilidad_api():
    """API para análisis de compatibilidad con Gemini AI"""
    try:
        # Obtener datos del proyecto
        datos_empresa = {
            'nombre': request.form.get('empresa_nombre'),
            'cnae': request.form.get('empresa_cnae'),
            'descripcion_proyecto': request.form.get('proyecto_descripcion'),
            'presupuesto': request.form.get('presupuesto'),
            'tamano_empresa': request.form.get('tamano_empresa')
        }
        
        # Obtener convocatoria (puede ser ID o PDF)
        convocatoria_id = request.form.get('convocatoria_id')
        pdf_file = request.files.get('convocatoria_pdf')  # Cambiado de pdf_convocatoria a convocatoria_pdf
        
        # Si es un ID de convocatoria, no está implementado aún
        if convocatoria_id:
            return jsonify({'success': False, 'error': 'Análisis por ID de convocatoria no implementado aún'}), 400
        
        if not pdf_file:
            return jsonify({'success': False, 'error': 'Debe proporcionar un PDF de la convocatoria'}), 400
        
        # Realizar análisis con Gemini AI (pasarle el PDF directamente)
        resultado = compatibility_analyzer.analyze_compatibility(
            empresa_nombre=datos_empresa.get('nombre', ''),
            empresa_cnae=datos_empresa.get('cnae', ''),
            proyecto_descripcion=datos_empresa.get('descripcion_proyecto', ''),
            convocatoria_pdf=pdf_file
        )
        
        # Verificar si hubo error
        if 'error' in resultado:
            logger.error(f"Error en análisis: {resultado.get('error')}")
            return jsonify({'success': False, 'error': resultado.get('error')}), 400
        
        # Si todo fue bien, resultado contiene {'success': True, 'result_id': '...'}
        logger.info("Análisis de compatibilidad completado")
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Error en análisis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# RUTAS DE SALUD Y MONITORIZACIÓN
# ============================================================================

@app.route('/health')
def health_check():
    """Endpoint de health check para monitorización"""
    try:
        # Verificar que la base de datos esté accesible
        programas = financing_dashboard.get_total_programas()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'total_programas': programas,
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error 500: {str(error)}")
    return render_template('500.html'), 500


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    # Solo para desarrollo local
    app.run(debug=False, host='0.0.0.0', port=5000)
