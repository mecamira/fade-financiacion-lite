# Sistema de Diseño FADE - Guía de Implementación

## Introducción

Este documento describe el Sistema de Diseño FADE implementado para la herramienta de gestión de convocatorias. El sistema está basado en el manual de identidad corporativa de FADE y sigue las mejores prácticas de diseño de UI/UX para aplicaciones B2B.

## Paleta de Colores

### Color Corporativo Principal
- **Azul FADE**: `#0078BF` (RGB: 0, 120, 191)
  - PANTONE®: 300
  - Variable CSS: `--color-primary-500`

### Escala de Azul Primario
| Token | Valor HEX | Uso |
|-------|-----------|-----|
| `--color-primary-50` | `#E6F2FF` | Fondos de alerta (Info), Hover sutil |
| `--color-primary-100` | `#B3D7FF` | Fondos de tabla (Header), Tints |
| `--color-primary-500` | `#0078BF` | Color de marca, Botones primarios, Enlaces |
| `--color-primary-700` | `#005A91` | Hover de botón primario, Texto de alto contraste |
| `--color-primary-900` | `#003C60` | Texto de marca oscuro |

### Escala de Grises
| Token | Valor HEX | Uso |
|-------|-----------|-----|
| `--color-neutral-0` | `#FFFFFF` | Fondo de página, Fondo de tarjeta |
| `--color-neutral-50` | `#F7FAFC` | Fondo de "Zebra Stripe", Fondo sutil |
| `--color-neutral-200` | `#E2E8F0` | Bordes de input, Separadores |
| `--color-neutral-700` | `#4A5568` | Texto secundario, Etiquetas (Labels) |
| `--color-neutral-900` | `#1A202C` | Texto del cuerpo principal |

**IMPORTANTE**: Nunca usar `#000000` (negro puro). Siempre usar `--color-neutral-900` para el texto.

### Colores Semánticos
| Token | Valor HEX | Uso |
|-------|-----------|-----|
| `--color-success-500` | `#38A169` | Éxito, Validación positiva |
| `--color-warning-500` | `#D69E2E` | Advertencia, Pendiente |
| `--color-error-500` | `#E53E3E` | Error, Validación negativa, Peligro |

### Paleta de Visualización de Datos
| Token | Valor HEX | Color |
|-------|-----------|-------|
| `--color-data-1` | `#0078BF` | Azul FADE |
| `--color-data-2` | `#00A0A0` | Teal |
| `--color-data-3` | `#5552A3` | Púrpura |
| `--color-data-4` | `#E07C00` | Naranja |

## Tipografía

### Familia de Fuentes
- **Principal**: Inter (Google Fonts)
- **Variable CSS**: `--font-family-base`

### Escala Tipográfica

| Caso de Uso | Tamaño | Peso | Altura Línea | Espaciado | Variable CSS |
|-------------|--------|------|--------------|-----------|--------------|
| Display (H1) | 32px | 700 | 40px | -0.5px | `--font-size-display` |
| Title (H2) | 24px | 600 | 32px | 0px | `--font-size-title` |
| Subtitle (H3) | 18px | 600 | 24px | 0px | `--font-size-subtitle` |
| Body (Default) | 16px | 400 | 24px | 0px | `--font-size-body` |
| Body (Strong) | 16px | 600 | 24px | 0px | - |
| Table Header | 14px | 600 | 20px | 0.2px | `--font-size-table-header` |
| Table Cell | 14px | 400 | 20px | 0px | `--font-size-table-cell` |
| Label (Forms) | 14px | 500 | 20px | 0px | `--font-size-label` |
| Caption | 12px | 400 | 16px | 0.1px | `--font-size-caption` |
| Button | 14px | 600 | 16px | 0.2px | `--font-size-button` |

## Sistema de Espaciado

Base: **8px**

