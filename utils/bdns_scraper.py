"""
Módulo para hacer scraping de información de convocatorias desde la BDNS
usando Selenium para manejar contenido dinámico de Angular
"""
import re
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("WARNING: Selenium no está instalado. El scraping de BDNS no estará disponible.")


class BDNSScraper:
    """Clase para extraer información de convocatorias desde la BDNS"""
    
    def __init__(self, headless: bool = True):
        """
        Inicializa el scraper
        
        Args:
            headless: Si True, ejecuta Chrome sin interfaz gráfica
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium no está instalado. "
                "Instala con: pip install selenium webdriver-manager"
            )
        
        self.headless = headless
        self.driver = None
    
    def _init_driver(self):
        """Inicializa el driver de Chrome (local o remoto según configuración)"""
        if self.driver is not None:
            return
        
        import os
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Opciones para mejor rendimiento
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        
        # Verificar si hay un Selenium remoto configurado (Docker)
        selenium_url = os.environ.get('SELENIUM_REMOTE_URL')
        
        if selenium_url:
            # Modo Docker (producción) - usar Selenium Grid remoto
            print(f"Usando Selenium remoto en: {selenium_url}")
            try:
                self.driver = webdriver.Remote(
                    command_executor=selenium_url,
                    options=chrome_options
                )
                print("✓ Conectado a Selenium Grid remoto")
            except Exception as e:
                print(f"Error al conectar con Selenium remoto: {e}")
                raise Exception(
                    f"No se pudo conectar con Selenium Grid en {selenium_url}. "
                    "Verifica que el contenedor de Selenium esté corriendo."
                )
        else:
            # Modo local (desarrollo) - usar ChromeDriver local
            print("Usando ChromeDriver local")
            try:
                # Intentar con webdriver-manager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✓ ChromeDriver inicializado con webdriver-manager")
            except Exception as e:
                print(f"Error con webdriver-manager: {e}")
                print("Intentando con ChromeDriver del sistema...")
                
                # Intentar sin especificar service (buscar en PATH)
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    print("✓ ChromeDriver inicializado desde PATH")
                except Exception as e2:
                    print(f"Error al inicializar Chrome: {e2}")
                    raise Exception(
                        "No se pudo inicializar Chrome. Asegúrate de tener Chrome instalado "
                        "o descarga ChromeDriver manualmente desde: "
                        "https://googlechromelabs.github.io/chrome-for-testing/"
                    )
        
        self.driver.set_page_load_timeout(30)
    
    def close(self):
        """Cierra el driver de Selenium"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        self._init_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    @staticmethod
    def extraer_codigo_bdns(url_o_codigo: str) -> Optional[str]:
        """
        Extrae el código BDNS de una URL o devuelve el código si ya es numérico
        
        Args:
            url_o_codigo: URL completa de BDNS o código numérico
            
        Returns:
            Código BDNS como string, o None si no se encuentra
            
        Examples:
            >>> BDNSScraper.extraer_codigo_bdns("https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias/860141")
            "860141"
            >>> BDNSScraper.extraer_codigo_bdns("860141")
            "860141"
        """
        # Si ya es un código numérico, devolverlo
        if url_o_codigo.strip().isdigit():
            return url_o_codigo.strip()
        
        # Intentar extraer de la URL
        # Patrón: /convocatorias/XXXXXX o /convocatoria/XXXXXX
        patron = r'/convocatorias?/(\d+)'
        match = re.search(patron, url_o_codigo)
        
        if match:
            return match.group(1)
        
        return None
    
    def obtener_info_convocatoria(self, codigo_bdns: str) -> Dict[str, Any]:
        """
        Obtiene información de una convocatoria desde la BDNS
        
        Args:
            codigo_bdns: Código BDNS de la convocatoria
            
        Returns:
            Diccionario con la información extraída:
            {
                'success': bool,
                'codigo_bdns': str,
                'url_bases': str,
                'documentos': [
                    {
                        'titulo': str,
                        'fecha_registro': str,
                        'fecha_publicacion': str,
                        'url': str
                    },
                    ...
                ],
                'error': str (solo si success=False)
            }
        """
        try:
            self._init_driver()
            
            # Construir URL
            url = f"https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias/{codigo_bdns}"
            
            print(f"Accediendo a: {url}")
            self.driver.get(url)
            
            # Esperar a que cargue el contenido (Angular tarda en cargar)
            # Esperamos a que aparezca algún elemento característico
            wait = WebDriverWait(self.driver, 15)
            
            # Esperar a que desaparezca el spinner de carga (si existe)
            time.sleep(3)  # Dar tiempo inicial para que Angular arranque
            
            # Intentar esperar a que aparezca la sección de documentos
            try:
                wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Documentos') or contains(text(), 'documentos')]"))
                )
            except:
                # Si no encontramos la sección de documentos, dar más tiempo
                time.sleep(5)
            
            # Extraer documentos (pasar codigo_bdns)
            documentos = self._extraer_documentos(codigo_bdns)
            
            resultado = {
                'success': True,
                'codigo_bdns': codigo_bdns,
                'url_bases': url,
                'documentos': documentos
            }
            
            return resultado
            
        except Exception as e:
            print(f"Error al obtener información de BDNS: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': f"Error al acceder a la BDNS: {str(e)}",
                'codigo_bdns': codigo_bdns
            }
    
    def _extraer_documentos(self, codigo_bdns: str) -> List[Dict[str, Any]]:
        """
        Extrae la lista de documentos de la convocatoria
        
        Returns:
            Lista de documentos con su información
        """
        documentos = []
        
        try:
            print("\n🔍 Buscando documentos en la sección 'Documentos de la convocatoria'...")
            
            # ESTRATEGIA 1: Buscar en la tabla específica "Documentos de la convocatoria"
            try:
                # Buscar todas las tablas
                tablas = self.driver.find_elements(By.TAG_NAME, "table")
                print(f"   Tablas encontradas: {len(tablas)}")
                
                for tabla in tablas:
                    tabla_text = tabla.text
                    
                    # Verificar si es la tabla de documentos de convocatoria
                    if "Documentos de la convocatoria" in tabla_text or "Fecha de registro" in tabla_text:
                        print("   ✓ Tabla de documentos encontrada!")
                        
                        # Buscar todas las filas de la tabla
                        filas = tabla.find_elements(By.TAG_NAME, "tr")
                        print(f"   Filas en la tabla: {len(filas)}")
                        
                        for idx, fila in enumerate(filas):
                            try:
                                # Buscar enlaces en esta fila
                                enlaces_fila = fila.find_elements(By.TAG_NAME, "a")
                                
                                # También buscar botones o elementos clickeables (Angular)
                                botones_fila = fila.find_elements(By.XPATH, ".//*[@role='button' or contains(@class, 'mat-') or @ng-click]")
                                
                                if enlaces_fila or botones_fila:
                                    # Obtener el texto completo de la fila para extraer fechas
                                    fila_text = fila.text
                                    print(f"\n   📄 Fila #{idx}: {fila_text[:80]}...")
                                    
                                    # Extraer fechas de la fila
                                    fechas = self._extraer_fechas_multiples(fila_text)
                                    
                                    # ESTRATEGIA: Hacer clic en el botón Permalink y capturar la URL del modal
                                    try:
                                        # Buscar el botón con title="Permalink"
                                        boton_permalink = fila.find_element(By.XPATH, ".//a[@title='Permalink']")
                                        
                                        if boton_permalink:
                                            print("      🔗 Encontrado botón Permalink, haciendo clic...")
                                            
                                            # Hacer clic en el botón usando JavaScript
                                            self.driver.execute_script("arguments[0].click();", boton_permalink)
                                            
                                            # Esperar a que aparezca el modal/dialog
                                            time.sleep(1)
                                            
                                            # Buscar el enlace con la URL en el modal
                                            try:
                                                # El modal tiene un <a> con la URL completa
                                                url_link = self.driver.find_element(By.XPATH, "//mat-dialog-container//a[@href and contains(@href, '/document/')]")
                                                doc_url = url_link.get_attribute('href')
                                                
                                                if doc_url and '/document/' in doc_url:
                                                    print(f"      ✓ URL capturada del modal: {doc_url}")
                                                    
                                                    # Descargar el PDF automáticamente
                                                    try:
                                                        print(f"      📄 Descargando PDF...")
                                                        import requests
                                                        
                                                        # Descargar el documento
                                                        pdf_response = requests.get(doc_url, timeout=30)
                                                        
                                                        if pdf_response.status_code == 200:
                                                            # Guardar en temporal
                                                            import tempfile
                                                            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                                                            temp_pdf.write(pdf_response.content)
                                                            temp_pdf_path = temp_pdf.name
                                                            temp_pdf.close()
                                                            
                                                            print(f"      ✓ PDF descargado: {temp_pdf_path}")
                                                        else:
                                                            print(f"      ⚠ Error al descargar PDF: {pdf_response.status_code}")
                                                            temp_pdf_path = None
                                                    except Exception as e:
                                                        print(f"      ⚠ Error al descargar PDF: {e}")
                                                        temp_pdf_path = None
                                                    
                                                    # Cerrar el modal (buscar botón "Cerrar")
                                                    try:
                                                        boton_cerrar = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cerrar') or contains(text(), 'Close')]")
                                                        boton_cerrar.click()
                                                        time.sleep(0.3)
                                                    except:
                                                        # Si no encuentra el botón, presionar ESC
                                                        from selenium.webdriver.common.keys import Keys
                                                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                                                        time.sleep(0.3)
                                                    
                                                    # Extraer nombre del archivo
                                                    nombre_archivo = "Documento de convocatoria"
                                                    if '.pdf' in fila_text.lower():
                                                        # Extraer nombre del PDF (buscar el patrón más específico)
                                                        match_pdf = re.search(r'get_app\s+([\w\s_-]+\.pdf)', fila_text, re.IGNORECASE)
                                                        if match_pdf:
                                                            nombre_archivo = match_pdf.group(1).strip()
                                                        else:
                                                            # Intento alternativo: buscar cualquier .pdf
                                                            match_pdf = re.search(r'([\w_-]+\.pdf)', fila_text, re.IGNORECASE)
                                                            if match_pdf:
                                                                nombre_archivo = match_pdf.group(1).strip()
                                                    
                                                    print(f"      ✓ Documento procesado:")
                                                    print(f"         Nombre: {nombre_archivo}")
                                                    print(f"         URL: {doc_url}")
                                                    print(f"         Fechas: {fechas}")
                                                    
                                                    doc_info = {
                                                        'titulo': nombre_archivo,
                                                        'url': doc_url,
                                                        'fecha_registro': fechas.get('fecha_registro'),
                                                        'fecha_publicacion': fechas.get('fecha_publicacion'),
                                                        'tipo': 'convocatoria',
                                                        'pdf_path': temp_pdf_path  # Ruta del PDF descargado
                                                    }
                                                    
                                                    documentos.append(doc_info)
                                                    continue  # Siguiente fila
                                                    
                                            except Exception as e:
                                                print(f"      ⚠ No se pudo capturar URL del modal: {e}")
                                                # Intentar cerrar cualquier modal abierto
                                                try:
                                                    from selenium.webdriver.common.keys import Keys
                                                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                                                except:
                                                    pass
                                                
                                    except Exception as e:
                                        print(f"      ⚠ Error al procesar botón Permalink: {e}")
                                    
                                    # Si no encontramos ID, intentar con enlaces tradicionales
                                    for enlace in enlaces_fila:
                                        href = enlace.get_attribute('href')
                                        texto = enlace.text.strip()
                                        
                                        print(f"      → Enlace encontrado:")
                                        print(f"         Texto: {texto}")
                                        print(f"         URL: {href}")
                                        
                                        # Aceptar enlaces que contengan 'document' O que apunten a PDFs
                                        if href and ('document' in href.lower() or href.endswith('.pdf') or '/convocatoria/' in href.lower()):
                                            print(f"      ✓ Documento aceptado!")
                                            print(f"      → Fechas: {fechas}")
                                            
                                            doc_info = {
                                                'titulo': texto if texto else 'Documento de convocatoria',
                                                'url': href,
                                                'fecha_registro': fechas.get('fecha_registro'),
                                                'fecha_publicacion': fechas.get('fecha_publicacion'),
                                                'tipo': 'convocatoria'
                                            }
                                            
                                            documentos.append(doc_info)
                                        else:
                                            print(f"      ✗ Enlace rechazado (href vacío o no cumple criterios)")
                                            
                            except Exception as e:
                                continue
                        
                        # Si encontramos documentos en la tabla, salir
                        if documentos:
                            break
                            
            except Exception as e:
                print(f"   Error al buscar en tablas: {e}")
            
            # ESTRATEGIA 2: Si no encontramos nada en tablas, buscar enlaces genéricos
            if not documentos:
                print("\n   ⚠ No se encontraron documentos en tablas, buscando enlaces genéricos...")
                
                enlaces_docs = self.driver.find_elements(By.TAG_NAME, "a")
                print(f"   Total de enlaces: {len(enlaces_docs)}")
                
                for idx, enlace in enumerate(enlaces_docs):
                    try:
                        href = enlace.get_attribute('href')
                        texto = enlace.text.strip()
                        
                        # Filtrar solo enlaces que parezcan documentos
                        if href and 'document' in href.lower():
                            print(f"\n   📄 Documento genérico #{idx + 1}:")
                            print(f"      Título: {texto}")
                            print(f"      URL: {href}")
                            
                            # Intentar encontrar fechas en el contexto
                            try:
                                parent = enlace.find_element(By.XPATH, "..")
                                parent_text = parent.text
                            except:
                                parent_text = ""
                            
                            fechas = self._extraer_fechas_de_texto(parent_text)
                            
                            doc_info = {
                                'titulo': texto if texto else 'Documento',
                                'url': href,
                                'fecha_registro': fechas.get('fecha_registro'),
                                'fecha_publicacion': fechas.get('fecha_publicacion'),
                                'tipo': 'generico'
                            }
                            
                            print(f"      Fechas: {fechas}")
                            documentos.append(doc_info)
                            
                    except Exception as e:
                        continue
            
            # ESTRATEGIA 3: Buscar las bases reguladoras por separado
            print("\n🔍 Buscando bases reguladoras...")
            try:
                enlaces_bases = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'bopa') or contains(@href, 'bases')]")
                
                for enlace in enlaces_bases:
                    try:
                        href = enlace.get_attribute('href')
                        texto = enlace.text.strip()
                        
                        if href and 'pdf' in href.lower():
                            # Buscar contexto para fechas
                            try:
                                parent = enlace.find_element(By.XPATH, "..")
                                parent_text = parent.text
                            except:
                                parent_text = ""
                            
                            fechas = self._extraer_fechas_de_texto(parent_text)
                            
                            doc_info = {
                                'titulo': 'Bases reguladoras' if not texto else texto,
                                'url': href,
                                'fecha_registro': fechas.get('fecha_registro'),
                                'fecha_publicacion': fechas.get('fecha_publicacion'),
                                'tipo': 'bases_reguladoras'
                            }
                            
                            # Solo añadir si no está ya en la lista
                            if not any(d['url'] == href for d in documentos):
                                documentos.append(doc_info)
                                print(f"   → Bases reguladoras: {href}")
                                
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"   Error al buscar bases: {e}")
            
            print(f"\n✅ Total documentos extraídos: {len(documentos)}")
            
            # Ordenar: primero convocatorias, luego genéricos, luego bases
            documentos.sort(key=lambda x: (
                0 if x.get('tipo') == 'convocatoria' else
                1 if x.get('tipo') == 'generico' else
                2
            ))
            
        except Exception as e:
            print(f"Error al extraer documentos: {e}")
            import traceback
            traceback.print_exc()
        
        return documentos
    
    def _extraer_fechas_de_texto(self, texto: str) -> Dict[str, Optional[str]]:
        """
        Extrae fechas de un texto en formato español
        
        Args:
            texto: Texto que puede contener fechas
            
        Returns:
            Diccionario con fecha_registro y fecha_publicacion
        """
        resultado = {
            'fecha_registro': None,
            'fecha_publicacion': None
        }
        
        # Patrones de fecha: dd/mm/yyyy o dd-mm-yyyy
        patron_fecha = r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b'
        
        # Buscar todas las fechas
        fechas_encontradas = re.findall(patron_fecha, texto)
        
        if fechas_encontradas:
            # Convertir primera fecha encontrada a formato YYYY-MM-DD
            dia, mes, año = fechas_encontradas[0]
            try:
                fecha_obj = datetime(int(año), int(mes), int(dia))
                fecha_formateada = fecha_obj.strftime('%Y-%m-%d')
                
                # Si el texto menciona "registro", es fecha de registro
                if 'registro' in texto.lower():
                    resultado['fecha_registro'] = fecha_formateada
                # Si menciona "publicación", es fecha de publicación
                elif 'publicación' in texto.lower() or 'publicacion' in texto.lower():
                    resultado['fecha_publicacion'] = fecha_formateada
                else:
                    # Por defecto, asumir que es fecha de publicación
                    resultado['fecha_publicacion'] = fecha_formateada
                
            except ValueError:
                pass
        
        return resultado
    
    def _extraer_fechas_multiples(self, texto: str) -> Dict[str, Optional[str]]:
        """
        Extrae múltiples fechas de un texto (fecha de registro Y fecha de publicación)
        
        Args:
            texto: Texto que puede contener múltiples fechas
            
        Returns:
            Diccionario con fecha_registro y fecha_publicacion
        """
        resultado = {
            'fecha_registro': None,
            'fecha_publicacion': None
        }
        
        # Patrones de fecha: dd/mm/yyyy o dd-mm-yyyy
        patron_fecha = r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b'
        
        # Buscar todas las fechas
        fechas_encontradas = re.findall(patron_fecha, texto)
        
        if len(fechas_encontradas) >= 2:
            # Si hay 2 o más fechas, asumimos que la primera es registro y la segunda publicación
            try:
                # Primera fecha = registro
                dia, mes, año = fechas_encontradas[0]
                fecha_obj = datetime(int(año), int(mes), int(dia))
                resultado['fecha_registro'] = fecha_obj.strftime('%Y-%m-%d')
                
                # Segunda fecha = publicación
                dia, mes, año = fechas_encontradas[1]
                fecha_obj = datetime(int(año), int(mes), int(dia))
                resultado['fecha_publicacion'] = fecha_obj.strftime('%Y-%m-%d')
                
            except (ValueError, IndexError):
                pass
                
        elif len(fechas_encontradas) == 1:
            # Si solo hay una fecha, usar el método simple
            return self._extraer_fechas_de_texto(texto)
        
        return resultado


# Función de utilidad para usar sin context manager
def obtener_info_bdns(url_o_codigo: str, headless: bool = True) -> Dict[str, Any]:
    """
    Función de utilidad para obtener información de BDNS
    
    Args:
        url_o_codigo: URL de BDNS o código numérico
        headless: Si True, ejecuta sin interfaz gráfica
        
    Returns:
        Diccionario con la información de la convocatoria
    """
    # Extraer código BDNS
    codigo = BDNSScraper.extraer_codigo_bdns(url_o_codigo)
    
    if not codigo:
        return {
            'success': False,
            'error': 'No se pudo extraer el código BDNS de la URL proporcionada'
        }
    
    # Usar context manager para asegurar que se cierra el driver
    with BDNSScraper(headless=headless) as scraper:
        return scraper.obtener_info_convocatoria(codigo)
