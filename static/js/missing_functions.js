/**
 * Extrae requisitos de un texto de descripción
 * @param {string} texto - Texto de descripción del programa
 * @returns {string} HTML con los requisitos extraídos o genéricos
 */
function extraerRequisitos(texto) {
    if (!texto) return generarRequisitosGenericos();
    
    // Patrones para detectar requisitos en el texto
    const patrones = [
        /requisitos[:\s]+(.*?)(?=\.|$)/i,
        /podrán ser beneficiarios[:\s]+(.*?)(?=\.|$)/i,
        /dirigido a[:\s]+(.*?)(?=\.|$)/i,
        /empresas que[:\s]+(.*?)(?=\.|$)/i,
        /condiciones[:\s]+(.*?)(?=\.|$)/i
    ];
    
    let requisitosTexto = '';
    
    // Buscar en cada patrón
    for (let patron of patrones) {
        const coincidencia = texto.match(patron);
        if (coincidencia && coincidencia[1]) {
            requisitosTexto += coincidencia[1].trim() + '. ';
        }
    }
    
    // Buscar listas de requisitos (elementos con guión o numerados)
    const lineas = texto.split('\n');
    let listaRequisitos = [];
    let enListaRequisitos = false;
    
    for (let linea of lineas) {
        if (linea.match(/requisitos|beneficiarios|elegibilidad/i)) {
            enListaRequisitos = true;
            continue;
        }
        
        if (enListaRequisitos && linea.trim().match(/^[-•*\d]|^\w+\)/)) {
            listaRequisitos.push(linea.trim().replace(/^[-•*\d\w)\s.]+/, '').trim());
        } else if (enListaRequisitos && linea.trim() === '') {
            enListaRequisitos = false;
        }
    }
    
    // Si encontramos requisitos explícitos o en formato lista
    if (requisitosTexto || listaRequisitos.length > 0) {
        let resultado = '';
        
        if (requisitosTexto) {
            resultado += `<p>${requisitosTexto}</p>`;
        }
        
        if (listaRequisitos.length > 0) {
            resultado += generarListaHTML(listaRequisitos);
        }
        
        return resultado;
    }
    
    // Si no encontramos requisitos explícitos, generar requisitos genéricos
    return generarRequisitosGenericos();
}

/**
 * Genera una lista HTML a partir de un array de textos
 * @param {Array} items - Array de elementos para la lista
 * @returns {string} HTML con la lista
 */
function generarListaHTML(items) {
    if (!items || items.length === 0) return '';
    
    let html = '<ul class="list-group list-group-flush">';
    
    for (let item of items) {
        html += `<li class="list-group-item"><i class="fas fa-check-circle text-success me-2"></i>${item}</li>`;
    }
    
    html += '</ul>';
    return html;
}

/**
 * Genera requisitos genéricos cuando no se encuentran específicos
 * @returns {string} HTML con los requisitos genéricos
 */
function generarRequisitosGenericos() {
    const requisitosGenericos = [
        'Ser empresa legalmente constituida y con actividad económica en España',
        'Estar al corriente de pago con la Seguridad Social y la Agencia Tributaria',
        'No estar incurso en ninguna de las prohibiciones previstas en la Ley General de Subvenciones',
        'Disponer de la capacidad administrativa, financiera y operativa para cumplir con los objetivos del proyecto',
        'Cumplir con la normativa de minimis (en caso de subvenciones)'
    ];
    
    return `
        <div class="alert alert-secondary">
            <p><i class="fas fa-info-circle me-2"></i>No se han encontrado requisitos específicos en la descripción. Estos son los requisitos habituales para este tipo de programas:</p>
        </div>
        ${generarListaHTML(requisitosGenericos)}
    `;
}

/**
 * Extrae información sobre plazos de solicitud
 * @param {string} convocatoria - Texto de la convocatoria
 * @param {string} descripcion - Descripción completa del programa
 * @returns {string} Texto con los plazos identificados
 */
