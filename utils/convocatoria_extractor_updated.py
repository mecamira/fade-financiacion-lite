"""
Módulo para extraer información estructurada de convocatorias de financiación
usando la API de Gemini 2.5 Flash Preview
"""
import os
import json
import re
import datetime
import traceback
from typing import Dict, Any, Optional, List

# Importar configuración y utilidades de Google API
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

# Para procesar PDFs
import PyPDF2
import io

class ConvocatoriaExtractor:
    """Clase para extraer información estructurada de convocatorias usando Gemini API"""
    
    def __init__(self):
        # Obtener clave API siguiendo el mismo enfoque que en gemini_advisor.py
        self.api_key = os.environ.get("GEMINI_API_KEY")
        
        # Si no hay API key en el entorno, usar la clave proporcionada para pruebas
        if not self.api_key:
            self.api_key = "AIzaSyBCrR9UZMg8bEHi1mzcmcpO9N6juTlbH4Q"
        
        # Si aún no hay API key, intentamos cargarla desde un archivo de configuración
        if not self.api_key:
            try:
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         'config', 'api_keys.json')
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('gemini_api_key')
            except Exception as e:
                print(f"Error al cargar clave API de Gemini: {e}")
        
        # Configurar cliente de Gemini
        genai.configure(api_key=self.api_key)
        # Usar el modelo Gemini 2.5 Flash Preview
        self.model_name = "models/gemini-2.5-flash"
        self.model = genai.GenerativeModel(self.model_name)
        print(f"Usando el modelo: {self.model_name}")
        
        # Prompt para extracción de información
        self._extraction_prompt = self._get_extraction_prompt()
    
    def _get_extraction_prompt(self) -> str:
        """Obtener el prompt para extraer información de convocatorias"""
        return f"""
        Eres un asistente especializado en extraer información estructurada de convocatorias de ayudas y subvenciones para empresas. Tu tarea es analizar el texto proporcionado y generar un objeto JSON con campos específicos.

        IMPORTANTE: Debes producir SOLO el objeto JSON, sin texto introductorio ni conclusiones. El JSON debe ser válido y seguir exactamente la estructura definida a continuación.

        ESTRUCTURA JSON REQUERIDA:
        {{
          "id": "identificador-unico-basado-en-nombre", 
          "nombre": "Nombre completo de la convocatoria",
          "organismo": "Organismo gestor",
          "tipo_ayuda": "Tipo de ayuda (Subvención, Préstamo, etc.)",
          "ambito": "Ámbito geográfico (Nacional, Comunidad Autónoma, etc.)",
          "beneficiarios": ["Lista", "de", "beneficiarios"],
          "sectores": ["Lista", "de", "sectores", "aplicables"],
          "tipo_proyecto": "Tipo de proyecto financiable",
          "convocatoria": {{
            "estado": "Estado (Abierta, Cerrada, Pendiente)",
            "fecha_apertura": "YYYY-MM-DD (null si no se especifica)",
            "fecha_cierre": "YYYY-MM-DD (null si no se especifica)"
          }},
          "financiacion": {{
            "intensidad": "% o descripción de la intensidad",
            "importe_maximo": "Cantidad máxima (numérico si es posible, sin símbolos)",
            "presupuesto_minimo": "Presupuesto mínimo (numérico si es posible, sin símbolos)",
            "presupuesto_maximo": "Presupuesto máximo (numérico si es posible, sin símbolos)"
          }},
          "requisitos": ["Lista", "de", "requisitos", "principales"],
          "resumen_breve": "Resumen breve y conciso de la convocatoria",
          "descripcion_detallada": "Descripción más detallada (2-3 frases)",
          "tags": ["Palabras", "clave", "relevantes"],
          "enlaces": {{
            "url_bdns": "URL página BDNS (null si no disponible)",
            "convocatoria": "URL PDF convocatoria (null si no disponible)",
            "bases_reguladoras": "URL PDF bases reguladoras (null si no disponible)"
          }},
          "codigo_bdns": "Código BDNS (numérico si es posible, null si no disponible)"
        }}

        INSTRUCCIONES ESPECÍFICAS:
        1. Para "id": Genera un identificador a partir del nombre, en minúsculas, sin acentos, con guiones en lugar de espacios.
        
        2. Para fechas: 
           - Usa formato YYYY-MM-DD
           - Si se menciona un plazo en días (ej: "20 días hábiles desde publicación"), utiliza la fecha de publicación proporcionada para calcular una fecha aproximada. Por ejemplo, 20 días hábiles son aproximadamente 28 días naturales.
           - Si no se indica fecha de apertura, asume que es la misma que la fecha de publicación.
        
        3. Para "estado": 
           - Debe ser "Abierta" si la fecha de cierre es posterior a la fecha actual
           - "Cerrada" si la fecha de cierre es anterior a la fecha actual
           - "Pendiente" si la fecha de apertura es posterior a la fecha actual
           - Si no hay fechas claras, deduce el estado por el contexto
        
        4. Para listas (beneficiarios, sectores, requisitos, tags): 
           - Incluye elementos individuales, no textos largos con separadores
           - Cada elemento debe ser una frase corta y concisa
        
        5. Para campos numéricos: 
           - Extrae SOLO números sin símbolos monetarios
           - Ejemplo: para "500.000€" escribe sólo "500000"
           - Redondea a enteros si es necesario
        
        6. Para la intensidad: 
           - Captura porcentajes y descripciones específicas de financiación
        
        7. Para el resumen_breve: 
           - Una frase concisa (máximo 200 caracteres)
        
        8. Para la descripcion_detallada: 
           - 2-3 frases con detalles relevantes (máximo 500 caracteres)
        
        9. Si un campo no tiene información, usa null (no elimines el campo)

        10. IMPORTANTE: Evita incluir palabras sueltas o texto que no sea parte del JSON. El output SOLAMENTE debe ser el objeto JSON válido.

        NOTAS IMPORTANTES:
        - Lee DETENIDAMENTE el documento. A menudo hay información importante oculta en párrafos o secciones que podrían parecer irrelevantes.
        - Sé PRECISO en la extracción de fechas, importes y porcentajes. Son cruciales para evaluar la adecuación de la convocatoria.
        - Sé EXHAUSTIVO en tu análisis para capturar todos los detalles relevantes del texto, especialmente requisitos, beneficiarios, tipo de proyectos y sectores.
        - VERIFICA que la información sea coherente en todo el documento.
        - ASEGÚRATE de que el JSON generado sea completamente válido y siga la estructura exacta.

        La fecha actual es {datetime.datetime.now().strftime("%Y-%m-%d")}. Si hay información sobre la fecha de publicación, usarás esta como referencia para calcular fechas. Si no hay fecha de cierre específica o si es posterior a la fecha actual, el estado debe ser "Abierta". Si la fecha de cierre es anterior a la fecha actual, el estado debe ser "Cerrada".

        Ahora, procesa el texto proporcionado sobre la convocatoria y genera SOLO el objeto JSON estructurado:
        """
    
    def extract_from_pdf(self, 
                         pdf_file,
                         codigo_bdns: Optional[str] = None,
                         fecha_publicacion: Optional[str] = None,
                         url_bdns: Optional[str] = None,
                         convocatoria_url: Optional[str] = None,
                         bases_reguladoras_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrae información estructurada desde un archivo PDF de la convocatoria
        
        Args:
            pdf_file: Archivo PDF (objeto de tipo file de Flask) 
            codigo_bdns: Código BDNS de la convocatoria (opcional)
            fecha_publicacion: Fecha de publicación en formato YYYY-MM-DD (opcional)
            url_bdns: URL de la página BDNS (opcional)
            convocatoria_url: URL del PDF de la convocatoria (opcional)
            bases_reguladoras_url: URL del PDF de bases reguladoras (opcional)
            
        Returns:
            Diccionario con la información estructurada de la convocatoria
        """
        try:
            # Leer el contenido del PDF
            pdf_text = self._extract_text_from_pdf(pdf_file)
            
            if not pdf_text:
                return {
                    "error": "No se pudo extraer texto del PDF"
                }
            
            # Una vez extraído el texto, usar el método existente para extraer información
            return self.extract_convocatoria_info(
                convocatoria_text=pdf_text,
                codigo_bdns=codigo_bdns,
                fecha_publicacion=fecha_publicacion,
                url_bdns=url_bdns,
                convocatoria_url=convocatoria_url,
                bases_reguladoras_url=bases_reguladoras_url
            )
        except Exception as e:
            print(f"Error al procesar PDF: {e}")
            traceback.print_exc()
            return {
                "error": "Error al procesar el archivo PDF",
                "details": str(e)
            }
    
    def _extract_text_from_pdf(self, pdf_file) -> str:
        """
        Extrae texto de un archivo PDF
        
        Args:
            pdf_file: Archivo PDF (objeto de tipo file de Flask)
            
        Returns:
            Texto extraído del PDF
        """
        try:
            # Leer el contenido del archivo en un buffer
            pdf_data = pdf_file.read()
            pdf_buffer = io.BytesIO(pdf_data)
            
            # Crear lector de PDF
            pdf_reader = PyPDF2.PdfReader(pdf_buffer)
            
            # Extraer texto de todas las páginas
            text = ""
            
            # Gemini 2.5 puede manejar más contexto, pero seguimos siendo prudentes
            # Incrementamos el límite de páginas a procesar
            page_limit = min(len(pdf_reader.pages), 30)
            print(f"Procesando {page_limit} páginas del PDF (de un total de {len(pdf_reader.pages)})")
            
            for page_num in range(page_limit):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text.strip() + "\n\n"
                except Exception as page_error:
                    print(f"Error al extraer texto de la página {page_num+1}: {page_error}")
                    continue
            
            # Limitar a un máximo de caracteres para evitar problemas de tokens
            # Gemini 2.5 puede manejar más contexto, por lo que ampliamos el límite
            max_length = 100000  # 100k caracteres
            if len(text) > max_length:
                print(f"Texto del PDF demasiado largo ({len(text)} caracteres), truncando a {max_length}")
                text = text[:max_length]
            
            # Limpiar texto
            text = self._clean_pdf_text(text)
            
            return text
        except Exception as e:
            print(f"Error al extraer texto del PDF: {e}")
            traceback.print_exc()
            return ""
    
    def _clean_pdf_text(self, text):
        """
        Limpia el texto extraído del PDF para mejorar la calidad
        
        Args:
            text: Texto extraído del PDF
            
        Returns:
            Texto limpio
        """
        # Eliminar caracteres no imprimibles
        text = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
        
        # Normalizar espacios y saltos de línea
        text = re.sub(r'\s+', ' ', text)  # Reemplazar múltiples espacios por uno solo
        text = re.sub(r'\n\s*\n+', '\n\n', text)  # Reducir múltiples saltos de línea a máximo dos
        
        # Eliminar líneas vacías al inicio y final
        text = text.strip()
        
        return text
    
    def _clean_malformed_json(self, json_text: str) -> str:
        """
        Intenta limpiar un JSON malformado para hacerlo válido
        
        Args:
            json_text: Texto JSON potencialmente malformado
            
        Returns:
            Texto JSON limpio
        """
        try:
            # Buscar errores comunes que rompen la sintaxis del JSON
            
            # Arreglar palabras sueltas entre elementos de array (caso velveteen)
            # Busca patrones como "]palabra[" o "]  palabra  [" o "] palabra [" etc.
            json_text = re.sub(r']\s*[a-zA-Z0-9_-]+\s*\[', '][', json_text)
            json_text = re.sub(r'"\s*[a-zA-Z0-9_-]+\s*\[', '"[', json_text)
            json_text = re.sub(r']\s*[a-zA-Z0-9_-]+\s*"', ']"', json_text)
            
            # Eliminar palabras sueltas al final de arrays
            json_text = re.sub(r'"\s*,\s*([a-zA-Z0-9_-]+)\s*\]', '"\n]', json_text)
            
            # Eliminar texto suelto entre comillas y coma
            json_text = re.sub(r'"\s+[a-zA-Z0-9_-]+\s*,\s*"', '",\n"', json_text)
            
            # Eliminar texto suelto entre comillas y corchete de cierre
            json_text = re.sub(r'"\s+[a-zA-Z0-9_-]+\s*\]', '"\n]', json_text)
            
            # Reparar llaves de cierre desplazadas
            json_text = re.sub(r'(["\]])([a-zA-Z0-9_-]+)(})', r'\1\n\3', json_text)
            
            # Caso especial para el problema "velveteen" entre elementos de array
            json_text = re.sub(r'"[^"]*"\s+velveteen\s+', '" ', json_text)
            
            # Buscar palabras sueltas después de los corchetes de cierre de un array y antes de la coma
            json_text = re.sub(r'\]\s+([a-zA-Z0-9_-]+)\s*,', '],', json_text)
            
            # Intento adicional: dividir el texto en líneas
            # y eliminar cualquier línea que no empiece con espacios seguidos de
            # uno de los caracteres válidos en JSON: {, }, [, ], ", número, true, false, null
            lines = json_text.split('\n')
            cleaned_lines = []
            for line in lines:
                # Eliminar líneas que no parecen ser parte de un JSON válido
                if re.match(r'^\s*([{\[\]},"]|true|false|null|-?\d+)', line.strip()) or not line.strip():
                    cleaned_lines.append(line)
            json_text = '\n'.join(cleaned_lines)
            
            return json_text
            
        except Exception as e:
            print(f"Error al limpiar JSON malformado: {e}")
            return json_text  # Devolvemos el texto original si hay algún error
    
    def extract_convocatoria_info(self, 
                                 convocatoria_text: str, 
                                 codigo_bdns: Optional[str] = None,
                                 fecha_publicacion: Optional[str] = None,
                                 bases_url: Optional[str] = None,
                                 convocatoria_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrae información estructurada de una convocatoria de financiación
        
        Args:
            convocatoria_text: Texto de la convocatoria
            codigo_bdns: Código BDNS de la convocatoria (opcional)
            fecha_publicacion: Fecha de publicación en formato YYYY-MM-DD (opcional)
            bases_url: URL de las bases de la convocatoria (opcional)
            convocatoria_url: URL de la convocatoria (opcional)
            
        Returns:
            Diccionario con la información estructurada de la convocatoria
        """
        try:
            # Preparar mensaje con información adicional si está disponible
            additional_info = ""
            
            if codigo_bdns or fecha_publicacion or bases_url or convocatoria_url:
                info_adicional = "INFORMACIÓN ADICIONAL A INCORPORAR EN EL JSON:\n"
                
                if codigo_bdns:
                    info_adicional += f"- Código BDNS: {codigo_bdns}\n"
                    
                if fecha_publicacion:
                    info_adicional += f"- Fecha de publicación: {fecha_publicacion}\n"
                    # Añadir fecha de publicación como contexto para el cálculo de fechas
                    additional_info += f"\nLa fecha de publicación es {fecha_publicacion}. "
                    additional_info += f"Si se menciona un plazo relativo a la publicación (ej: 15 días), "
                    additional_info += f"calcula la fecha absoluta usando esta fecha como referencia.\n"
                    
                if bases_url:
                    info_adicional += f"- URL de las bases: {bases_url}\n"
                    
                if convocatoria_url:
                    info_adicional += f"- URL de la convocatoria: {convocatoria_url}\n"
                
                # Añadir a la convocatoria
                convocatoria_text = info_adicional + additional_info + "\n" + convocatoria_text
            
            # Limitar la longitud del texto para evitar problemas con la API
            # Gemini 2.5 admite contextos muy largos, pero seguimos siendo prudentes
            max_length = 250000  # 250k caracteres (mayor capacidad que antes)
            if len(convocatoria_text) > max_length:
                print(f"Texto demasiado largo ({len(convocatoria_text)} caracteres), truncando a {max_length}")
                convocatoria_text = convocatoria_text[:max_length]
            
            # Obtener respuesta del modelo
            prompt = self._extraction_prompt
            
            # Generar respuesta
            # Usamos la configuración ajustada para el nuevo modelo
            print(f"Generando contenido con el modelo {self.model_name}...")
            response = self.model.generate_content(
                [prompt, convocatoria_text],
                generation_config={
                    "temperature": 0.1,  # Temperatura baja para resultados más determinísticos
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 16384,  # Aumentado para evitar JSON incompleto
                }
            )
            
            # Extraer JSON de la respuesta
            json_text = response.text.strip()
            
            # Limpiar: quitar backticks y marcadores de JSON si existen
            json_text = re.sub(r'^```json\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)
            json_text = json_text.strip()
            
            # Paso adicional: eliminar texto que no sea parte del JSON pero pueda estar dentro
            # Identificamos casos como "velveteen" u otras palabras aleatorias que puedan aparecer
            try:
                # Intenta parsear el JSON antes de limpiarlo más
                json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"Detectado error en JSON, intentando limpiar: {e}")
                # Limpieza avanzada: busca patrones que rompen el JSON
                json_text = self._clean_malformed_json(json_text)
            
            # Parsear JSON limpio
            try:
                result = json.loads(json_text)
                
                # Asegurar estructura mínima
                self._validate_structure(result)
                
                # Completar con información adicional si no se añadió correctamente
                if codigo_bdns and (not result.get('codigo_bdns') or result['codigo_bdns'] == "null"):
                    result['codigo_bdns'] = codigo_bdns
                
                if bases_url and (not result.get('enlaces', {}).get('bases') or result['enlaces']['bases'] == "null"):
                    if 'enlaces' not in result:
                        result['enlaces'] = {}
                    result['enlaces']['bases'] = bases_url
                
                if convocatoria_url and (not result.get('enlaces', {}).get('convocatoria') or result['enlaces']['convocatoria'] == "null"):
                    if 'enlaces' not in result:
                        result['enlaces'] = {}
                    result['enlaces']['convocatoria'] = convocatoria_url
                
                # Verificar el estado de la convocatoria basado en las fechas
                self._verificar_estado_convocatoria(result, fecha_publicacion)
                
                return result
            
            except json.JSONDecodeError as e:
                print(f"Error al parsear JSON: {e}")
                print(f"Texto recibido: {json_text}")
                return {
                    "error": "No se pudo extraer la información de la convocatoria en formato válido",
                    "details": str(e)
                }
        
        except GoogleAPIError as e:
            print(f"Error en la API de Google: {e}")
            
            # Comprobar si es un error de cuota excedida
            if "429" in str(e) and "quota" in str(e).lower():
                return {
                    "error": "Se ha excedido la cuota de la API de Google Gemini. Por favor, inténtelo más tarde.",
                    "details": "Este error ocurre debido a un uso intensivo de la API o cuando se procesan documentos muy grandes."
                }
            # Otros errores de la API
            return {
                "error": "Error en la API de Google",
                "details": str(e)
            }
        except Exception as e:
            print(f"Error inesperado: {e}")
            traceback.print_exc()
            return {
                "error": "Error inesperado al extraer la información",
                "details": str(e)
            }
    
    def _verificar_estado_convocatoria(self, result: Dict[str, Any], fecha_publicacion: Optional[str] = None) -> None:
        """
        Verifica y corrige el estado de la convocatoria basado en las fechas
        
        Args:
            result: Diccionario con la información de la convocatoria
            fecha_publicacion: Fecha de publicación en formato YYYY-MM-DD (opcional)
        """
        try:
            # Si no tenemos objeto convocatoria, no podemos verificar
            if 'convocatoria' not in result or not isinstance(result['convocatoria'], dict):
                return
            
            # Obtener fecha actual
            fecha_actual = datetime.datetime.now().date()
            
            # Obtener fechas de la convocatoria
            fecha_apertura = result['convocatoria'].get('fecha_apertura')
            fecha_cierre = result['convocatoria'].get('fecha_cierre')
            
            # Si no hay fecha de apertura pero tenemos fecha de publicación, usarla como apertura
            if (not fecha_apertura or fecha_apertura == "null") and fecha_publicacion:
                try:
                    result['convocatoria']['fecha_apertura'] = fecha_publicacion
                    fecha_apertura = fecha_publicacion
                except:
                    pass
            
            # Determinar estado basado en fechas
            if fecha_cierre and fecha_cierre != "null":
                try:
                    fecha_cierre_dt = datetime.datetime.strptime(fecha_cierre, "%Y-%m-%d").date()
                    
                    # Si la fecha de cierre es posterior a la actual, la convocatoria está abierta
                    if fecha_cierre_dt >= fecha_actual:
                        result['convocatoria']['estado'] = "Abierta"
                    else:
                        result['convocatoria']['estado'] = "Cerrada"
                except:
                    # Si hay error al parsear la fecha, mantener el estado como está
                    pass
            elif fecha_apertura and fecha_apertura != "null":
                try:
                    fecha_apertura_dt = datetime.datetime.strptime(fecha_apertura, "%Y-%m-%d").date()
                    
                    # Si la fecha de apertura es posterior a la actual, la convocatoria está pendiente
                    if fecha_apertura_dt > fecha_actual:
                        result['convocatoria']['estado'] = "Pendiente"
                    # Si la fecha de apertura es anterior o igual a la actual y no hay fecha de cierre, está abierta
                    else:
                        result['convocatoria']['estado'] = "Abierta"
                except:
                    # Si hay error al parsear la fecha, mantener el estado como está
                    pass
        except Exception as e:
            # Si hay algún error, no modificar el estado
            print(f"Error al verificar estado de convocatoria: {e}")
    
    def _validate_structure(self, data: Dict[str, Any]) -> None:
        """
        Valida que el diccionario tiene la estructura mínima necesaria
        y completa campos faltantes
        """
        # Campos obligatorios de primer nivel
        required_fields = [
            'id', 'nombre', 'organismo', 'tipo_ayuda', 'ambito', 'beneficiarios',
            'sectores', 'tipo_proyecto', 'convocatoria', 'financiacion', 'requisitos',
            'resumen_breve', 'descripcion_detallada', 'tags', 'enlaces'
        ]
        
        for field in required_fields:
            if field not in data:
                data[field] = None if field not in ['beneficiarios', 'sectores', 'requisitos', 'tags'] else []
        
        # Campos anidados
        if 'convocatoria' not in data or not isinstance(data['convocatoria'], dict):
            data['convocatoria'] = {}
        
        conv_fields = ['estado', 'fecha_apertura', 'fecha_cierre']
        for field in conv_fields:
            if field not in data['convocatoria']:
                data['convocatoria'][field] = None
        
        if 'financiacion' not in data or not isinstance(data['financiacion'], dict):
            data['financiacion'] = {}
        
        fin_fields = ['intensidad', 'importe_maximo', 'presupuesto_minimo', 'presupuesto_maximo']
        for field in fin_fields:
            if field not in data['financiacion']:
                data['financiacion'][field] = None
        
        if 'enlaces' not in data or not isinstance(data['enlaces'], dict):
            data['enlaces'] = {}
        
        enl_fields = ['bases', 'convocatoria']
        for field in enl_fields:
            if field not in data['enlaces']:
                data['enlaces'][field] = None
        
        # Asegurar que los campos array son realmente arrays
        array_fields = ['beneficiarios', 'sectores', 'requisitos', 'tags']
        for field in array_fields:
            if field not in data or not isinstance(data[field], list):
                data[field] = []
    
    def verificar_duplicados(self, convocatoria: Dict[str, Any], programas_existentes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verifica si una convocatoria potencialmente duplica alguna existente
        VERSIÓN MEJORADA - Enfoque especial en código BDNS y nombre
        
        Args:
            convocatoria: La nueva convocatoria a verificar
            programas_existentes: Lista de programas existentes
            
        Returns:
            Lista de posibles duplicados con información detallada
        """
        posibles_duplicados = []
        
        # Obtener información de la nueva convocatoria
        nuevo_bdns = self._normalizar_bdns(convocatoria.get('codigo_bdns'))
        nuevo_nombre = self._normalizar_texto(convocatoria.get('nombre', ''))
        nuevo_organismo = self._normalizar_texto(convocatoria.get('organismo', ''))
        nuevo_id = convocatoria.get('id', '')
        
        print(f"Verificando duplicados para: {nuevo_nombre}")
        print(f"BDNS: {nuevo_bdns}, Organismo: {nuevo_organismo}")
        
        for i, programa in enumerate(programas_existentes):
            programa_bdns = self._normalizar_bdns(programa.get('codigo_bdns'))
            programa_nombre = self._normalizar_texto(programa.get('nombre', ''))
            programa_organismo = self._normalizar_texto(programa.get('organismo', ''))
            programa_id = programa.get('id', '')
            
            # PRIORIDAD 1: Código BDNS idéntico (máxima confianza)
            if nuevo_bdns and programa_bdns and nuevo_bdns == programa_bdns:
                posibles_duplicados.append({
                    "programa": programa,
                    "confianza": "Muy Alta",
                    "motivo": f"Código BDNS idéntico: {nuevo_bdns}",
                    "puntuacion": 100,
                    "tipo": "bdns_exacto"
                })
                print(f"  DUPLICADO BDNS EXACTO: {programa_nombre}")
                continue
            
            # PRIORIDAD 2: ID idéntico (muy alta confianza)
            if nuevo_id and programa_id and nuevo_id == programa_id:
                posibles_duplicados.append({
                    "programa": programa,
                    "confianza": "Muy Alta", 
                    "motivo": f"Identificador idéntico: {nuevo_id}",
                    "puntuacion": 95,
                    "tipo": "id_exacto"
                })
                print(f"  DUPLICADO ID EXACTO: {programa_nombre}")
                continue
            
            # PRIORIDAD 3: Nombre exacto + organismo exacto (muy alta confianza)
            if (nuevo_nombre and programa_nombre and nuevo_organismo and programa_organismo and
                nuevo_nombre == programa_nombre and nuevo_organismo == programa_organismo):
                posibles_duplicados.append({
                    "programa": programa,
                    "confianza": "Muy Alta",
                    "motivo": f"Nombre y organismo idénticos",
                    "puntuacion": 90,
                    "tipo": "nombre_organismo_exacto"
                })
                print(f"  DUPLICADO NOMBRE+ORGANISMO EXACTO: {programa_nombre}")
                continue
            
            # PRIORIDAD 4: Similitud alta en nombre + mismo organismo (alta confianza)
            similitud_nombre = self._similitud_texto_avanzada(nuevo_nombre, programa_nombre)
            if (similitud_nombre >= 0.85 and nuevo_organismo and programa_organismo and 
                nuevo_organismo == programa_organismo):
                posibles_duplicados.append({
                    "programa": programa,
                    "confianza": "Alta",
                    "motivo": f"Nombre muy similar ({similitud_nombre:.0%}) y mismo organismo",
                    "puntuacion": int(80 + (similitud_nombre - 0.85) * 67),  # 80-90 puntos
                    "tipo": "nombre_similar_organismo_exacto"
                })
                print(f"  DUPLICADO PROBABLE: {programa_nombre} (sim: {similitud_nombre:.0%})")
                continue
            
            # PRIORIDAD 5: Código BDNS similar (para casos de errores tipográficos)
            if nuevo_bdns and programa_bdns:
                similitud_bdns = self._similitud_bdns(nuevo_bdns, programa_bdns)
                if similitud_bdns >= 0.8:  # Muy similar pero no idéntico
                    posibles_duplicados.append({
                        "programa": programa,
                        "confianza": "Media-Alta",
                        "motivo": f"Código BDNS muy similar: {nuevo_bdns} vs {programa_bdns}",
                        "puntuacion": int(70 + (similitud_bdns - 0.8) * 50),  # 70-80 puntos
                        "tipo": "bdns_similar"
                    })
                    print(f"  BDNS SIMILAR: {programa_nombre} ({nuevo_bdns} vs {programa_bdns})")
                    continue
            
            # PRIORIDAD 6: Nombre muy similar pero organismos diferentes (sospechoso)
            if similitud_nombre >= 0.9:
                posibles_duplicados.append({
                    "programa": programa,
                    "confianza": "Media",
                    "motivo": f"Nombre casi idéntico ({similitud_nombre:.0%}) pero organismos diferentes",
                    "puntuacion": int(50 + (similitud_nombre - 0.9) * 100),  # 50-60 puntos
                    "tipo": "nombre_similar_organismo_diferente"
                })
                print(f"  POSIBLE DUPLICADO: {programa_nombre} (nombres similares, org. diferentes)")
                continue
            
            # PRIORIDAD 7: Detección de variaciones en el nombre (convocatorias anuales)
            if self._es_variacion_anual(nuevo_nombre, programa_nombre) and nuevo_organismo == programa_organismo:
                posibles_duplicados.append({
                    "programa": programa,
                    "confianza": "Media",
                    "motivo": "Posible variación anual de la misma convocatoria",
                    "puntuacion": 45,
                    "tipo": "variacion_anual"
                })
                print(f"  VARIACIÓN ANUAL: {programa_nombre}")
        
        # Ordenar por puntuación (más alta primero) y limitar resultados
        posibles_duplicados.sort(key=lambda x: x["puntuacion"], reverse=True)
        
        # Solo devolver los más relevantes (puntuación >= 40)
        posibles_duplicados = [d for d in posibles_duplicados if d["puntuacion"] >= 40]
        
        print(f"Encontrados {len(posibles_duplicados)} posibles duplicados")
        return posibles_duplicados[:10]  # Máximo 10 resultados
    
    def _normalizar_bdns(self, bdns) -> Optional[str]:
        """
        Normaliza un código BDNS para comparación
        
        Args:
            bdns: Código BDNS en cualquier formato
            
        Returns:
            Código BDNS normalizado o None
        """
        if not bdns or bdns in [None, 'null', 'nan', 'None', '']:
            return None
            
        # Convertir a string y limpiar
        bdns_str = str(bdns).strip()
        
        # Si está vacío después de strip
        if not bdns_str or bdns_str.lower() in ['null', 'nan', 'none']:
            return None
        
        # Eliminar caracteres no numéricos (excepto el punto decimal que quitaremos después)
        bdns_clean = re.sub(r'[^\d.]', '', bdns_str)
        
        # Si queda vacío o muy corto, no es válido
        if len(bdns_clean) < 5:
            return None
        
        # Convertir a float y luego a int para eliminar .0 y decimales
        try:
            # Si tiene punto decimal, convertir a float primero
            if '.' in bdns_clean:
                bdns_float = float(bdns_clean)
                bdns_int = int(bdns_float)
            else:
                bdns_int = int(bdns_clean)
            
            # Devolver como string sin ceros a la izquierda innecesarios
            return str(bdns_int)
        except (ValueError, OverflowError):
            # Si no se puede convertir a número, intentar limpiar más
            # Eliminar .0 al final si existe
            if bdns_clean.endswith('.0'):
                bdns_clean = bdns_clean[:-2]
            
            # Eliminar ceros a la izquierda
            bdns_clean = bdns_clean.lstrip('0')
            
            return bdns_clean if bdns_clean else None
    
    def _normalizar_texto(self, texto: str) -> str:
        """
        Normaliza texto para comparación
        
        Args:
            texto: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        if not texto:
            return ""
            
        import unicodedata
        
        # Convertir a minúsculas
        texto = texto.lower().strip()
        
        # Eliminar acentos y caracteres especiales
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
        
        # Reemplazar múltiples espacios por uno solo
        texto = re.sub(r'\s+', ' ', texto)
        
        # Eliminar puntuación común que no afecta el significado
        texto = re.sub(r'[.,;:()[\]{}"\'-]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    def _similitud_texto_avanzada(self, texto1: str, texto2: str) -> float:
        """
        Calcula similitud avanzada entre dos textos usando múltiples métricas
        
        Args:
            texto1: Primer texto
            texto2: Segundo texto
            
        Returns:
            Puntuación de similitud entre 0 y 1
        """
        if not texto1 or not texto2:
            return 0.0
            
        # Si son idénticos
        if texto1 == texto2:
            return 1.0
        
        # Similitud de Jaccard (conjuntos de palabras)
        palabras1 = set(texto1.split())
        palabras2 = set(texto2.split())
        
        interseccion = len(palabras1.intersection(palabras2))
        union = len(palabras1.union(palabras2))
        
        jaccard = interseccion / union if union > 0 else 0
        
        # Similitud de subcadenas (bigramas)
        bigramas1 = set([texto1[i:i+2] for i in range(len(texto1)-1)])
        bigramas2 = set([texto2[i:i+2] for i in range(len(texto2)-1)])
        
        interseccion_bg = len(bigramas1.intersection(bigramas2))
        union_bg = len(bigramas1.union(bigramas2))
        
        bigrama_sim = interseccion_bg / union_bg if union_bg > 0 else 0
        
        # Similitud de longitud (penalizar diferencias grandes)
        len_sim = 1 - abs(len(texto1) - len(texto2)) / max(len(texto1), len(texto2), 1)
        
        # Verificar si uno está contenido en el otro
        contenido = 0
        if texto1 in texto2 or texto2 in texto1:
            min_len = min(len(texto1), len(texto2))
            max_len = max(len(texto1), len(texto2))
            contenido = min_len / max_len
        
        # Combinar métricas con pesos
        similitud_final = (
            jaccard * 0.4 +           # Peso alto para palabras comunes
            bigrama_sim * 0.3 +       # Peso medio para estructura
            len_sim * 0.1 +           # Peso bajo para longitud
            contenido * 0.2           # Peso medio para contención
        )
        
        return min(similitud_final, 1.0)
    
    def _similitud_bdns(self, bdns1: str, bdns2: str) -> float:
        """
        Calcula similitud específica para códigos BDNS
        
        Args:
            bdns1: Primer código BDNS
            bdns2: Segundo código BDNS
            
        Returns:
            Similitud entre 0 y 1
        """
        if not bdns1 or not bdns2:
            return 0.0
            
        if bdns1 == bdns2:
            return 1.0
        
        # Para códigos numéricos, verificar similitudes específicas
        if len(bdns1) == len(bdns2):
            # Contar dígitos diferentes
            diferentes = sum(c1 != c2 for c1, c2 in zip(bdns1, bdns2))
            similitud = 1 - (diferentes / len(bdns1))
            
            # Si solo difieren en 1-2 dígitos, es muy sospechoso
            if diferentes <= 2:
                return similitud
        
        # Para longitudes diferentes, usar distancia de Levenshtein simplificada
        if abs(len(bdns1) - len(bdns2)) <= 2:
            # Implementación básica de distancia de edición
            return self._distancia_edicion_normalizada(bdns1, bdns2)
        
        return 0.0
    
    def _distancia_edicion_normalizada(self, s1: str, s2: str) -> float:
        """
        Calcula distancia de edición normalizada entre dos strings
        
        Args:
            s1: Primera cadena
            s2: Segunda cadena
            
        Returns:
            Similitud entre 0 y 1
        """
        if len(s1) < len(s2):
            return self._distancia_edicion_normalizada(s2, s1)
        
        if len(s2) == 0:
            return 0.0
        
        # Crear matriz de distancias
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Costo de inserción, eliminación, sustitución
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        distancia = previous_row[-1]
        max_len = max(len(s1), len(s2))
        
        return 1 - (distancia / max_len)
    
    def _es_variacion_anual(self, nombre1: str, nombre2: str) -> bool:
        """
        Detecta si dos nombres son variaciones anuales de la misma convocatoria
        
        Args:
            nombre1: Primer nombre
            nombre2: Segundo nombre
            
        Returns:
            True si parecen variaciones anuales
        """
        # Eliminar años de ambos nombres
        nombre1_sin_año = re.sub(r'\b(19|20)\d{2}\b', '', nombre1)
        nombre2_sin_año = re.sub(r'\b(19|20)\d{2}\b', '', nombre2)
        
        # Limpiar espacios extra
        nombre1_sin_año = re.sub(r'\s+', ' ', nombre1_sin_año).strip()
        nombre2_sin_año = re.sub(r'\s+', ' ', nombre2_sin_año).strip()
        
        # Si son muy similares sin los años, probablemente sean variaciones anuales
        similitud_sin_años = self._similitud_texto_avanzada(nombre1_sin_año, nombre2_sin_año)
        
        # También verificar si un nombre contiene al otro después de eliminar años
        if similitud_sin_años >= 0.85:
            return True
            
        # Verificar patrones específicos de convocatorias anuales
        patrones_anuales = [
            r'\b(convocatoria|programa|ayuda|subvencion)\b',
            r'\b(primera|segunda|tercera)\b',
            r'\b(i|ii|iii|iv|v)\b'
        ]
        
        for patron in patrones_anuales:
            if re.search(patron, nombre1_sin_año) and re.search(patron, nombre2_sin_año):
                if similitud_sin_años >= 0.7:
                    return True
                    
        return False

    def _similitud_texto(self, texto1: str, texto2: str) -> float:
        """
        Calcula la similitud entre dos textos (implementación básica)
        
        Args:
            texto1: Primer texto
            texto2: Segundo texto
            
        Returns:
            Valor entre 0 y 1 indicando la similitud
        """
        # Simplificar textos para comparación
        t1 = texto1.lower().strip()
        t2 = texto2.lower().strip()
        
        # Si son idénticos
        if t1 == t2:
            return 1.0
        
        # Si uno está contenido en el otro
        if t1 in t2 or t2 in t1:
            min_len = min(len(t1), len(t2))
            max_len = max(len(t1), len(t2))
            return min_len / max_len
        
        # Implementación básica de similitud de caracteres compartidos
        # En producción se recomendaría usar algo más sofisticado
        chars1 = set(t1)
        chars2 = set(t2)
        
        interseccion = len(chars1.intersection(chars2))
        union = len(chars1.union(chars2))
        
        return interseccion / union if union > 0 else 0