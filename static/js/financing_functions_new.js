/**
 * Genera ejemplos de proyectos financiables basados en el nombre del programa y tipo de ayuda
 * @param {string} programName - Nombre del programa de financiación
 * @param {string} tipoAyuda - Tipo de ayuda (subvención, préstamo, etc.)
 * @returns {string} - Lista HTML de ejemplos de proyectos
 */
function generarEjemplosProyectos(programName, tipoAyuda) {
    let ejemplos = [];
    
    // Determinar categoría general del programa basado en su nombre y tipo
    const programaLower = (programName || '').toLowerCase();
    const tipoAyudaLower = (tipoAyuda || '').toLowerCase();
    
    // Ejemplos para programas de innovación/I+D
    if (programaLower.includes('innova') || programaLower.includes('i+d') || 
        programaLower.includes('investigación') || programaLower.includes('desarrollo')) {
        ejemplos = [
            'Desarrollo de un nuevo producto o servicio innovador',
            'Mejora significativa de procesos productivos mediante nuevas tecnologías',
            'Proyectos de investigación aplicada en colaboración con universidades o centros tecnológicos',
            'Implantación de tecnologías emergentes (IA, blockchain, etc.) en productos o servicios',
            'Diseño y desarrollo de prototipos y pruebas de concepto innovadoras'
        ];
    }
    // Ejemplos para programas de digitalización
    else if (programaLower.includes('digital') || programaLower.includes('kit digital') ||
            programaLower.includes('transformacion') || programaLower.includes('industria 4.0')) {
        ejemplos = [
            'Implementación de sistemas de gestión empresarial (ERP/CRM)',
            'Desarrollo de tienda online o mejora del comercio electrónico existente',
            'Digitalización de procesos internos y gestión documental',
            'Implementación de soluciones de ciberseguridad',
            'Desarrollo de aplicaciones móviles para negocio o servicio al cliente'
        ];
    }
    // Ejemplos para programas de sostenibilidad y eficiencia energética
    else if (programaLower.includes('sostenib') || programaLower.includes('verde') || 
             programaLower.includes('ecológ') || programaLower.includes('ambient') || 
             programaLower.includes('energía') || programaLower.includes('eficiencia')) {
        ejemplos = [
            'Instalación de sistemas de energía renovable (solar, eólica, etc.)',
            'Mejora de la eficiencia energética en instalaciones productivas',
            'Implementación de economía circular en procesos productivos',
            'Desarrollo de productos o servicios con menor impacto ambiental',
            'Proyectos de reducción de emisiones o huella de carbono'
        ];
    }
    // Ejemplos para programas de internacionalización
    else if (programaLower.includes('internacional') || programaLower.includes('export') || 
             programaLower.includes('exterior') || programaLower.includes('global')) {
        ejemplos = [
            'Participación en ferias internacionales como expositor',
            'Desarrollo de plan de marketing internacional',
            'Adaptación de productos o servicios a mercados exteriores',
            'Registro de patentes o marcas en mercados internacionales',
            'Establecimiento de filiales o delegaciones en el extranjero'
        ];
    }
    // Ejemplos para programas de emprendimiento o creación de empresas
    else if (programaLower.includes('emprend') || programaLower.includes('start') || 
             programaLower.includes('creación de empresa') || programaLower.includes('nueva empresa')) {
        ejemplos = [
            'Gastos de constitución y puesta en marcha de la empresa',
            'Desarrollo del producto mínimo viable (MVP)',
            'Primeras acciones comerciales y de marketing',
            'Contratación de personal clave para el arranque',
            'Alquiler de instalaciones y equipamiento inicial'
        ];
    }
    // Ejemplos genéricos si no se identifica una categoría específica
    else {
        ejemplos = [
            'Proyectos de mejora de la competitividad empresarial',
            'Inversiones en activos productivos para aumento de capacidad',
            'Desarrollo de nuevas líneas de negocio',
            'Proyectos de colaboración con otros agentes del sector',
            'Modernización de instalaciones y equipamiento'
        ];
    }
    
    // Si el tipo de ayuda es préstamo, adaptar los ejemplos mencionando inversiones mayores
    if (tipoAyudaLower.includes('préstamo') || tipoAyudaLower.includes('prestamo')) {
        for (let i = 0; i < ejemplos.length; i++) {
            ejemplos[i] = ejemplos[i] + ' (con inversiones significativas en activos)';
        }
    }
    // Si es subvención para pequeña empresa, adaptar los ejemplos
    else if (tipoAyudaLower.includes('subvención') && programaLower.includes('pyme')) {
        for (let i = 0; i < ejemplos.length; i++) {
            ejemplos[i] = ejemplos[i] + ' (adaptado a la escala de PYME)';
        }
    }
    
    return generarListaHTML(ejemplos);
}