function extraerPlazos(convocatoria, descripcion) {
    // Si la convocatoria ya contiene información de fechas, la utilizamos
    if (convocatoria && convocatoria.match(/\d{1,2}\/\d{1,2}\/\d{2,4}|\d{4}$/)) {
        return convocatoria;
    }
    
    // Buscar patrones de plazos en la descripción
    const patronesPlazos = [
        /plazo[^.]*hasta el (\d{1,2} de [^\d.]+ de \d{4})/i,
        /fecha límite[^.]*(\d{1,2}\/\d{1,2}\/\d{2,4})/i,
        /convocatoria abierta desde (\d{1,2}\/\d{1,2}\/\d{2,4})[^.]*hasta (\d{1,2}\/\d{1,2}\/\d{2,4})/i,
        /convocatoria (\d{4})[^.]*abierta/i
    ];
    
    for (let patron of patronesPlazos) {
        const coincidencia = descripcion.match(patron);
        if (coincidencia) {
            if (coincidencia[2]) { // Si hay fecha de inicio y fin
                return `Del ${coincidencia[1]} al ${coincidencia[2]}`;
            } else {
                return coincidencia[1]; // Solo una fecha
            }
        }
    }
    
    // Si es una convocatoria permanente
    if (descripcion.match(/convocatoria permanente|convocatoria abierta todo el año|ventanilla abierta/i)) {
        return 'Convocatoria permanente (ventanilla abierta)';
    }
    
    // Si no se encuentra información específica
    return convocatoria || 'Consultar convocatoria actual';
}

/**
 * Genera información sobre documentación necesaria
 * @param {string} tipoAyuda - Tipo de ayuda o programa
 * @param {string} descripcion - Descripción completa del programa
 * @returns {string} HTML con la documentación necesaria
 */
function generarInfoDocumentacion(tipoAyuda, descripcion) {
    // Buscar menciones a documentación en la descripción
    let documentacionMencionada = [];
    
    const patronesDoc = [
        /documentación requerida[:\s]+(.*?)(?=\.|$)/i,
        /deberá[n]? presentar[:\s]+(.*?)(?=\.|$)/i,
        /documentos necesarios[:\s]+(.*?)(?=\.|$)/i
    ];
    
    for (let patron of patronesDoc) {
        const coincidencia = descripcion.match(patron);
        if (coincidencia && coincidencia[1]) {
            documentacionMencionada.push(coincidencia[1].trim());
        }
    }
    
    // Si encontramos menciones específicas a la documentación
    if (documentacionMencionada.length > 0) {
        return `
            <p>Según la información disponible, deberá presentar:</p>
            <p>${documentacionMencionada.join('. ')}</p>
            <hr>
            <p><i class="fas fa-info-circle me-2"></i>Adicionalmente, es habitual que se requiera la siguiente documentación:</p>
            ${generarDocumentacionTipica(tipoAyuda)}
        `;
    }
    
    // Si no hay menciones específicas, proporcionar la documentación típica
    return `
        <div class="alert alert-secondary">
            <p><i class="fas fa-info-circle me-2"></i>No se ha encontrado información específica sobre la documentación requerida. Estos son los documentos habitualmente solicitados para este tipo de programa:</p>
        </div>
        ${generarDocumentacionTipica(tipoAyuda)}
    `;
}

/**
 * Genera listas de documentación típica según el tipo de ayuda
 * @param {string} tipoAyuda - Tipo de ayuda o programa
 * @returns {string} HTML con la lista de documentación
 */
