# Campos de Convocatorias - Origen y Reglas de Generación

Este documento lista TODOS los campos que se extraen/generan para cada convocatoria, detallando su origen, reglas de generación y procesamiento.

---

## 📊 RESUMEN DE CAMPOS

**Total de campos: 28**

- **Extraídos por Gemini AI**: 19 campos
- **Desde BDNS (scraper)**: 3 campos
- **Auto-generados (normalización)**: 5 campos
- **Calculados (procesamiento)**: 1 campo

---

## 1️⃣ CAMPOS EXTRAÍDOS POR GEMINI AI (19 campos)

Estos campos se extraen del PDF de la convocatoria usando Google Gemini 2.5 Flash.

### **1.1. Identificación básica**

#### `nombre` (string)
- **Fuente**: Texto del PDF
- **Reglas**:
  - Título conciso, máximo 100 caracteres
  - NO incluir fechas, plazos ni años
  - NO incluir tipo de ayuda (va en `tipo_ayuda`)
  - Eliminar prefijos como "Convocatoria de", "Programa de"
  - Si es muy largo, resumir manteniendo la esencia
- **Ejemplos buenos**:
  - "Subvenciones contratación indefinida personas con discapacidad"
  - "Ayudas Severo Ochoa para estancias breves de investigación"
- **Ejemplos malos** (demasiado largos):
  - "Convocatoria de subvenciones para empresas por la contratación indefinida de personas desempleadas con discapacidad (Del 1 de junio de 2025 al 31 de mayo de 2027)"

#### `organismo` (string)
- **Fuente**: Texto del PDF
- **Reglas**: Nombre del organismo gestor exacto
- **Ejemplos**: "CDTI", "Principado de Asturias", "Red.es"

#### `codigo_bdns` (string/number)
- **Fuente**:
  1. BDNS scraper (si viene de URL BDNS)
  2. Parámetro manual en formulario
  3. Texto del PDF (si aparece mencionado)
- **Reglas**:
  - Numérico si es posible
  - null si no está disponible
- **Procesamiento posterior**: Se convierte a `int` si es posible

---

### **1.2. Clasificación de la ayuda**

#### `tipo_ayuda` (string)
- **Fuente**: Texto del PDF
- **Reglas**: Tipo de ayuda literal
- **Ejemplos**:
  - "Subvención"
  - "Préstamo participativo"
  - "Capital Riesgo"
  - "Ayuda en especie"

#### `ambito` (string)
- **Fuente**: Texto del PDF
- **Reglas**: Ámbito geográfico
- **Ejemplos**: "Nacional", "Comunidad Autónoma", "Regional", "Local"

#### `tipo_proyecto` (string)
- **Fuente**: Texto del PDF
- **Reglas**: Descripción del tipo de proyecto financiable
- **Ejemplos**:
  - "Investigación, desarrollo, innovación"
  - "Digitalización de PYMES"
  - "Contratación de personal"

---

### **1.3. Fechas y estado**

#### `convocatoria.estado` (string: "Abierta" | "Cerrada" | "Pendiente")
- **Fuente**: Calculado por Gemini AI
- **Reglas**:
  - **"Abierta"**: fecha_cierre > fecha_actual
  - **"Cerrada"**: fecha_cierre < fecha_actual
  - **"Pendiente"**: fecha_apertura > fecha_actual
  - Si no hay fechas claras, deduce por contexto

#### `convocatoria.fecha_apertura` (string: "YYYY-MM-DD")
- **Fuente**: Texto del PDF
- **Reglas**:
  - Formato ISO: YYYY-MM-DD
  - Si no se indica, asume fecha_publicacion (si está disponible)
  - Si menciona "20 días hábiles desde publicación", calcula: 20 días hábiles ≈ 28 días naturales
  - null si no hay información

#### `convocatoria.fecha_cierre` (string: "YYYY-MM-DD")
- **Fuente**: Texto del PDF
- **Reglas**:
  - Formato ISO: YYYY-MM-DD
  - Calcula fechas relativas si es necesario (ej: "30 días desde publicación")
  - null si no hay información

---

### **1.4. Financiación**

#### `financiacion.intensidad` (string)
- **Fuente**: Texto del PDF
- **Reglas**: Captura porcentajes y descripciones específicas
- **Ejemplos**: "70%", "Hasta 100%", "50-80% según tipo de empresa"