/**
 * Genera consejos útiles para presentar solicitudes de financiación
 * @param {string} programName - Nombre del programa de financiación
 * @param {string} tipoAyuda - Tipo de ayuda (subvención, préstamo, etc.)
 * @returns {string} - HTML con consejos para presentar solicitudes
 */
function generarConsejosPresentacion(programName, tipoAyuda) {
    // Consejos generales para cualquier tipo de programa
    const consejosGenerales = [
        'Lea detenidamente las bases de la convocatoria antes de preparar la solicitud',
        'Identifique claramente los objetivos del proyecto y alinéelos con los del programa',
        'Incluya indicadores medibles para evaluar el éxito del proyecto',
        'Presente un presupuesto realista y bien justificado',
        'Destaque el impacto potencial (económico, social, ambiental) del proyecto'
    ];
    
    // Consejos específicos según el tipo de programa o ayuda
    let consejosEspecificos = [];
    
    const programaLower = (programName || '').toLowerCase();
    const tipoAyudaLower = (tipoAyuda || '').toLowerCase();
    
    // Consejos para programas de I+D+i
    if (programaLower.includes('innova') || programaLower.includes('i+d') || 
        programaLower.includes('investigación') || programaLower.includes('desarrollo')) {
        consejosEspecificos = [
            'Demuestre claramente el carácter innovador del proyecto',
            'Detalle el estado del arte y cómo su proyecto lo supera',
            'Incluya un plan de protección de resultados (patentes, modelos de utilidad, etc.)',
            'Destaque la capacidad técnica del equipo para ejecutar el proyecto',
            'Cuantifique el potencial de comercialización de los resultados'
        ];
    }
    // Consejos para programas de digitalización
    else if (programaLower.includes('digital') || programaLower.includes('transformacion') || 
             programaLower.includes('industria 4.0')) {
        consejosEspecificos = [
            'Presente un diagnóstico digital de partida de la empresa',
            'Defina claramente los objetivos de digitalización a alcanzar',
            'Detalle cómo la solución elegida se integra con los sistemas existentes',
            'Incluya un plan de formación para los empleados en las nuevas tecnologías',
            'Describa los indicadores de mejora que se utilizarán para medir el éxito'
        ];
    }
    // Consejos para programas de sostenibilidad
    else if (programaLower.includes('sostenib') || programaLower.includes('verde') || 
             programaLower.includes('ecológ') || programaLower.includes('ambient')) {
        consejosEspecificos = [
            'Calcule y presente el impacto ambiental actual y la mejora esperada',
            'Alinee el proyecto con los Objetivos de Desarrollo Sostenible (ODS)',
            'Incluya certificaciones ambientales que posea o planee obtener',
            'Detalle el ciclo de vida completo de productos o servicios',
            'Presente un plan de gestión de residuos o economía circular'
        ];
    }
    // Consejos para programas de internacionalización
    else if (programaLower.includes('internacional') || programaLower.includes('export') || 
             programaLower.includes('exterior')) {
        consejosEspecificos = [
            'Incluya un análisis de mercado del país/países objetivo',
            'Presente estudios de competencia internacional',
            'Detalle la estrategia de entrada y canal de distribución',
            'Incluya plan de marketing adaptado al mercado objetivo',
            'Documente la capacidad productiva para atender mercados internacionales'
        ];
    }
    // Consejos específicos según tipo de ayuda
    else if (tipoAyudaLower.includes('préstamo') || tipoAyudaLower.includes('prestamo')) {
        consejosEspecificos = [
            'Demuestre la capacidad de devolución del préstamo con proyecciones financieras',
            'Detalle la aplicación de los fondos con un cronograma de inversiones',
            'Presente garantías o avales si son requeridos',
            'Incluya un análisis de sensibilidad ante diversos escenarios',
            'Demuestre la solvencia financiera de la empresa'
        ];
    }
    else if (tipoAyudaLower.includes('subvención')) {
        consejosEspecificos = [
            'Justifique la necesidad de la subvención para realizar el proyecto',
            'Detalle el efecto incentivador de la ayuda',
            'Presente un plan de ejecución realista según los plazos de la convocatoria',
            'Incluya un plan de contingencia ante posibles desviaciones',
            'Detalle los gastos subvencionables según las bases de la convocatoria'
        ];
    }
    // Consejos genéricos si no se identifica una categoría específica
    else {
        consejosEspecificos = [
            'Adapte la solicitud al lenguaje y prioridades del organismo convocante',
            'Incluya cartas de apoyo de clientes o colaboradores relevantes',
            'Presente referencias de proyectos similares realizados con éxito',
            'Destaque la alineación del proyecto con estrategias regionales o nacionales',
            'Incluya un análisis de riesgos y plan de mitigación'
        ];
    }
    
    // Combinar todos los consejos y generar HTML
    return `
        <div class="row">
            <div class="col-md-6">
                <h6 class="mb-3"><i class="fas fa-list-ol me-2"></i>Consejos generales:</h6>
                ${generarListaHTML(consejosGenerales)}
            </div>
            <div class="col-md-6">
                <h6 class="mb-3"><i class="fas fa-star me-2"></i>Consejos específicos:</h6>
                ${generarListaHTML(consejosEspecificos)}
            </div>
        </div>
    `;
}