function generarDocumentacionTipica(tipoAyuda) {
    // Documentación común para todos los tipos de ayuda
    const documentacionComun = [
        'Formulario de solicitud cumplimentado',
        'CIF/NIF de la empresa o entidad solicitante',
        'Escrituras de constitución y estatutos',
        'Acreditación del representante legal',
        'Certificados de estar al corriente de pagos con la Seguridad Social y Hacienda',
        'Declaración responsable de no estar incurso en prohibiciones para obtener la condición de beneficiario'
    ];
    
    // Documentación específica según tipo de ayuda
    let documentacionEspecifica = [];
    
    if (tipoAyuda) {
        const tipoAyudaLower = tipoAyuda.toLowerCase();
        
        if (tipoAyudaLower.includes('subvención') || tipoAyudaLower.includes('ayuda directa')) {
            documentacionEspecifica = [
                'Memoria técnica del proyecto',
                'Presupuesto detallado',
                'Plan de financiación',
                'Declaración de otras ayudas solicitadas o concedidas',
                'Declaración de minimis (si aplica)'
            ];
        } else if (tipoAyudaLower.includes('préstamo')) {
            documentacionEspecifica = [
                'Memoria técnica y económica del proyecto',
                'Cuentas anuales de los últimos 2-3 ejercicios',
                'Plan de negocio a 3-5 años',
                'Garantías ofrecidas (si aplica)',
                'Declaración de endeudamiento actual'
            ];
        } else if (tipoAyudaLower.includes('deducción') || tipoAyudaLower.includes('fiscal')) {
            documentacionEspecifica = [
                'Memoria técnica de actividades de I+D+i',
                'Justificación de gastos e inversiones realizadas',
                'Contabilidad separada o código contable específico',
                'Contratos del personal investigador (si aplica)',
                'Informe motivado o certificación (recomendado)'
            ];
        } else if (tipoAyudaLower.includes('garantía') || tipoAyudaLower.includes('aval')) {
            documentacionEspecifica = [
                'Estados financieros',
                'Valoración de garantías',
                'Plan de negocio',
                'Justificación de necesidad de financiación',
                'Declaración de patrimonio'
            ];
        } else {
            // Documentación genérica para otros tipos de ayuda
            documentacionEspecifica = [
                'Memoria técnica del proyecto',
                'Presupuesto detallado por partidas',
                'Justificación de la necesidad de la ayuda',
                'Impacto esperado y resultados cuantificables'
            ];
        }
    }
    
    // Combinar documentación común y específica
    return generarListaHTML([...documentacionComun, ...documentacionEspecifica]);
}