#### `financiacion.importe_maximo` (string/number)
- **Fuente**: Texto del PDF
- **Reglas**:
  - Extraer SOLO números, sin símbolos monetarios
  - "500.000€" → "500000"
  - Redondea a enteros si es necesario
- **Procesamiento posterior**: Se convierte a `float`

#### `financiacion.presupuesto_minimo` (string/number)
- **Fuente**: Texto del PDF
- **Reglas**: Igual que `importe_maximo`
- **Procesamiento posterior**: Se convierte a `float`

#### `financiacion.presupuesto_maximo` (string/number)
- **Fuente**: Texto del PDF
- **Reglas**: Igual que `importe_maximo`
- **Procesamiento posterior**: Se convierte a `float`

---

### **1.5. Listas (beneficiarios, sectores, requisitos)**

#### `beneficiarios` (array de strings)
- **Fuente**: Texto del PDF
- **Reglas**:
  - Elementos individuales, NO textos largos con separadores
  - Cada elemento: frase corta y concisa
- **Ejemplos**:
  ```json
  ["PYMES", "Startups", "Autónomos"]
  ```

#### `sectores` (array de strings)
- **Fuente**: Texto del PDF
- **Reglas**: Igual que `beneficiarios`
- **Ejemplos**:
  ```json
  ["Tecnología", "I+D+i", "Industria"]
  ```

#### `requisitos` (array de strings)
- **Fuente**: Texto del PDF
- **Reglas**: Lista de requisitos principales, uno por elemento
- **Ejemplos**:
  ```json
  [
    "Tener menos de 250 empleados",
    "Facturación inferior a 50M€",
    "Proyecto innovador"
  ]
  ```

#### `tags` (array de strings)
- **Fuente**: Texto del PDF
- **Reglas**: Palabras clave relevantes
- **Ejemplos**:
  ```json
  ["innovación", "digitalización", "I+D", "sostenibilidad"]
  ```

---

### **1.6. Descripciones**

#### `resumen_breve` (string)
- **Fuente**: Texto del PDF
- **Reglas**:
  - Máximo 200 caracteres
  - Una frase concisa
- **Ejemplo**: "Ayudas para digitalización de PYMES mediante implementación de soluciones tecnológicas"

#### `descripcion_detallada` (string)
- **Fuente**: Texto del PDF
- **Reglas**:
  - Máximo 500 caracteres
  - 2-3 frases con detalles relevantes
- **Ejemplo**: "Subvenciones destinadas a empresas con menos de 250 empleados para proyectos de transformación digital. Se financian gastos de software, hardware, formación y consultoría tecnológica hasta el 70% del coste total."

---

## 2️⃣ CAMPOS DESDE BDNS SCRAPER (3 campos)

Estos campos se extraen del sitio web de BDNS usando Selenium.

#### `enlaces.url_bdns` (string URL)
- **Fuente**: BDNS scraper
- **Reglas**:
  - Se construye como: `https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias/{codigo_bdns}`
  - También puede venir del parámetro manual en formulario
- **Ejemplo**: "https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias/864249"

#### `enlaces.convocatoria` (string URL)
- **Fuente**:
  1. BDNS scraper (documentos extraídos con botón "Descargar")
  2. Parámetro manual en formulario
  3. Gemini AI (si aparece en el PDF)
- **Reglas**: URL del PDF de la convocatoria
- **Ejemplo**: "https://www.ejemplo.com/convocatoria.pdf"

#### `enlaces.bases_reguladoras` (string URL)
- **Fuente**:
  1. BDNS scraper (sección "Dirección electrónica de las bases reguladoras")
  2. Parámetro manual en formulario
- **Reglas**: URL del PDF de bases reguladoras
- **Busca en BDNS**:
  - XPath: `//div[contains(text(), 'Dirección electrónica de las bases reguladoras')]/..//a[@href]`
  - O enlaces con "bopa" o "bases" en el href
- **Ejemplo**: "https://www.bopa.es/bases-reguladoras.pdf"

---

## 3️⃣ CAMPOS AUTO-GENERADOS (5 campos)

Estos campos se generan automáticamente al cargar/guardar los programas mediante funciones de normalización.

