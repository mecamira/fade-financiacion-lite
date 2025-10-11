"""
Módulo para el análisis de compatibilidad de proyectos con convocatorias de ayudas I+D+i
usando la API de Gemini 2.5 Flash Preview - VERSIÓN MEJORADA CON OPCIÓN DE INFORMACIÓN INSUFICIENTE
"""
import os
import json
import re
import datetime
import traceback
import tempfile
import uuid
from typing import Dict, Any, Optional, List

# Importar configuración y utilidades de Google API
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

# Para procesar PDFs
import PyPDF2
import io

class CompatibilityAnalyzer:
    """Clase para analizar la compatibilidad de proyectos con convocatorias de ayudas I+D+i"""
    
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
        
        # Cargar el documento de restricciones
        self.restricciones_text = self._load_restricciones_doc()
        
        # Prompt para análisis de compatibilidad
        self._analysis_prompt = self._get_analysis_prompt()
    
    def _load_restricciones_doc(self) -> str:
        """
        Carga el documento de restricciones de actividad
        
        Returns:
            str: Texto extraído del documento de restricciones
        """
        try:
            # Buscar el archivo PDF en el directorio raíz
            pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'Reestricciones_ayudas.pdf')
            
            if not os.path.exists(pdf_path):
                print(f"No se encontró el archivo de restricciones en {pdf_path}")
                return ""
            
            # Leer el PDF
            pdf_reader = PyPDF2.PdfReader(pdf_path)
            
            # Extraer texto de todas las páginas
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text.strip() + "\n\n"
                except Exception as page_error:
                    print(f"Error al extraer texto de la página {page_num+1}: {page_error}")
                    continue
            
            return text
        except Exception as e:
            print(f"Error al cargar el documento de restricciones: {e}")
            return ""
    
    def _get_analysis_prompt(self) -> str:
        """
        Obtener el prompt para analizar la compatibilidad de un proyecto con una convocatoria
        
        Returns:
            str: Prompt para el análisis de compatibilidad
        """
        return f"""
        Eres un asesor especializado en ayudas y subvenciones de I+D+i en el Principado de Asturias. 
        Tu tarea es analizar si un proyecto empresarial es compatible con una convocatoria de ayudas específica.
        
        Para ello, debes usar:
        1. La descripción del proyecto y la información de la empresa (CNAE)
        2. La convocatoria de ayudas proporcionada
        3. El documento de restricciones de actividad para ayudas I+D+i del Principado de Asturias
        
        DOCUMENTO DE RESTRICCIONES:
        {self.restricciones_text}
        
        INSTRUCCIONES IMPORTANTES:
        1. Analiza detalladamente la convocatoria proporcionada
        2. Identifica requisitos, sectores excluidos, beneficiarios elegibles y restricciones de CNAE
        3. Verifica si la empresa y su proyecto cumplen con todos los requisitos y no están en sectores excluidos
        4. Considera las restricciones de la UE (FEDER, FTJ, Minimis, RGEC) según la convocatoria
        5. Evalúa si el proyecto se alinea con la S3/RIS3 de Asturias si es un requisito
        
        CRITERIOS DE COMPATIBILIDAD - MUY IMPORTANTE:
        - "compatible": true → Solo cuando TODOS los factores son claramente compatibles
        - "compatible": false → Solo cuando hay factores que CLARAMENTE EXCLUYEN la compatibilidad (NO por falta de información)
        - "compatible": "insufficient_data" → Cuando NO TIENES SUFICIENTE INFORMACIÓN para determinar la compatibilidad de factores clave
        
        DEBES DEVOLVER UN OBJETO JSON CON ESTE FORMATO EXACTO:
        {{
          "compatible": true/false/"insufficient_data",
          "resumen": "Resumen breve del análisis (2-3 frases explicando el resultado)",
          "motivo_incertidumbre": "Solo si compatible es 'insufficient_data': explica qué información falta",
          "convocatoria": {{
            "nombre": "Nombre de la convocatoria",
            "organismo": "Organismo gestor",
            "tipo_ayuda": "Tipo de ayuda",
            "ambito": "Ámbito geográfico"
          }},
          "factores": [
            {{
              "nombre": "Sector de actividad (CNAE)",
              "compatible": true/false/"insufficient_data",
              "detalle": "Explicación de la compatibilidad, incompatibilidad o falta de información"
            }},
            {{
              "nombre": "Beneficiario",
              "compatible": true/false/"insufficient_data",
              "detalle": "Explicación sobre si la empresa cumple, no cumple o falta información"
            }},
            {{
              "nombre": "Alineación con S3/RIS3",
              "compatible": true/false/"insufficient_data",
              "detalle": "Explicación de alineación, no alineación o información insuficiente"
            }},
            {{
              "nombre": "Tipo de proyecto",
              "compatible": true/false/"insufficient_data",
              "detalle": "Explicación de elegibilidad, no elegibilidad o información insuficiente"
            }},
            {{
              "nombre": "Restricciones específicas",
              "compatible": true/false/"insufficient_data",
              "detalle": "Explicación sobre restricciones aplicables o información faltante"
            }}
          ],
          "recomendaciones": [
            "Lista de 2-4 recomendaciones concretas. Si falta información, incluir qué datos adicionales se necesitan"
          ]
        }}
        
        REGLAS CRÍTICAS:
        - NO uses "false" por falta de información. Usa "insufficient_data" en su lugar.
        - Solo usa "false" cuando hay una exclusión o incompatibilidad clara y explícita.
        - Si un factor clave tiene "insufficient_data", la compatibilidad general debe ser "insufficient_data".
        - Si hay factores incompatibles (false) y otros con información insuficiente, prioriza "false".
        - Sé específico sobre qué información falta cuando uses "insufficient_data".
        - En las recomendaciones, sugiere qué datos o documentos adicionales se necesitan.
        
        Ahora, analiza cuidadosamente la convocatoria y el proyecto proporcionados:
        """
    
    def analyze_compatibility(self, 
                             empresa_nombre: str,
                             empresa_cnae: str,
                             proyecto_descripcion: str,
                             convocatoria_pdf) -> Dict[str, Any]:
        """
        Analiza la compatibilidad de un proyecto con una convocatoria de ayudas
        
        Args:
            empresa_nombre: Nombre de la empresa
            empresa_cnae: CNAE de la empresa
            proyecto_descripcion: Descripción del proyecto
            convocatoria_pdf: Archivo PDF de la convocatoria
        
        Returns:
            Diccionario con los resultados del análisis
        """
        try:
            # Extraer texto de la convocatoria PDF
            convocatoria_text = self._extract_text_from_pdf(convocatoria_pdf)
            
            if not convocatoria_text:
                return {
                    "error": "No se pudo extraer texto del PDF de la convocatoria"
                }
            
            # Crear un texto estructurado con toda la información
            input_text = f"""
            INFORMACIÓN DE LA EMPRESA:
            Nombre: {empresa_nombre}
            CNAE: {empresa_cnae}
            
            DESCRIPCIÓN DEL PROYECTO:
            {proyecto_descripcion}
            
            CONVOCATORIA DE AYUDAS:
            {convocatoria_text}
            """
            
            # Obtener respuesta del modelo
            prompt = self._analysis_prompt
            
            # Limitar el tamaño del texto para evitar problemas con tokens
            max_length = 200000  # 200k caracteres
            if len(input_text) > max_length:
                print(f"Texto demasiado largo ({len(input_text)} caracteres), truncando a {max_length}")
                input_text = input_text[:max_length]
            
            # Generar respuesta
            print(f"Generando análisis de compatibilidad con {self.model_name}...")
            response = self.model.generate_content(
                [prompt, input_text],
                generation_config={
                    "temperature": 0.2,  # Baja temperatura para análisis consistente
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
            
            # Verificar si la respuesta fue bloqueada por seguridad
            if not response.candidates or response.candidates[0].finish_reason != 1:  # 1 = STOP (completado)
                finish_reason = response.candidates[0].finish_reason if response.candidates else 'UNKNOWN'
                return {
                    "error": f"La API de Gemini bloqueó la respuesta (finish_reason: {finish_reason}). Esto puede deberse a filtros de seguridad.",
                    "details": "Intenta reformular la descripción del proyecto evitando términos que puedan ser interpretados como sensibles."
                }
            
            # Extraer JSON de la respuesta
            try:
                json_text = response.text.strip()
            except ValueError as e:
                return {
                    "error": "No se pudo obtener el texto de la respuesta",
                    "details": str(e)
                }
            
            # Limpiar: quitar backticks y marcadores de JSON si existen
            json_text = re.sub(r'^```json\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)
            json_text = json_text.strip()
            
            # Parsear JSON limpio
            try:
                result = json.loads(json_text)
                
                # Validar que el resultado tenga el formato esperado
                if not self._validate_result_format(result):
                    return {
                        "error": "El análisis no devolvió un formato válido",
                        "details": "Formato de respuesta incorrecto"
                    }
                
                # Generar un ID único para el resultado
                result_id = str(uuid.uuid4())
                result['id'] = result_id
                result['timestamp'] = datetime.datetime.now().isoformat()
                
                # Guardar resultado en un archivo temporal para referencia futura
                self._save_result(result_id, result)
                
                return {
                    "success": True,
                    "result_id": result_id
                }
            
            except json.JSONDecodeError as e:
                print(f"Error al parsear JSON: {e}")
                print(f"Texto recibido: {json_text}")
                return {
                    "error": "No se pudo procesar el análisis en formato válido",
                    "details": str(e)
                }
            
        except Exception as e:
            print(f"Error inesperado en el análisis de compatibilidad: {e}")
            traceback.print_exc()
            return {
                "error": "Error inesperado al analizar la compatibilidad",
                "details": str(e)
            }
    
    def _validate_result_format(self, result: Dict[str, Any]) -> bool:
        """
        Valida que el resultado tenga el formato esperado
        
        Args:
            result: Resultado del análisis
            
        Returns:
            True si el formato es válido, False en caso contrario
        """
        try:
            # Verificar campos obligatorios
            required_fields = ['compatible', 'resumen', 'convocatoria', 'factores', 'recomendaciones']
            
            for field in required_fields:
                if field not in result:
                    print(f"Campo obligatorio faltante: {field}")
                    return False
            
            # Verificar que compatible sea uno de los valores válidos
            valid_compatible_values = [True, False, "insufficient_data"]
            if result['compatible'] not in valid_compatible_values:
                print(f"Valor de 'compatible' no válido: {result['compatible']}")
                return False
            
            # Verificar que factores sea una lista
            if not isinstance(result['factores'], list):
                print("'factores' debe ser una lista")
                return False
            
            # Verificar formato de cada factor
            for factor in result['factores']:
                if not isinstance(factor, dict):
                    print("Cada factor debe ser un diccionario")
                    return False
                    
                factor_required_fields = ['nombre', 'compatible', 'detalle']
                for field in factor_required_fields:
                    if field not in factor:
                        print(f"Campo faltante en factor: {field}")
                        return False
                
                if factor['compatible'] not in valid_compatible_values:
                    print(f"Valor de 'compatible' no válido en factor: {factor['compatible']}")
                    return False
            
            # Verificar que recomendaciones sea una lista
            if not isinstance(result['recomendaciones'], list):
                print("'recomendaciones' debe ser una lista")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error al validar formato del resultado: {e}")
            return False
    
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
            max_length = 200000  # 200k caracteres
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
    
    def _save_result(self, result_id: str, result: Dict[str, Any]) -> None:
        """
        Guarda el resultado del análisis en un archivo temporal
        
        Args:
            result_id: ID único del resultado
            result: Datos del resultado del análisis
        """
        try:
            # Crear directorio temporal si no existe
            tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tmp')
            os.makedirs(tmp_dir, exist_ok=True)
            
            # Guardar resultado en archivo JSON
            file_path = os.path.join(tmp_dir, f"compatibility_{result_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"Resultado guardado en {file_path}")
        except Exception as e:
            print(f"Error al guardar resultado: {e}")
    
    def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un resultado previamente guardado
        
        Args:
            result_id: ID único del resultado
            
        Returns:
            Datos del resultado o None si no se encuentra
        """
        try:
            # Buscar archivo de resultado
            tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tmp')
            file_path = os.path.join(tmp_dir, f"compatibility_{result_id}.json")
            
            if not os.path.exists(file_path):
                print(f"No se encontró el archivo de resultado {file_path}")
                return None
            
            # Cargar resultado desde archivo JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            return result
        except Exception as e:
            print(f"Error al obtener resultado: {e}")
            return None
    
    def get_compatibility_summary(self, result_id: str) -> Optional[str]:
        """
        Obtiene un resumen legible del resultado de compatibilidad
        
        Args:
            result_id: ID único del resultado
            
        Returns:
            Resumen legible del análisis
        """
        result = self.get_result(result_id)
        if not result:
            return None
        
        compatible = result.get('compatible')
        
        if compatible is True:
            status = "✅ COMPATIBLE"
        elif compatible is False:
            status = "❌ NO COMPATIBLE"
        elif compatible == "insufficient_data":
            status = "❓ INFORMACIÓN INSUFICIENTE"
        else:
            status = "❔ ESTADO DESCONOCIDO"
        
        summary = f"{status}\n\n"
        summary += f"Resumen: {result.get('resumen', 'Sin resumen disponible')}\n\n"
        
        if compatible == "insufficient_data" and 'motivo_incertidumbre' in result:
            summary += f"Motivo de incertidumbre: {result['motivo_incertidumbre']}\n\n"
        
        # Agregar información de la convocatoria
        convocatoria = result.get('convocatoria', {})
        if convocatoria:
            summary += f"Convocatoria: {convocatoria.get('nombre', 'Sin nombre')}\n"
            summary += f"Organismo: {convocatoria.get('organismo', 'Sin organismo')}\n\n"
        
        # Agregar factores críticos
        factores = result.get('factores', [])
        if factores:
            summary += "Factores analizados:\n"
            for factor in factores:
                factor_status = factor.get('compatible')
                if factor_status is True:
                    icon = "✅"
                elif factor_status is False:
                    icon = "❌"
                elif factor_status == "insufficient_data":
                    icon = "❓"
                else:
                    icon = "❔"
                
                summary += f"  {icon} {factor.get('nombre', 'Factor sin nombre')}\n"
        
        return summary