/**
 * Genera ejemplos de proyectos financiables
 * @param {string} programName - Nombre del programa
 * @param {string} tipoAyuda - Tipo de ayuda o programa
 * @returns {string} HTML con ejemplos de proyectos
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
    else if (programaLower.includes('digital') || programaLower.includes('industria 4.0') || 
             programaLower.includes('transformación') || programaLower.includes('tic')) {
        ejemplos = [
            'Implementación de soluciones de comercio electrónico y marketing digital',
            'Digitalización de procesos internos mediante implantación de ERP/CRM',
            'Proyectos de ciberseguridad y protección de datos',
            'Automatización de líneas de producción mediante sistemas de control avanzados',
            'Implementación de sistemas de monitorización remota y mantenimiento predictivo'
        ];
    }
    // Ejemplos para programas de sostenibilidad/economía circular
    else if (programaLower.includes('sostenib') || programaLower.includes('verde') || 
             programaLower.includes('circular') || programaLower.includes('ecológic')) {
        ejemplos = [
            'Instalación de sistemas de energía renovable en las instalaciones',
            'Optimización de procesos para reducir el consumo energético y emisiones',
            'Desarrollo de envases y embalajes sostenibles y biodegradables',
            'Implementación de sistemas de gestión y valorización de residuos',
            'Proyectos para reducir el consumo de agua y materias primas no renovables'
        ];
    }
    // Ejemplos para programas de internacionalización
    else if (programaLower.includes('internacional') || programaLower.includes('exterior') || 
             programaLower.includes('export')) {
        ejemplos = [
            'Participación en ferias internacionales para promoción de productos',
            'Adaptación de productos a normativas técnicas de mercados extranjeros',
            'Desarrollo de estrategias de marketing digital para mercados internacionales',
            'Creación de una red comercial en el exterior mediante agentes o distribuidores',
            'Implantación de filiales o delegaciones en mercados estratégicos'
        ];
    }
    // Ejemplos genéricos para otros tipos de programa
    else {
        ejemplos = [
            'Ampliación o modernización de la capacidad productiva',
            'Contratación y formación de personal especializado',
            'Adquisición de equipamiento técnico avanzado',
            'Proyectos de innovación en productos o servicios',
            'Mejora de la eficiencia energética y sostenibilidad'
        ];
    }
    
    // Si el tipo de ayuda es préstamo, adaptar los ejemplos mencionando inversiones mayores
    if (tipoAyudaLower.includes('préstamo')) {
        for (let i = 0; i < ejemplos.length; i++) {
            ejemplos[i] = ejemplos[i] + ' (con inversiones significativas en activos)';
        }
    }
    
    return generarListaHTML(ejemplos);
}

/**
 * Genera consejos para presentar solicitudes de financiación
 * @param {string} programName - Nombre del programa
 * @param {string} tipoAyuda - Tipo de ayuda o programa
 * @returns {string} HTML con consejos para presentación
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
    if (programaLower.includes('i+d') || programaLower.includes('innova') || 
        programaLower.includes('investigación')) {
        consejosEspecificos = [
            'Detalle el estado del arte y destaque claramente la innovación de su propuesta',
            'Demuestre la capacidad técnica del equipo para desarrollar el proyecto',
            'Elabore un plan de explotación comercial de los resultados',
            'Si es posible, incluya una estrategia de protección de la propiedad intelectual',
            'Considere incluir colaboraciones con centros de investigación o universidades'
        ];
    }
    // Consejos para subvenciones
    else if (tipoAyudaLower.includes('subvención') || tipoAyudaLower.includes('ayuda directa')) {
        consejosEspecificos = [
            'Asegúrese de que su proyecto cumple todos los requisitos de elegibilidad',
            'Presente toda la documentación administrativa requerida sin errores',
            'Calcule correctamente los costes elegibles según las bases',
            'Demuestre la adicionalidad de la ayuda (que el proyecto no se realizaría sin ella)',
            'Detalle claramente el cronograma de ejecución y los hitos del proyecto'
        ];
    }
    // Consejos para préstamos
    else if (tipoAyudaLower.includes('préstamo')) {
        consejosEspecificos = [
            'Demuestre la capacidad de devolución del préstamo con proyecciones financieras',
            'Detalle el plan de negocio y la generación de ingresos derivada del proyecto',
            'Destaque las garantías disponibles para respaldar la operación',
            'Presente un análisis de sensibilidad con diferentes escenarios',
            'Incluya un plan de contingencia en caso de desviaciones'
        ];
    }
    // Consejos para deducciones fiscales
    else if (tipoAyudaLower.includes('deducción') || tipoAyudaLower.includes('fiscal')) {
        consejosEspecificos = [
            'Documente rigurosamente todas las actividades de I+D+i realizadas',
            'Mantenga una contabilidad detallada y separada de los gastos del proyecto',
            'Considere obtener un informe motivado o certificación para mayor seguridad jurídica',
            'Involucre al departamento financiero/fiscal desde el inicio del proyecto',
            'Conserve toda la documentación técnica que justifique la novedad del proyecto'
        ];
    }
    
    // Si no hay consejos específicos, añadir algunos genéricos adicionales
    if (consejosEspecificos.length === 0) {
        consejosEspecificos = [
            'Adapte su propuesta a los criterios de evaluación del programa',
            'Cuide la presentación y redacción de la memoria técnica',
            'Incluya información visual (gráficos, diagramas) para facilitar la comprensión',
            'No deje la solicitud para el último momento, evite prisas y posibles errores',
            'Consulte con un asesor especializado para maximizar sus posibilidades'
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
 * Configura la funcionalidad de impresión de resultados
 */