#### `organismo_grupo` (string)
- **Fuente**: Auto-generado desde `organismo`
- **Reglas**: Normalización mediante `normalizar_organismo()`
- **Mapeo**:
  ```python
  'CDTI' → si contiene: 'CDTI', 'CDTI E.P.E', 'CDTI Innovación'...
  'IDEPA/Asturias' → si contiene: 'SEKUENS', 'SEPEPA', 'Principado de Asturias'...
  'Europea' → si contiene: 'EUIPO'
  'Financieras' → si contiene: 'Asturgar', 'SRP', 'MicroBank'...
  'Red.es' → si contiene: 'Red.es'
  'Ministerios' → si contiene: 'Ministerio'
  'EOI' → si contiene: 'EOI', 'Escuela de Organización Industrial'
  'Otros' → resto
  ```

#### `tipo_ayuda_grupo` (string)
- **Fuente**: Auto-generado desde `tipo_ayuda`
- **Reglas**: Normalización mediante `normalizar_tipo_ayuda()`
- **Mapeo**:
  ```python
  'Subvención' → si contiene: 'Subvención', 'a fondo perdido', 'Entregas dinerarias'...
  'Préstamo/Crédito' → si contiene: 'Préstamo', 'participativo', 'Reembolsable'...
  'Capital Riesgo/Inversión' → si contiene: 'Capital Riesgo', 'Coinversión'...
  'Aval/Garantía' → si contiene: 'Aval', 'Garantía'
  'Ayuda en especie' → si contiene: 'Ayuda en especie', 'Asesoramiento'...
  'Otros' → resto
  ```

#### `sectores_grupos` (array de strings)
- **Fuente**: Auto-generado desde `sectores`
- **Reglas**: Normalización mediante `normalizar_sector()` aplicado a cada elemento
- **Mapeo**:
  ```python
  'General/Multisectorial' → 'General', 'Multisectorial', 'Tecnológico'...
  'I+D+i / Tecnología' → 'TIC', 'Biotecnología', 'Nanotecnología', 'I+D'...
  'Industria/Manufactura' → 'Industrial', 'Manufacturera'...
  'Salud/Sanidad' → 'Salud', 'Salud Digital', 'Salud Animal'
  'Agroalimentación/Pesca' → 'Pesca', 'Acuicultura', 'Agroecología'...
  'Energía/Sostenibilidad' → 'Energías renovables', 'Economía Circular'...
  'Aeroespacial' → 'Aeroespacial'
  'Turismo/Hostelería' → 'Turismo', 'Establecimientos turísticos'
  'Cultura/Creativo' → 'Artesanía', 'Creativo'
  'Transporte/Logística' → 'Transporte', 'Logística', 'Electromovilidad'...
  'Otros' → resto
  ```

#### `beneficiarios_grupos` (array de strings)
- **Fuente**: Auto-generado desde `beneficiarios`
- **Reglas**: Normalización mediante `normalizar_beneficiario()` aplicado a cada elemento
- **Mapeo**:
  ```python
  'Todas las empresas' → 'Empresas', 'Sociedades', 'Cooperativas'
  'PYME' → 'PYMES', 'Pequeñas empresas', 'Microempresas'...
  'Gran Empresa' → 'Gran Empresa', 'Grandes Empresas'
  'Startups/EBT' → 'Startups', 'Empresas de Base Tecnológica', 'EBT'...
  'Autónomos' → 'Autónomos', 'Personas físicas emprendedoras'
  'Emprendedores' → 'Emprendedores', 'Emprendedores innovadores'...
  'Agrupaciones' → 'Agrupaciones de empresas', 'Agrupaciones de 2-6 empresas'...
  'Sector Público' → 'Ayuntamientos', 'Entidades Locales'...
  'Otros' → 'Particulares', 'Asociaciones', 'Artesanos'...
  ```

---

## 4️⃣ CAMPO CALCULADO (1 campo)

#### `id` (string)
- **Fuente**: Auto-generado desde `nombre`
- **Reglas**:
  - Identificador único basado en el nombre
  - Minúsculas
  - Sin acentos
  - Guiones en lugar de espacios
  - Sin caracteres especiales
- **Ejemplo**:
  - Nombre: "Subvenciones Digitalización PYMES 2025"
  - ID: "subvenciones-digitalizacion-pymes-2025"

---

## 📝 PROCESAMIENTO POST-EXTRACCIÓN

