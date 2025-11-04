# Mapeos de Normalización - Documento de Trabajo

Este documento lista TODOS los campos normalizados (actuales y propuestos) con sus mapeos completos.

**Objetivo**: Revisar, ajustar y aprobar los mapeos antes de implementarlos en producción.

**Instrucciones para colaboradores**:
- ✏️ Añade, elimina o modifica valores en cada grupo
- 📝 Añade comentarios con `<!-- Comentario aquí -->`
- ✅ Marca como `[APROBADO]` cuando esté listo
- ⚠️ Marca como `[REVISAR]` si necesita discusión

---

## 📊 RESUMEN DE CAMPOS NORMALIZADOS

| Campo Original | Campo Normalizado | Estado | Grupos | Última actualización |
|----------------|-------------------|--------|--------|---------------------|
| `organismo` | `organismo_grupo` | ✅ En producción | 8 | 29/10/2025 |
| `tipo_ayuda` | `tipo_ayuda_grupo` | ✅ En producción | 5 | 29/10/2025 |
| `sectores` (array) | `sectores_grupos` (array) | ✅ En producción | 10 | 29/10/2025 |
| `beneficiarios` (array) | `beneficiarios_grupos` (array) | ✅ En producción | 9 | 29/10/2025 |
| `tipo_proyecto` | `tipo_proyecto_grupo` | 🆕 Propuesto | 12 | - |
| `ambito` | `ambito_grupo` | 🆕 Propuesto | 5 | - |

---

## 1️⃣ ORGANISMO → ORGANISMO_GRUPO

**Estado**: ✅ En producción
**Ubicación código**: `utils/financing_dashboard.py` líneas 9-18
**Lógica**: Busca coincidencias parciales (contains) en minúsculas

### Mapeos actuales:

```python
ORGANISMO_GRUPOS = {
    'CDTI': [
        'CDTI',
        'CDTI E.P.E',
        'CDTI Innovación',
        'CDTI (con fondos FEMPA)',
        'CDTI (en colaboración con AEI)'
    ],

    'IDEPA/Asturias': [
        'SEKUENS',
        'SEPEPA',
        'Consejería',
        'Principado de Asturias',
        'IDEPA',
        'Ayuntamiento de Gijón',
        'Ayuntamiento de Avilés',
        'Sociedad de Desarrollo'
    ],

    'Europea': [
        'EUIPO'
        # ⚠️ [REVISAR] Añadir más organismos europeos?
    ],

    'Financieras': [
        'Asturgar',
        'SRP',
        'MicroBank',
        'TORSA CAPITAL'
        # ⚠️ [REVISAR] Añadir: ICO, ENISA, COFIDES?
    ],

    'Red.es': [
        'Red.es'
    ],

    'Ministerios': [
        'Ministerio de Hacienda',
        'Ministerio'
        # ⚠️ [REVISAR] Demasiado genérico? ¿Separar por ministerio específico?
    ],

    'EOI': [
        'EOI',
        'Escuela de Organización Industrial'
    ],

    'Otros': []  # Cualquier organismo que no coincida con los anteriores
}
```

### 📝 Comentarios y propuestas:

<!-- Ejemplo de comentario:
- ¿Añadir categoría "CCAA" para agrupar todas las comunidades autónomas?
- ¿Separar "Financieras públicas" de "Financieras privadas"?
-->

---

## 2️⃣ TIPO_AYUDA → TIPO_AYUDA_GRUPO

**Estado**: ✅ En producción
**Ubicación código**: `utils/financing_dashboard.py` líneas 21-33
**Lógica**: Busca coincidencias parciales (contains) en minúsculas

### Mapeos actuales:

```python
TIPO_AYUDA_GRUPOS = {
    'Subvención': [
        'Subvención',
        'Subvención a fondo perdido',
        'Subvención (concesión directa)',
        'Subvención (Bono Digital)',
        'Subvención (Reembolso/Bonos)',
        'Entregas dinerarias sin contraprestación'
    ],

    'Préstamo/Crédito': [
        'Préstamo',
        'Préstamo participativo',
        'Préstamo (con aval)',
        'Ayuda Parcialmente Reembolsable'
    ],

    'Capital Riesgo/Inversión': [
        'Capital Riesgo',
        'Capital Riesgo / Coinversión',
        'Capital Riesgo, Préstamos Participativos',
        'Capital Semilla, Préstamo Participativo, Capital Riesgo'
    ],

    'Aval/Garantía': [
        'Aval',
        'Aval (para anticipo de subvención)'
    ],

    'Ayuda en especie': [
        'Ayuda en especie',
        'Ayuda en especie (Asesoramiento)',
        'Ayuda en especie (Plan de Aceleración)'
    ],

    'Otros': []  # Cualquier tipo de ayuda que no coincida
}
```

### 📝 Comentarios y propuestas:

<!-- Ejemplo:
- ¿Añadir categoría "Ventajas fiscales" para bonificaciones y deducciones?
- ¿Separar "Préstamo" de "Crédito"?
-->

---

## 3️⃣ SECTORES → SECTORES_GRUPOS

**Estado**: ✅ En producción
**Ubicación código**: `utils/financing_dashboard.py` líneas 35-59
**Lógica**: Busca coincidencias bidireccionales (valor in sector OR sector in valor)

### Mapeos actuales:

```python
SECTOR_GRUPOS = {
    'General/Multisectorial': [
        'General',
        'Multisectorial',
        'General (con exclusiones)',
        'Tecnológico / Innovador (Multisectorial)',
        'Multisectorial (con exclusiones)',
        'Multisectorial (Base Tecnológica)',
        'General (Propiedad Intelectual)',
        'General (Proyectos viables)'
    ],

    'I+D+i / Tecnología': [
        'Tecnologías prioritarias Cervera',
        'Base Tecnológica',
        'TIC',
        'Biotecnología',
        'Biomedicina',
        'Nanotecnología',
        'Fotónica',
        'Tecnología avanzada',
        'Innovación',
        'Industrias culturales',
        'Servicios avanzados',
        'I+D'
        # ⚠️ [REVISAR] ¿Añadir: IA, Blockchain, IoT, Ciberseguridad?
    ],

    'Industria/Manufactura': [
        'Industrial',
        'Servicios conexos a la industria',
        'Industrias transformadoras',
        'Infraestructura Industrial',
        'Industria Alimentaria',
        'Industria Manufacturera'
    ],

    'Salud/Sanidad': [
        'Salud',
        'Salud de Vanguardia',
        'Salud Digital',
        'Salud Animal'
    ],

    'Agroalimentación/Pesca': [
        'Pesca',
        'Acuicultura',
        'Agroecología',
        'Mejora genética',
        'Transformación y Comercialización Pesca/Acuicultura',
        'Sanidad animal'
        # ⚠️ [REVISAR] ¿Separar Agricultura de Pesca?
    ],

    'Energía/Sostenibilidad': [
        'Energías renovables',
        'Movilidad Sostenible',
        'Energía Limpia',
        'Economía Circular',
        'Descontaminación',
        'Construcción Sostenible'
    ],

    'Aeroespacial': [
        'Aeroespacial'
    ],

    'Turismo/Hostelería': [
        'Turismo',
        'Establecimientos turísticos innovadores'
    ],

    'Cultura/Creativo': [
        'Artesanía',
        'Ejes Estratégicos Gijón Transforma (Creativo'
        # ⚠️ [REVISAR] ¿Añadir: Audiovisual, Videojuegos, Diseño?
    ],

    'Transporte/Logística': [
        'Transporte Aéreo',
        'Logística Inteligente',
        'Electromovilidad',
        'Vehículos Autónomos'
    ],

    'Otros': []
}
```