function setupPrintFunctionality() {
    const printBtn = document.querySelector('.print-results-btn');
    
    if (!printBtn) return;
    
    printBtn.addEventListener('click', function() {
        // Preparar contenido para imprimir
        const programCards = document.querySelectorAll('.program-card');
        let printContent = `
            <div class="print-header">
                <h2>Programas de financiación recomendados</h2>
                <p>Fecha: ${new Date().toLocaleDateString()}</p>
            </div>
        `;
        
        // Añadir cada programa
        programCards.forEach((card, index) => {
            const nombre = card.querySelector('.program-card-header h4')?.textContent || `Programa ${index + 1}`;
            const organismo = getCardDetail(card, 'Organismo');
            const tipoAyuda = getCardDetail(card, 'Tipo de ayuda');
            const intensidad = getCardDetail(card, 'Intensidad');
            const descripcion = card.querySelector('.program-description p')?.textContent || '';
            const justificacion = card.querySelector('.justification-text')?.textContent || '';
            
            printContent += `
                <div class="program-print-item">
                    <h3>${nombre}</h3>
                    <div class="program-print-details">
                        <p><strong>Organismo:</strong> ${organismo}</p>
                        <p><strong>Tipo de ayuda:</strong> ${tipoAyuda}</p>
                        <p><strong>Intensidad:</strong> ${intensidad}</p>
                    </div>
                    <div class="program-print-description">
                        <h4>Descripción</h4>
                        <p>${descripcion}</p>
                    </div>
                    <div class="program-print-justification">
                        <h4>Justificación</h4>
                        <p>${justificacion}</p>
                    </div>
                </div>
            `;
        });
        
        // Crear iframe para impresión
        const printFrame = document.createElement('iframe');
        printFrame.style.position = 'absolute';
        printFrame.style.top = '-9999px';
        document.body.appendChild(printFrame);
        
        // Escribir contenido en el iframe
        printFrame.contentDocument.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Programas de Financiación</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .print-header { text-align: center; margin-bottom: 30px; }
                    .program-print-item { margin-bottom: 30px; page-break-inside: avoid; }
                    .program-print-item h3 { background-color: #f0f0f0; padding: 10px; }
                    .program-print-details { margin: 15px 0; }
                    .program-print-description, .program-print-justification { margin-top: 15px; }
                    h4 { border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                    @media print {
                        body { margin: 0; }
                        .program-print-item { page-break-inside: avoid; }
                    }
                </style>
            </head>
            <body>
                ${printContent}
            </body>
            </html>
        `);
        
        // Cerrar el documento y ejecutar impresión
        printFrame.contentDocument.close();
        printFrame.contentWindow.focus();
        
        // Mostrar notificación e imprimir
        showNotification('Preparando documento para impresión...');
        setTimeout(() => {
            printFrame.contentWindow.print();
            // Eliminar el iframe después de imprimir
            setTimeout(() => document.body.removeChild(printFrame), 500);
        }, 1000);
    });
}

/**
 * Muestra una notificación tipo toast
 * @param {string} mensaje - Mensaje a mostrar
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
    
    // Definir ícono según tipo
    let icono = 'info-circle';
    let colorClass = 'bg-info';
    
    if (tipo === 'success') {
        icono = 'check-circle';
        colorClass = 'bg-success';
    } else if (tipo === 'warning') {
        icono = 'exclamation-triangle';
        colorClass = 'bg-warning';
    } else if (tipo === 'error') {
        icono = 'times-circle';
        colorClass = 'bg-danger';
    }
    
    // Crear el toast
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="5000">
            <div class="toast-header ${colorClass} text-white">
                <i class="fas fa-${icono} me-2"></i>
                <strong class="me-auto">Herramienta de Deducciones</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${mensaje}
            </div>
        </div>
    `;
    
    // Añadir el toast al contenedor
    notifContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Inicializar y mostrar el toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Eliminar el toast del DOM después de ocultarse
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Formatea el texto original de respuesta (si existe)
 */
function formatOriginalResponse() {
    const originalResponseContainer = document.querySelector('.original-response-container');
    
    if (!originalResponseContainer) return;
    
    // Formatear texto para mejorar legibilidad
    const textContent = originalResponseContainer.textContent;
    
    // Corregir problema con el símbolo del euro
    const fixedEuroText = textContent.replace(/€/g, '€').replace(/�/g, '€');
    
    // Convertir URLs en enlaces clickables
    const linkifiedText = fixedEuroText.replace(
        /(https?:\/\/[^\s]+)/g, 
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    // Mejorar formato de listas
    let formattedText = linkifiedText;
    
    // Detectar posibles listas y aplicar formato
    if (formattedText.includes('\n- ') || formattedText.includes('\n* ')) {
        const lines = formattedText.split('\n');
        let inList = false;
        let formattedLines = [];
        
        for (let line of lines) {
            if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
                if (!inList) {
                    formattedLines.push('<ul>');
                    inList = true;
                }
                formattedLines.push('<li>' + line.trim().substring(2) + '</li>');
            } else {
                if (inList) {
                    formattedLines.push('</ul>');
                    inList = false;
                }
                formattedLines.push(line);
            }
        }
        
        if (inList) {
            formattedLines.push('</ul>');
        }
        
        formattedText = formattedLines.join('\n');
    }
    
    // Actualizar el contenido con formato mejorado
    originalResponseContainer.innerHTML = formattedText;
}