| Variable | Valor | Uso |
|----------|-------|-----|
| `--spacing-1` | 8px | Espaciado mínimo |
| `--spacing-2` | 16px | Espaciado estándar |
| `--spacing-3` | 24px | Espaciado medio |
| `--spacing-4` | 32px | Espaciado grande |
| `--spacing-5` | 40px | Espaciado extra grande |
| `--spacing-6` | 48px | Espaciado máximo |

**Regla**: Todos los márgenes, rellenos y alturas deben ser múltiplos de 8px.

## Componentes

### Botones

#### Botón Primario (Acción principal)
```html
<button class="btn btn-primary">Guardar</button>
```
- Fondo: `--color-primary-500`
- Texto: `--color-neutral-0`
- Hover: `--color-primary-700`

#### Botón Secundario (Acción alternativa)
```html
<button class="btn btn-secondary">Cancelar</button>
<button class="btn btn-outline-primary">Exportar</button>
```
- Fondo: `--color-neutral-0`
- Borde: `--color-primary-500`
- Texto: `--color-primary-500`
- Hover: Fondo `--color-primary-50`

#### Botón Terciario/Ghost (Acción menor)
```html
<button class="btn btn-tertiary">Ver Detalles</button>
<button class="btn btn-link">Ver Detalles</button>
```
- Fondo: Transparente
- Texto: `--color-primary-500`
- Hover: Fondo `--color-primary-50`

### Tarjetas KPI

```html
<div class="kpi-card">
    <div class="kpi-card-title">TÍTULO DEL KPI</div>
    <div class="kpi-card-value">123</div>
    <div class="kpi-card-context">Contexto o tendencia</div>
</div>
```

- Fondo: `--color-neutral-0`
- Borde: 1px solid `--color-neutral-200`
- Border-radius: `--border-radius-md` (8px)
- Sombra: `--shadow-sm`

### Tablas de Datos

```html
<table class="table table-striped table-hover">
    <thead>
        <tr>
            <th>Columna 1</th>
            <th>Columna 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Dato 1</td>
            <td>Dato 2</td>
        </tr>
    </tbody>
</table>
```

**Especificaciones**:
- **Header**:
  - Fondo: `--color-primary-50`
  - Texto: `--color-primary-900`
  - Borde inferior: 2px solid `--color-primary-500`
  - Font: 14px, semibold
- **Celdas**:
  - Padding: 12px 16px
  - Font: 14px, regular
  - Borde: 1px solid `--color-neutral-200`
- **Zebra Striping**:
  - Impares: `--color-neutral-0`
  - Pares: `--color-neutral-50`
- **Hover**: `--color-primary-50`

### Formularios

#### Labels
```html
<label for="input-id" class="form-label">Etiqueta del Campo</label>
<input type="text" class="form-control" id="input-id">
```

**IMPORTANTE**:
- Las etiquetas deben estar SIEMPRE visibles
- No usar placeholders como etiquetas
- Labels fuera del campo de entrada

#### Estados de Focus
```css
.form-control:focus {
    border-color: var(--color-primary-500);
    box-shadow: 0 0 0 3px var(--color-primary-50);
}
```

#### Campos Requeridos
```html
<label for="input" class="form-label required">Campo Requerido</label>
```
- Se añade automáticamente un asterisco rojo (*) después del label

### Alertas

```html
<div class="alert alert-success">Mensaje de éxito</div>
<div class="alert alert-warning">Mensaje de advertencia</div>
<div class="alert alert-danger">Mensaje de error</div>
<div class="alert alert-info">Mensaje informativo</div>
```

### Badges

```html
<span class="badge bg-primary">Primario</span>
<span class="badge bg-success">Éxito</span>
<span class="badge bg-warning">Advertencia</span>
<span class="badge bg-secondary">Secundario</span>
```

## Guía de Estilo: "Hacer" y "No Hacer"

### ✅ HACER