### 📝 Comentarios y propuestas:

<!-- Ejemplo:
- ¿Crear categoría "Digital/Software" separada de I+D+i?
- ¿Añadir categoría "Construcción" (no solo sostenible)?
-->

---

## 4️⃣ BENEFICIARIOS → BENEFICIARIOS_GRUPOS

**Estado**: ✅ En producción
**Ubicación código**: `utils/financing_dashboard.py` líneas 61-77
**Lógica**: Busca coincidencias bidireccionales (valor in beneficiario OR beneficiario in valor)

### Mapeos actuales:

```python
BENEFICIARIO_GRUPOS = {
    'Todas las empresas': [
        'Empresas',
        'Empresas (individualmente)',
        'Sociedades',
        'Cooperativas'
    ],

    'PYME': [
        'PYMES',
        'PYMES Españolas',
        'Pequeñas empresas',
        'Medianas Empresas',
        'MIDCAPS',
        'Microempresas',
        'Micropymes'
    ],

    'Gran Empresa': [
        'Gran Empresa',
        'Grandes Empresas'
    ],

    'Startups/EBT': [
        'Startups',
        'Empresas de Base Tecnológica',
        'EBT',
        'Pequeñas empresas innovadoras',
        'Empresas emergentes'
    ],

    'Autónomos': [
        'Autónomos',
        'Personas físicas emprendedoras'
    ],

    'Emprendedores': [
        'Emprendedores',
        'Emprendedores innovadores',
        'Mujeres emprendedoras y empresarias'
        # ⚠️ [REVISAR] ¿Separar "Emprendedores" de "Mujeres emprendedoras"?
    ],

    'Agrupaciones': [
        'Agrupaciones de empresas',
        'Agrupaciones de 2-6 empresas',
        'Agrupaciones de 3-8 empresas'
    ],

    'Sector Público': [
        'Ayuntamientos',
        'Entidades Locales',
        'Sector Público',
        'Corporaciones',
        'Sociedades públicas'
    ],

    'Otros': [
        'Particulares',
        'Comunidades Propietarios',
        'Entidades sin ánimo de lucro',
        'Asociaciones',
        'Artesanos'
        # ⚠️ [REVISAR] ¿Crear categoría "ONG/Sin ánimo de lucro"?
    ]
}
```

### 📝 Comentarios y propuestas:

<!-- Ejemplo:
- ¿Crear categoría específica "Investigadores/Centros de investigación"?
- ¿Separar "Particulares" de "Otros"?
-->

---

## 5️⃣ TIPO_PROYECTO → TIPO_PROYECTO_GRUPO (🆕 PROPUESTO)

**Estado**: 🆕 Propuesto - NO implementado
**Ubicación código**: A crear en `utils/financing_dashboard.py`
**Lógica propuesta**: Busca coincidencias parciales (contains) en minúsculas

### Análisis de valores existentes:

Basándome en las convocatorias reales del sistema, estos son los tipos de proyecto más comunes:
- Investigación, desarrollo, innovación
- Digitalización de PYMES
- Contratación de personal
- Inversión en activos productivos
- Formación y capacitación
- Internacionalización
- Sostenibilidad y economía circular
- Propiedad intelectual
- Marketing y comercialización

### Mapeos propuestos:

```python
TIPO_PROYECTO_GRUPOS = {
    'I+D+i': [
        'Investigación',
        'Desarrollo',
        'Innovación',
        'I+D',
        'I+D+i',
        'Proyectos de investigación',
        'Desarrollo experimental',
        'Investigación industrial',
        'Innovación tecnológica',
        'Proyectos innovadores'
    ],

    'Digitalización': [
        'Digitalización',
        'Transformación digital',
        'Tecnologías digitales',
        'Soluciones digitales',
        'Implementación TIC',
        'Software',
        'Hardware tecnológico',
        'Ciberseguridad'
    ],

    'Inversión productiva': [
        'Inversión en activos',
        'Activos productivos',
        'Maquinaria',
        'Equipamiento',
        'Infraestructura',
        'Modernización',
        'Ampliación de instalaciones',
        'Nuevas instalaciones'
    ],

    'Recursos Humanos': [
        'Contratación',
        'Contratación de personal',
        'Recursos humanos',
        'Incorporación de talento',
        'Personal cualificado',
        'Formación',
        'Capacitación',
        'Formación de empleados'
    ],

    'Internacionalización': [
        'Internacionalización',
        'Expansión internacional',
        'Exportación',
        'Mercados exteriores',
        'Comercio exterior',
        'Apertura de mercados'
    ],

    'Sostenibilidad': [
        'Sostenibilidad',
        'Economía circular',
        'Eficiencia energética',
        'Energías renovables',
        'Descarbonización',
        'Movilidad sostenible',
        'Proyectos verdes',
        'Medio ambiente'
    ],

    'Propiedad Intelectual': [
        'Propiedad intelectual',
        'Propiedad industrial',
        'Patentes',
        'Marcas',
        'Diseños industriales',
        'Registro de patentes'
    ],

    'Marketing/Comercialización': [
        'Marketing',
        'Comercialización',
        'Promoción',
        'Comunicación',
        'Branding',
        'Estrategias de marketing',
        'Publicidad'
    ],

    'Creación empresas': [
        'Creación de empresas',
        'Emprendimiento',
        'Puesta en marcha',
        'Inicio de actividad',
        'Startups',
        'Nueva empresa'
    ],

    'Cooperación empresarial': [
        'Cooperación',
        'Proyectos colaborativos',
        'Consorcios',
        'Agrupaciones empresariales',
        'Proyectos conjuntos',
        'Colaboración empresarial'
    ],

    'Mejora competitividad': [
        'Mejora de competitividad',
        'Competitividad',
        'Productividad',
        'Eficiencia operativa',
        'Optimización de procesos',
        'Mejora continua'
    ],

    'Diversificación': [
        'Diversificación',
        'Nuevas líneas de negocio',
        'Ampliación de actividad',
        'Nuevos productos',
        'Nuevos servicios'
    ],

    'General': [
        'General',
        'Multisectorial',
        'Diversos tipos de proyecto',
        'Proyectos viables',
        'Cualquier proyecto'
    ],

    'Otros': []
}
```

### 📝 Comentarios y propuestas:

<!--
IMPORTANTE: Este es un campo NUEVO. Revisar especialmente:
1. ¿Faltan categorías importantes?
2. ¿Hay solapamientos entre categorías?
3. ¿Los nombres de categorías son claros para los usuarios finales?
-->

---

## 6️⃣ AMBITO → AMBITO_GRUPO (🆕 PROPUESTO)

**Estado**: 🆕 Propuesto - NO implementado
**Ubicación código**: A crear en `utils/financing_dashboard.py`
**Lógica propuesta**: Busca coincidencias exactas o parciales

### Análisis de valores existentes:

Del análisis de convocatorias reales:
- Nacional
- Comunidad Autónoma
- Regional
- Local
- Europeo
- Internacional

### Mapeos propuestos:

```python
AMBITO_GRUPOS = {
    'Europeo': [
        'Europeo',
        'UE',
        'Unión Europea',
        'Comunitario',
        'Europa',
        'Programa europeo'
    ],

    'Nacional': [
        'Nacional',
        'Estatal',
        'España',
        'Ámbito nacional',
        'Todo el territorio nacional'
    ],

    'Autonómico': [
        'Comunidad Autónoma',
        'Autonómico',
        'Regional',
        'CCAA',
        # Específicos de cada CCAA:
        'Asturias',
        'Principado de Asturias',
        'Cataluña',
        'Madrid',
        'Andalucía',
        'Valencia',
        'Galicia',
        'País Vasco',
        'Castilla y León',
        'Castilla-La Mancha',
        'Aragón',
        'Extremadura',
        'Murcia',
        'Canarias',
        'Baleares',
        'Navarra',
        'La Rioja',
        'Cantabria'
    ],

    'Local': [
        'Local',
        'Provincial',
        'Municipal',
        'Comarcal',
        'Ayuntamiento',
        'Diputación',
        # Ciudades específicas si es necesario:
        'Gijón',
        'Oviedo',
        'Avilés'
    ],

    'Internacional': [
        'Internacional',
        'Global',
        'Fuera de la UE',
        'Terceros países'
    ],

    'Otros': []
}
```