/**
 * Configura la funcionalidad de impresión para los resultados
 * Permite generar un documento imprimible con la información de los programas
 */
function setupPrintFunctionality() {
    const printBtn = document.querySelector('.print-results-btn');
    
    if (!printBtn) return;
    
    printBtn.addEventListener('click', function() {
        // Mostrar notificación de preparación
        showNotification('Preparando documento para impresión...', 'info');
        
        // Preparar contenido para imprimir
        const programCards = document.querySelectorAll('.program-card');
        
        if (!programCards.length) {
            showNotification('No hay programas para imprimir', 'warning');
            return;
        }
        
        // Crear encabezado del documento
        let printContent = `
            <div class="print-header">
                <h2>Programas de financiación recomendados</h2>
                <p>Fecha: ${new Date().toLocaleDateString()}</p>
            </div>
            <div class="print-description">
                <p>Este documento contiene información sobre programas de financiación que pueden ser relevantes para su proyecto o empresa. La información es orientativa y debe consultar las fuentes oficiales para obtener detalles actualizados.</p>
            </div>
        `;
        
        // Extraer información de cada tarjeta de programa
        programCards.forEach((card, index) => {
            const programTitle = card.querySelector('.card-title')?.textContent || 'Programa sin título';
            const programDescription = card.querySelector('.card-text')?.textContent || 'Sin descripción';
            const programDetails = card.querySelectorAll('.card-details li');
            const infoButton = card.querySelector('.info-btn');
            const programId = infoButton ? infoButton.getAttribute('data-program-id') : null;
            
            // Extraer detalles adicionales si están disponibles
            let detallesHTML = '<ul>';
            programDetails.forEach(detail => {
                detallesHTML += `<li>${detail.textContent}</li>`;
            });
            detallesHTML += '</ul>';
            
            // Crear sección de programa
            printContent += `
                <div class="print-program">
                    <h3>${index + 1}. ${programTitle}</h3>
                    <div class="print-program-description">
                        <p>${programDescription}</p>
                    </div>
                    <div class="print-program-details">
                        <h4>Detalles del programa:</h4>
                        ${detallesHTML}
                    </div>
                </div>
                <hr>
            `;
        });
        
        // Añadir pie de página
        printContent += `
            <div class="print-footer">
                <p>Documento generado por la Herramienta de Deducciones - ${new Date().toLocaleDateString()}</p>
                <p>La información contenida en este documento es orientativa. Consulte las bases de cada convocatoria.</p>
            </div>
        `;
        
        // Crear estilos para el documento imprimible
        const printStyles = `
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .print-header { margin-bottom: 20px; text-align: center; }
                .print-description { margin-bottom: 30px; }
                .print-program { margin-bottom: 20px; }
                .print-program h3 { color: #2c3e50; margin-bottom: 10px; }
                .print-program-details { margin-top: 15px; }
                .print-program-details h4 { font-size: 16px; margin-bottom: 10px; }
                .print-program-details ul { margin-top: 5px; }
                .print-footer { margin-top: 30px; font-size: 12px; text-align: center; color: #7f8c8d; }
                hr { border: 0; border-top: 1px solid #eee; margin: 20px 0; }
            </style>
        `;
        
        // Crear iframe para impresión
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        document.body.appendChild(iframe);
        
        // Escribir contenido en el iframe
        iframe.contentDocument.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Programas de Financiación - ${new Date().toLocaleDateString()}</title>
                ${printStyles}
            </head>
            <body>
                ${printContent}
            </body>
            </html>
        `);
        
        iframe.contentDocument.close();
        
        // Esperar a que se cargue el contenido y abrir diálogo de impresión
        setTimeout(() => {
            iframe.contentWindow.print();
            
            // Eliminar iframe después de imprimir
            setTimeout(() => {
                document.body.removeChild(iframe);
                showNotification('Documento preparado para impresión', 'success');
            }, 1000);
        }, 500);
    });
}

/**
 * Muestra notificaciones tipo toast para diferentes acciones del usuario
 * @param {string} mensaje - Mensaje a mostrar en la notificación
 * @param {string} tipo - Tipo de notificación (success, info, warning, error)
 */
function showNotification(mensaje, tipo = 'success') {
    // Crear contenedor de notificaciones si no existe
    let notifContainer = document.getElementById('notificationsContainer');
    
    if (!notifContainer) {
        notifContainer = document.createElement('div');
        notifContainer.id = 'notificationsContainer';
        notifContainer.className = 'position-fixed bottom-0 end-0 p-3';
        notifContainer.style.zIndex = '1050';
        document.body.appendChild(notifContainer);
    }
    
    // Generar ID único para el toast
    const toastId = 'toast-' + Date.now();
    
    // Definir icono según tipo de notificación
    let icon = 'info-circle';
    let bgColor = 'bg-info';
    
    switch (tipo) {
        case 'success':
            icon = 'check-circle';
            bgColor = 'bg-success';
            break;
        case 'warning':
            icon = 'exclamation-triangle';
            bgColor = 'bg-warning';
            break;
        case 'error':
            icon = 'times-circle';
            bgColor = 'bg-danger';
            break;
        case 'info':
        default:
            icon = 'info-circle';
            bgColor = 'bg-info';
            break;
    }
    
    // Crear el HTML del toast
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgColor} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${icon} me-2"></i> ${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
            </div>
        </div>
    `;
    
    // Agregar toast al contenedor
    notifContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Inicializar el toast y mostrarlo
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    
    toast.show();
    
    // Eliminar el toast del DOM después de ocultarse
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Formatea el texto original de la respuesta para mejorar su legibilidad
 * y corregir problemas con caracteres especiales como el símbolo del euro
 */
function formatOriginalResponse() {
    const originalResponseContainer = document.querySelector('.original-response-container');
    
    if (!originalResponseContainer) return;
    
    // Formatear texto para mejorar legibilidad
    const textContent = originalResponseContainer.textContent;
    
    // Corregir problema con el símbolo del euro
    let fixedEuroText = textContent.replace(/€/g, '€').replace(/�/g, '€');
    
    // Mejorar formato de listas detectando patrones
    fixedEuroText = fixedEuroText.replace(/^\s*[-•*]\s+(.+)$/gm, '<li>$1</li>');
    
    // Convertir bloques de <li> en listas completas
    fixedEuroText = fixedEuroText.replace(/<li>(.+?)<\/li>(\s*<li>(.+?)<\/li>)+/g, (match) => {
        return '<ul class="mb-3">' + match + '</ul>';
    });
    
    // Convertir URLs en enlaces clickables
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    fixedEuroText = fixedEuroText.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // Mejorar formato de párrafos
    let formattedText = '';
    const paragraphs = fixedEuroText.split(/\n\n+/);
    
    paragraphs.forEach(paragraph => {
        const trimmedParagraph = paragraph.trim();
        if (trimmedParagraph.length > 0) {
            // No envolver en <p> si ya es HTML (contiene etiquetas)
            if (trimmedParagraph.includes('<') && trimmedParagraph.includes('>')) {
                formattedText += trimmedParagraph + '\n\n';
            } else {
                formattedText += '<p class="mb-3">' + trimmedParagraph + '</p>\n';
            }
        }
    });
    
    // Mejorar formato de títulos detectando títulos potenciales
    formattedText = formattedText.replace(/<p class="mb-3">([^:]{2,50}):(\s*)<\/p>/g, '<h5 class="mt-4 mb-3">$1</h5>');
    
    // Destacar información importante con negrita
    const importantTerms = [
        'plazo', 'requisitos', 'documentación', 'importe', 'cuantía', 'financiación', 
        'subvención', 'préstamo', 'interés', 'amortización', 'garantías', 'elegible',
        'no elegible', 'compatible', 'incompatible', 'justificación', 'subsanación'
    ];
    
    importantTerms.forEach(term => {
        const regex = new RegExp(`\\b${term}\\b`, 'gi');
        formattedText = formattedText.replace(regex, '<strong>$&</strong>');
    });
    
    // Actualizar el contenido con formato mejorado
    originalResponseContainer.innerHTML = formattedText;
    
    // Añadir clases para mejorar la presentación
    originalResponseContainer.classList.add('p-3', 'border', 'rounded', 'bg-light');
}