1. ✅ Usar la familia de fuentes Inter para todo el texto de la UI
2. ✅ Usar los tokens de color (variables CSS) en lugar de códigos HEX hardcodeados
3. ✅ Usar la unidad de espaciado base de 8px (múltiplos: 8px, 16px, 24px, 32px...)
4. ✅ Aplicar el estilo Zebra (Zebra Striping) a todas las tablas de datos
5. ✅ Usar `--color-neutral-900` para texto principal
6. ✅ Mantener las etiquetas de formulario siempre visibles
7. ✅ Usar los estados de focus con borde azul y sombra

### ❌ NO HACER

1. ❌ No usar `#000000` (negro puro) para texto. Usar `--color-neutral-900` en su lugar
2. ❌ No usar la fuente del logotipo para texto de UI
3. ❌ No usar degradados o sombras de texto no definidos en este sistema
4. ❌ No usar placeholders como etiquetas de formulario
5. ❌ No usar valores de espaciado que no sean múltiplos de 8px
6. ❌ No hardcodear colores. Siempre usar variables CSS

## Arquitectura de Archivos

```
static/css/
├── fade_design_system.css   # Sistema de diseño FADE (variables y componentes)
├── style.css                 # Estilos personalizados adicionales
└── [otros archivos CSS]

templates/
├── base.html                 # Template base con carga de fuentes y CSS
└── [otros templates]
```

## Orden de Carga de CSS

**IMPORTANTE**: El orden es crítico para que el sistema de diseño funcione correctamente:

```html
<!-- 1. Google Fonts - Inter -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- 2. Bootstrap CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- 3. Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">

<!-- 4. FADE Design System - DEBE IR DESPUÉS DE BOOTSTRAP -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/fade_design_system.css') }}">

<!-- 5. Custom CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
```

## Uso de Variables CSS en JavaScript

Para acceder a las variables CSS desde JavaScript (útil para gráficos):

```javascript
// Obtener valor de una variable CSS
const primaryColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-primary-500').trim();

// Ejemplo con Chart.js
backgroundColor: 'rgba(0, 120, 191, 0.5)',  // color-data-1: Azul FADE
borderColor: 'rgba(0, 120, 191, 1)',
```

## Colores para Gráficos (Chart.js)

Usar esta paleta en orden para gráficos:

```javascript
const chartColors = [
    'rgba(0, 120, 191, 0.7)',    // color-data-1: Azul FADE
    'rgba(0, 160, 160, 0.7)',    // color-data-2: Teal
    'rgba(85, 82, 163, 0.7)',    // color-data-3: Púrpura
    'rgba(224, 124, 0, 0.7)',    // color-data-4: Naranja
    'rgba(56, 161, 105, 0.7)',   // color-success-500
    'rgba(214, 158, 46, 0.7)',   // color-warning-500
];
```

## Accesibilidad

- Todos los colores cumplen con WCAG 2.1 AA para contraste
- La paleta de datos es accesible para daltónicos
- Los estados de focus son claramente visibles
- Textos legibles en tamaños pequeños gracias a Inter

## Escalabilidad

Este sistema de diseño es reutilizable para futuras herramientas internas de FADE:
- CRM Interno
- Gestión de Socios
- Otras aplicaciones B2B

Mantener coherencia con este sistema garantiza:
- Identidad de marca consistente
- Ahorro de tiempo de desarrollo
- Experiencia de usuario coherente

## Soporte y Mantenimiento

Para modificaciones al sistema de diseño:
1. Actualizar `/static/css/fade_design_system.css`
2. Documentar cambios en este archivo
3. Probar en todos los templates
4. Validar accesibilidad

## Referencias

- Manual de Identidad Corporativa FADE
- Análisis del sitio web fade.es
- Google Fonts: [Inter](https://fonts.google.com/specimen/Inter)
- WCAG 2.1: [Accesibilidad Web](https://www.w3.org/WAI/WCAG21/quickref/)