### 📝 Comentarios y propuestas:

<!--
¿Es necesario listar TODAS las CCAA o con la palabra "Comunidad Autónoma" es suficiente?
¿Separar "Regional" de "Autonómico" o son lo mismo?
-->

---

## 🔧 IMPLEMENTACIÓN TÉCNICA

### Función de normalización genérica:

```python
def normalizar_campo(valor, mapeo_grupos):
    """
    Normaliza un valor según el mapeo de grupos proporcionado

    Args:
        valor: String a normalizar
        mapeo_grupos: Dict con {grupo: [valores_posibles]}

    Returns:
        String con el grupo normalizado o 'Otros'
    """
    if not valor:
        return 'Otros'

    valor_lower = valor.lower()

    for grupo, valores in mapeo_grupos.items():
        for valor_posible in valores:
            if valor_posible.lower() in valor_lower or valor_lower in valor_posible.lower():
                return grupo

    return 'Otros'
```

### Integración en `load_all_financing_programs()`:

```python
# Añadir al cargar programas:
programa['tipo_proyecto_grupo'] = normalizar_campo(
    programa.get('tipo_proyecto'),
    TIPO_PROYECTO_GRUPOS
)

programa['ambito_grupo'] = normalizar_campo(
    programa.get('ambito'),
    AMBITO_GRUPOS
)
```

---

## 📋 CHECKLIST DE APROBACIÓN

Antes de implementar en producción, verificar:

- [ ] **Organismo_grupo**: Revisar y aprobar mapeos
- [ ] **Tipo_ayuda_grupo**: Revisar y aprobar mapeos
- [ ] **Sectores_grupos**: Revisar y aprobar mapeos
- [ ] **Beneficiarios_grupos**: Revisar y aprobar mapeos
- [ ] **Tipo_proyecto_grupo**: Aprobar propuesta y ajustar mapeos
- [ ] **Ambito_grupo**: Aprobar propuesta y ajustar mapeos
- [ ] Validar que no hay solapamientos problemáticos
- [ ] Validar que los nombres de grupos son claros para usuarios finales
- [ ] Probar normalización con datos reales

---

## 📝 NOTAS PARA COLABORADORES

### Cómo añadir/modificar valores:

1. **Añadir un nuevo valor a un grupo existente**:
   ```python
   'PYME': [
       'PYMES',
       'Pequeñas empresas',
       'Nuevo valor aquí'  # ← Añadir aquí
   ]
   ```

2. **Crear un nuevo grupo**:
   ```python
   'Nombre del nuevo grupo': [
       'Valor 1',
       'Valor 2',
       'Valor 3'
   ]
   ```

3. **Marcar para revisión**:
   ```python
   # ⚠️ [REVISAR] Descripción del problema o duda
   ```

### Criterios de diseño:

- **Grupos amplios pero significativos**: No crear demasiados grupos pequeños
- **Nombres claros**: Los usuarios finales verán estos nombres en filtros
- **Sin solapamientos**: Un valor no debería encajar en múltiples grupos
- **Escalable**: Fácil añadir nuevos valores sin reestructurar

---

**Última actualización**: 31/10/2025
**Responsable**: Equipo FADE
**Próxima revisión**: Pendiente de aprobación