Después de la extracción con Gemini AI, se aplican estas transformaciones:

### **Conversión de tipos numéricos**

```python
# Campos de financiacion se convierten a float
financiacion.importe_maximo → float
financiacion.presupuesto_minimo → float
financiacion.presupuesto_maximo → float

# Si el valor es 'nan', 'No especificado', '', o null → se convierte a null
```

### **Normalización de codigo_bdns**

```python
# Se intenta convertir a int
"864249" → 864249
"864249.0" → 864249
864249.5 → 864249
```

### **Generación de campos normalizados**

Al cargar los programas (`load_all_financing_programs()`), se añaden automáticamente:

```python
programa['organismo_grupo'] = normalizar_organismo(programa['organismo'])
programa['tipo_ayuda_grupo'] = normalizar_tipo_ayuda(programa['tipo_ayuda'])
programa['sectores_grupos'] = [normalizar_sector(s) for s in programa['sectores']]
programa['beneficiarios_grupos'] = [normalizar_beneficiario(b) for b in programa['beneficiarios']]
```

---

## 🔍 FLUJO COMPLETO DE EXTRACCIÓN

```
1. Usuario ingresa URL BDNS o sube PDF
   ↓
2. BDNS Scraper (si URL BDNS)
   - Extrae: codigo_bdns, url_bdns, bases_reguladoras, documentos
   ↓
3. Extracción de PDF (PyPDF2)
   - Lee hasta 30 páginas
   - Máximo 100,000 caracteres
   - Limpia texto (espacios, saltos de línea)
   ↓
4. Gemini AI 2.5 Flash
   - Recibe: texto del PDF + metadatos opcionales (codigo_bdns, fecha_publicacion, urls)
   - Genera: JSON con 19 campos estructurados
   ↓
5. Validación y limpieza JSON
   - Limpia JSON malformado
   - Valida estructura
   ↓
6. Post-procesamiento
   - Conversión de tipos (float, int)
   - Generación de ID
   ↓
7. Normalización (al guardar/cargar)
   - Genera: organismo_grupo, tipo_ayuda_grupo, sectores_grupos, beneficiarios_grupos
   ↓
8. Almacenamiento en JSON
   - Guarda en: data/programas_financiacion.json
```

---

## 📁 ARCHIVOS CLAVE

| Archivo | Función |
|---------|---------|
| `utils/convocatoria_extractor_updated.py` | Extracción con Gemini AI (19 campos) |
| `utils/bdns_scraper.py` | Scraping BDNS con Selenium (3 campos enlaces) |
| `utils/financing_dashboard.py` | Normalización y filtros (5 campos auto-generados) |
| `data/programas_financiacion.json` | Almacenamiento de datos |

---

## ⚙️ CONFIGURACIÓN DE EXTRACCIÓN

### **Límites del PDF**
- **Páginas**: Hasta 30 páginas
- **Caracteres**: Hasta 100,000 caracteres
- **Timeout Gemini**: 60 segundos

### **Modelo AI**
- **Modelo**: Google Gemini 2.5 Flash (`gemini-2.0-flash-exp`)
- **Temperatura**: 0.2 (más determinista)
- **Token límite**: ~250KB de texto procesable

### **BDNS Scraper**
- **Timeout página**: 30 segundos
- **Espera carga Angular**: 3-5 segundos
- **Estrategias**:
  1. Buscar botón "Descargar" (`get_app`)
  2. Buscar botón "Permalink"
  3. Buscar enlaces genéricos con `/document/` o `.pdf`

---

## 🎯 CAMPOS PENDIENTES DE MEJORA

Basado en el análisis, estos son campos que podrías querer revisar:

1. **`tipo_proyecto`**: Actualmente es un string libre. ¿Debería normalizarse como los sectores?

2. **`ambito`**: Valores libres. ¿Sería mejor tener un conjunto fijo? (Nacional, Autonómico, Local, Europeo)

3. **`convocatoria.estado`**: Se calcula automáticamente, pero ¿debería ser editable manualmente?

4. **Nombres de campos financieros**: ¿Son suficientemente claros?
   - `presupuesto_minimo/maximo` → ¿Debería llamarse `presupuesto_proyecto_min/max`?
   - `importe_maximo` → ¿Es claro que es la cuantía máxima de la ayuda?

---

**Última actualización**: 29/10/2025
