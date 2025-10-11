"""
Módulo para procesar archivos PDF y extraer texto
"""
import os
import PyPDF2
from typing import Optional


def extraer_texto_pdf(pdf_path: str) -> Optional[str]:
    """
    Extrae texto de un archivo PDF
    
    Args:
        pdf_path: Ruta al archivo PDF
        
    Returns:
        Texto extraído del PDF o None si hay error
    """
    try:
        if not os.path.exists(pdf_path):
            print(f"Error: El archivo {pdf_path} no existe")
            return None
        
        texto_completo = []
        
        # Abrir el PDF
        with open(pdf_path, 'rb') as file:
            # Crear lector PDF
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Obtener número de páginas
            num_paginas = len(pdf_reader.pages)
            print(f"📄 Procesando PDF con {num_paginas} páginas...")
            
            # Extraer texto de cada página
            for i, page in enumerate(pdf_reader.pages):
                try:
                    texto_pagina = page.extract_text()
                    if texto_pagina:
                        texto_completo.append(texto_pagina)
                        print(f"   ✓ Página {i+1}/{num_paginas} procesada")
                except Exception as e:
                    print(f"   ⚠ Error en página {i+1}: {e}")
                    continue
        
        # Unir todo el texto
        texto_final = '\n\n'.join(texto_completo)
        
        if not texto_final.strip():
            print("⚠ Advertencia: No se pudo extraer texto del PDF")
            return None
        
        print(f"✓ Texto extraído correctamente ({len(texto_final)} caracteres)")
        return texto_final
        
    except Exception as e:
        print(f"Error al extraer texto del PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def validar_pdf(pdf_path: str) -> bool:
    """
    Valida que un archivo sea un PDF válido
    
    Args:
        pdf_path: Ruta al archivo PDF
        
    Returns:
        True si es un PDF válido, False en caso contrario
    """
    try:
        if not os.path.exists(pdf_path):
            return False
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            # Intentar acceder al número de páginas
            _ = len(pdf_reader.pages)
            return True
            
    except Exception as e:
        print(f"Error al validar PDF: {e}")
        return False


def obtener_info_pdf(pdf_path: str) -> dict:
    """
    Obtiene información metadata de un PDF
    
    Args:
        pdf_path: Ruta al archivo PDF
        
    Returns:
        Diccionario con información del PDF
    """
    try:
        info = {
            'num_paginas': 0,
            'titulo': None,
            'autor': None,
            'creador': None,
            'fecha_creacion': None
        }
        
        if not os.path.exists(pdf_path):
            return info
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Número de páginas
            info['num_paginas'] = len(pdf_reader.pages)
            
            # Metadata
            if pdf_reader.metadata:
                info['titulo'] = pdf_reader.metadata.get('/Title')
                info['autor'] = pdf_reader.metadata.get('/Author')
                info['creador'] = pdf_reader.metadata.get('/Creator')
                info['fecha_creacion'] = pdf_reader.metadata.get('/CreationDate')
        
        return info
        
    except Exception as e:
        print(f"Error al obtener info del PDF: {e}")
        return info
