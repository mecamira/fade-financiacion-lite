/**
 * JavaScript para la página de resultados de financiación
 */
document.addEventListener('DOMContentLoaded', function() {
    // Animación de entrada para las tarjetas
    animateProgramCards();
    
    // Configurar modal de contacto
    setupContactModal();
    
    // Configurar modales informativos
    setupInfoModals();
    
    // Configurar impresión
    setupPrintFunctionality();
    
    // Formatear texto original (si existe)
    formatOriginalResponse();
    
    // Añadir evento para forzar el formateo si se actualiza el contenido dinámicamente
    const refreshFormattingBtn = document.querySelector('.refresh-formatting-btn');
    if (refreshFormattingBtn) {
        refreshFormattingBtn.addEventListener('click', function() {
            formatOriginalResponse();
            showNotification('Formato actualizado correctamente', 'success');
        });
    }
});

/**
 * Anima las tarjetas de programas con un efecto de entrada
 */
function animateProgramCards() {
    const cards = document.querySelectorAll('.program-card');
    const futureCards = document.querySelectorAll('.future-program-card');
    
    // Animar tarjetas de programas actuales
    if (cards.length > 0) {        
        // Añadir las animaciones con un pequeño retraso entre cada tarjeta
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('animated');
            }, 100 + (index * 150)); // 100ms iniciales + 150ms por tarjeta
        });
    }
    
    // Animar tarjetas de programas futuros
    if (futureCards.length > 0) {
        // Esperar a que terminen las animaciones de las tarjetas actuales
        const startDelay = cards.length > 0 ? cards.length * 150 + 300 : 100;
        
        futureCards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('animated');
            }, startDelay + (index * 100)); // Animación algo más rápida para las futuras
        });
    }
}

/**
 * Configura el modal de contacto con asesor
 */
function setupContactModal() {
    const contactBtn = document.querySelector('.contact-advisor-btn');
    
    if (!contactBtn) return;
    
    contactBtn.addEventListener('click', function() {
        // Verificar si ya existe el modal, si no, crearlo
        let contactModal = document.getElementById('contactModal');
        
        if (!contactModal) {
            // Crear el modal dinámicamente
            contactModal = createContactModal();
            document.body.appendChild(contactModal);
            
            // Inicializar el modal de Bootstrap
            new bootstrap.Modal(contactModal);
        }
        
        // Abrir el modal
        const bsModal = bootstrap.Modal.getInstance(contactModal) || new bootstrap.Modal(contactModal);
        bsModal.show();
    });
}



/**
 * Configura modales informativos para programas
 */
function setupInfoModals() {
    // Configurar botones de información del encabezado
    const headerInfoButtons = document.querySelectorAll('.info-button-header');
    
    headerInfoButtons.forEach((button) => {
        // Obtener el nombre del programa
        const programName = button.getAttribute('data-program');
        
        // Configurar evento de clic
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            // Buscar la tarjeta del programa
            const card = this.closest('.program-card');
            if (card) {
                showProgramInfoModal(programName, card);
            }
        });
    });
}

/**
 * Muestra modal con información detallada de un programa
 */
function showProgramInfoModal(programName, card) {
    // Recopilar información del programa desde la tarjeta
    const organismo = getCardDetail(card, 'Organismo');
    const tipoAyuda = getCardDetail(card, 'Tipo de ayuda');
    const intensidad = getCardDetail(card, 'Intensidad');
    const convocatoria = getCardDetail(card, 'Convocatoria');
    const justificacion = card.querySelector('.justification-text')?.textContent || '';
    const descripcion = card.querySelector('.program-description p')?.textContent || '';
    
    // Extraer/Generar información adicional util
    const requisitosInfo = extraerRequisitos(descripcion);
    const plazosSolicitud = extraerPlazos(convocatoria, descripcion);
    const documentacionInfo = generarInfoDocumentacion(tipoAyuda, descripcion);
    const ejemplosProyectos = generarEjemplosProyectos(programName, tipoAyuda);
    const consejosPresentacion = generarConsejosPresentacion(programName, tipoAyuda);
    
    // Crear modal
    let infoModal = document.getElementById('programInfoModal');
    
    if (!infoModal) {
        infoModal = document.createElement('div');
        infoModal.className = 'modal fade';
        infoModal.id = 'programInfoModal';
        infoModal.tabIndex = '-1';
        document.body.appendChild(infoModal);
    }
    
    // Actualizar contenido
    infoModal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Información detallada: ${programName}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <!-- Pestañas de navegación -->
                    <ul class="nav nav-tabs" id="programInfoTabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="info-tab" data-bs-toggle="tab" data-bs-target="#info"
                                type="button" role="tab" aria-controls="info" aria-selected="true">
                                <i class="fas fa-info-circle me-1"></i>Resumen
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="requisitos-tab" data-bs-toggle="tab" data-bs-target="#requisitos"
                                type="button" role="tab" aria-controls="requisitos" aria-selected="false">
                                <i class="fas fa-clipboard-check me-1"></i>Requisitos
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="documentacion-tab" data-bs-toggle="tab" data-bs-target="#documentacion"
                                type="button" role="tab" aria-controls="documentacion" aria-selected="false">
                                <i class="fas fa-file-alt me-1"></i>Documentación
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="consejos-tab" data-bs-toggle="tab" data-bs-target="#consejos"
                                type="button" role="tab" aria-controls="consejos" aria-selected="false">
                                <i class="fas fa-lightbulb me-1"></i>Consejos
                            </button>
                        </li>
                    </ul>
                    
                    <!-- Contenido de las pestañas -->
                    <div class="tab-content pt-3" id="programInfoTabsContent">
                        <!-- Pestaña de Información General -->
                        <div class="tab-pane fade show active" id="info" role="tabpanel" aria-labelledby="info-tab">
                            <div class="alert alert-primary">
                                <div class="d-flex">
                                    <div class="me-2"><i class="fas fa-bookmark fa-2x"></i></div>
                                    <div>
                                        <h5 class="alert-heading">Programa: ${programName}</h5>
                                        <p class="mb-0">Gestionado por ${organismo}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <div class="card h-100">
                                        <div class="card-header bg-light">Detalles básicos</div>
                                        <div class="card-body">
                                            <dl class="row mb-0">
                                                <dt class="col-sm-4">Tipo:</dt>
                                                <dd class="col-sm-8">${tipoAyuda}</dd>
                                                
                                                <dt class="col-sm-4">Intensidad:</dt>
                                                <dd class="col-sm-8">${intensidad}</dd>
                                                
                                                <dt class="col-sm-4">Convocatoria:</dt>
                                                <dd class="col-sm-8">${convocatoria}</dd>
                                                
                                                ${plazosSolicitud ? `<dt class="col-sm-4">Plazos:</dt>
                                                <dd class="col-sm-8">${plazosSolicitud}</dd>` : ''}
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-md-6">
                                    <div class="card h-100">
                                        <div class="card-header bg-light">Adecuación a su proyecto</div>
                                        <div class="card-body">
                                            <p>${justificacion}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="card mb-0">
                                <div class="card-header bg-light">Descripción completa</div>
                                <div class="card-body">
                                    <p>${descripcion}</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Pestaña de Requisitos y Elegibilidad -->
                        <div class="tab-pane fade" id="requisitos" role="tabpanel" aria-labelledby="requisitos-tab">
                            <div class="alert alert-warning">
                                <h5 class="alert-heading"><i class="fas fa-exclamation-triangle me-2"></i>Requisitos de elegibilidad</h5>
                                <p>Para acceder a este programa, deberá cumplir con los siguientes requisitos:</p>
                            </div>
                            
                            <div class="card mb-3">
                                <div class="card-body">
                                    ${requisitosInfo}
                                </div>
                            </div>
                            
                            <div class="card mb-0">
                                <div class="card-header bg-light">Ejemplos de proyectos financiables</div>
                                <div class="card-body">
                                    ${ejemplosProyectos}
                                </div>
                            </div>
                        </div>
                        
                        <!-- Pestaña de Documentación -->
                        <div class="tab-pane fade" id="documentacion" role="tabpanel" aria-labelledby="documentacion-tab">
                            <div class="alert alert-info">
                                <h5 class="alert-heading"><i class="fas fa-file-alt me-2"></i>Documentación necesaria</h5>
                                <p>Para solicitar esta ayuda, generalmente necesitará presentar los siguientes documentos:</p>
                            </div>
                            
                            <div class="card mb-3">
                                <div class="card-body">
                                    ${documentacionInfo}
                                </div>
                            </div>
                            
                            <div class="card mb-0">
                                <div class="card-header bg-light">Enlaces de interés</div>
                                <div class="card-body">
                                    <p>Para más información sobre este programa, visite la web oficial del organismo correspondiente:</p>
                                    <div class="d-grid gap-2 d-md-flex">
                                        <a href="#" class="btn btn-outline-primary" target="_blank" 
                                           onclick="window.open('https://www.google.com/search?q=${encodeURIComponent(programName + ' ' + organismo)}', '_blank'); return false;">
                                            <i class="fas fa-external-link-alt me-1"></i> Buscar información oficial
                                        </a>
                                        <a href="#" class="btn btn-outline-secondary" target="_blank" 
                                           onclick="alert('Esta funcionalidad estará disponible próximamente.'); return false;">
                                            <i class="fas fa-file-pdf me-1"></i> Bases reguladoras
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Pestaña de Consejos -->
                        <div class="tab-pane fade" id="consejos" role="tabpanel" aria-labelledby="consejos-tab">
                            <div class="alert alert-success">
                                <h5 class="alert-heading"><i class="fas fa-lightbulb me-2"></i>Consejos para su solicitud</h5>
                                <p>Recomendaciones para aumentar sus posibilidades de éxito en este programa:</p>
                            </div>
                            
                            <div class="card mb-0">
                                <div class="card-body">
                                    ${consejosPresentacion}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    <button type="button" class="btn btn-primary contact-advisor-btn">
                        <i class="fas fa-user-tie me-1"></i> Contactar asesor
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Inicializar y mostrar modal
    const modalInstance = new bootstrap.Modal(infoModal);
    modalInstance.show();
    
    // Configurar botón de contacto en el modal
    setTimeout(() => {
        const contactBtn = infoModal.querySelector('.contact-advisor-btn');
        if (contactBtn) {
            contactBtn.addEventListener('click', function() {
                modalInstance.hide();
                document.querySelector('.contact-advisor-btn').click();
            });
        }
    }, 500);
}

/**
 * Obtiene un detalle específico de la tarjeta de programa
 */
function getCardDetail(card, label) {
    const items = card.querySelectorAll('.detail-label');
    for (let item of items) {
        if (item.textContent.includes(label)) {
            return item.nextElementSibling?.textContent || 'No especificado';
        }
    }
    return 'No especificado';
}

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

/**
 * Genera una lista HTML a partir de un array de textos
 * @param {Array} items - Array de textos
 * @returns {string} Lista HTML
 */
function generarListaHTML(items) {
    if (!items || !Array.isArray(items) || items.length === 0) {
        return '<p class="text-muted">No hay información disponible.</p>';
    }
    
    let html = '<ul class="mb-0">';
    
    items.forEach(item => {
        html += `<li>${item}</li>`;
    });
    
    html += '</ul>';
    
    return html;
}

/**
 * Extrae requisitos de un texto de descripción
 * @param {string} texto - Texto de descripción
 * @returns {string} HTML con los requisitos extraídos
 */
function extraerRequisitos(texto) {
    if (!texto) return generarRequisitosGenericos();
    
    const textoLower = texto.toLowerCase();
    const frases = texto.split(/[.!?]\s+/);
    const requisitos = [];
    
    // Buscar frases que contengan pistas de requisitos
    frases.forEach(frase => {
        const fraseLower = frase.toLowerCase().trim();
        
        if (fraseLower.includes('requisito') || 
            fraseLower.includes('debe cumplir') || 
            fraseLower.includes('será necesario') || 
            fraseLower.includes('elegible') ||
            fraseLower.includes('podrán acceder') || 
            fraseLower.includes('podrán solicitar') ||
            fraseLower.includes('estar al corriente') ||
            fraseLower.includes('tener la condición') ||
            fraseLower.startsWith('tener') ||
            fraseLower.startsWith('estar') ||
            fraseLower.startsWith('no haber') ||
            (fraseLower.includes('mínimo') && fraseLower.includes('empleados'))) {
            
            // Limpiar la frase
            let requisitoLimpio = frase.trim();
            if (!requisitoLimpio.endsWith('.') && !requisitoLimpio.endsWith('!') && !requisitoLimpio.endsWith('?')) {
                requisitoLimpio += '.';
            }
            
            requisitos.push(requisitoLimpio);
        }
    });
    
    // Si no hemos encontrado requisitos específicos, buscar palabras clave en el texto
    if (requisitos.length === 0) {
        if (textoLower.includes('pyme') || textoLower.includes('pequeña y mediana')) {
            requisitos.push('Ser PYME según la definición de la UE (menos de 250 empleados y volumen de negocio anual inferior a 50M€).');
        }
        
        if (textoLower.includes('startup') || textoLower.includes('nueva creación')) {
            requisitos.push('Empresa de reciente creación (menos de 5 años desde su constitución).');
        }
        
        if (textoLower.includes('innovador') || textoLower.includes('innovación')) {
            requisitos.push('El proyecto debe tener un componente innovador demostrable.');
        }
        
        if (textoLower.includes('viabilidad') || textoLower.includes('viable')) {
            requisitos.push('El proyecto debe demostrar viabilidad técnica, económica y comercial.');
        }
    }
    
    // Si seguimos sin requisitos, generar genéricos
    if (requisitos.length === 0) {
        return generarRequisitosGenericos();
    }
    
    return generarListaHTML(requisitos);
}

/**
 * Genera requisitos genéricos para cuando no se pueden extraer del texto
 * @returns {string} HTML con requisitos genéricos
 */
function generarRequisitosGenericos() {
    const requisitosGenericos = [
        'Estar al corriente de las obligaciones tributarias y con la Seguridad Social.',
        'No estar incurso en ninguna de las prohibiciones previstas en la Ley General de Subvenciones.',
        'Realizar la actividad o proyecto que fundamenta la concesión de la ayuda.',
        'Justificar el cumplimiento de los requisitos y condiciones establecidos en la normativa.',
        'Someterse a las actuaciones de comprobación requeridas por el organismo concedente.'
    ];
    
    return generarListaHTML(requisitosGenericos);
}

/**
 * Extrae información sobre plazos de solicitud
 * @param {string} convocatoria - Texto de la convocatoria
 * @param {string} descripcion - Texto de descripción
 * @returns {string} Información sobre plazos
 */
function extraerPlazos(convocatoria, descripcion) {
    // Si no hay información de convocatoria ni descripción, retornar vacío
    if (!convocatoria && !descripcion) return '';
    
    // Buscar patrones de fechas en la convocatoria o descripción
    const textoCompleto = (convocatoria + ' ' + descripcion).toLowerCase();
    
    // Buscar patrones comunes de plazos
    if (textoCompleto.includes('plazo') && textoCompleto.includes('abierto')) {
        return 'Convocatoria con plazo abierto. Consulte la web oficial para fechas específicas.';
    }
    
    // Buscar patrones de fecha (básico)
    const patronesFecha = [
        /hasta\s+el\s+(\d{1,2}\s+de\s+[a-zéñ]+\s+de\s+\d{4})/i,
        /del\s+(\d{1,2}\s+de\s+[a-zéñ]+)\s+al\s+(\d{1,2}\s+de\s+[a-zéñ]+\s+de\s+\d{4})/i,
        /plazo.*?(\d{1,2}\s+de\s+[a-zéñ]+\s+de\s+\d{4})/i
    ];
    
    for (let patron of patronesFecha) {
        const match = textoCompleto.match(patron);
        if (match) {
            return match[0].charAt(0).toUpperCase() + match[0].slice(1);
        }
    }
    
    // Si no se encontró nada específico, dar información genérica según la convocatoria
    if (convocatoria.toLowerCase().includes('permanente')) {
        return 'Convocatoria permanente sin fecha límite definida.';
    } else if (convocatoria.toLowerCase().includes('anual')) {
        return 'Convocatoria anual. Consulte la web oficial para plazos específicos del año en curso.';
    } else if (convocatoria.toLowerCase().includes('cerrada')) {
        return 'Convocatoria cerrada. Pendiente de apertura de nuevo plazo.';
    }
    
    return '';
}

/**
 * Genera información sobre documentación necesaria según tipo de ayuda
 * @param {string} tipoAyuda - Tipo de ayuda (subvención, préstamo, etc.)
 * @param {string} descripcion - Texto de descripción
 * @returns {string} HTML con información sobre documentación
 */
function generarInfoDocumentacion(tipoAyuda, descripcion) {
    // Primero intentamos extraer menciones específicas a documentos en la descripción
    const documentosExtraidos = extraerDocumentosEspecificos(descripcion);
    
    if (documentosExtraidos && documentosExtraidos.length > 0) {
        return generarListaHTML(documentosExtraidos);
    }
    
    // Si no hay documentos específicos, generamos según el tipo de ayuda
    return generarDocumentacionTipica(tipoAyuda);
}

/**
 * Extrae menciones específicas a documentos requeridos en el texto de descripción
 * @param {string} descripcion - Texto de descripción
 * @returns {Array} Array de documentos extraídos o null si no se encontraron
 */
function extraerDocumentosEspecificos(descripcion) {
    if (!descripcion) return null;
    
    const textoLower = descripcion.toLowerCase();
    const frases = descripcion.split(/[.!?]\s+/);
    const documentos = [];
    
    // Palabras clave que indican documentación
    const keywordsDoc = ['presentar', 'adjuntar', 'aportar', 'documento', 'documentación', 'certificado', 'memoria'];
    
    // Buscar frases que contengan keywords de documentación
    frases.forEach(frase => {
        const fraseLower = frase.toLowerCase().trim();
        
        // Si la frase contiene alguna keyword
        if (keywordsDoc.some(keyword => fraseLower.includes(keyword))) {
            // Limpiamos la frase
            let docLimpio = frase.trim();
            if (!docLimpio.endsWith('.') && !docLimpio.endsWith('!') && !docLimpio.endsWith('?')) {
                docLimpio += '.';
            }
            
            documentos.push(docLimpio);
        }
    });
    
    return documentos.length > 0 ? documentos : null;
}

/**
 * Genera lista de documentación típica según el tipo de ayuda
 * @param {string} tipoAyuda - Tipo de ayuda (subvención, préstamo, etc.)
 * @returns {string} HTML con lista de documentación
 */
function generarDocumentacionTipica(tipoAyuda) {
    const documentosComunes = [
        'Formulario de solicitud debidamente cumplimentado',
        'CIF de la empresa y DNI del representante legal',
        'Escrituras o documento de constitución de la empresa',
        'Poder de representación del firmante de la solicitud',
        'Certificados de estar al corriente con Hacienda y Seguridad Social'
    ];
    
    let documentosEspecificos = [];
    
    // Documentos específicos según tipo de ayuda
    const tipoAyudaLower = (tipoAyuda || '').toLowerCase();
    
    if (tipoAyudaLower.includes('subvención') || tipoAyudaLower.includes('ayuda')) {
        documentosEspecificos = [
            'Memoria técnica del proyecto según modelo normalizado',
            'Presupuesto detallado de los gastos para los que se solicita la subvención',
            'Declaración responsable de ayudas solicitadas o recibidas',
            'Plan de empresa o viabilidad del proyecto (según aplique)'
        ];
    } else if (tipoAyudaLower.includes('préstamo') || tipoAyudaLower.includes('credito')) {
        documentosEspecificos = [
            'Estados financieros de los últimos 2-3 ejercicios',
            'Memoria económica y plan de negocio',
            'Detalle de endeudamiento actual y proyectado',
            'Garantías ofrecidas para la operación (si aplica)',
            'Proyecciones financieras para el periodo de devolución del préstamo'
        ];
    } else if (tipoAyudaLower.includes('garantía') || tipoAyudaLower.includes('aval')) {
        documentosEspecificos = [
            'Contrato o borrador del préstamo a garantizar',
            'Certificado de solvencia de la entidad garante',
            'Plan de tesorería a medio plazo',
            'Informe de necesidades de financiación'
        ];
    } else {
        documentosEspecificos = [
            'Memoria descriptiva del proyecto o actuación',
            'Calendario de ejecución y plan de trabajo',
            'Presupuesto o factura proforma de las inversiones/gastos',
            'Declaración de otras ayudas para el mismo proyecto'
        ];
    }
    
    // Combinar documentos comunes y específicos
    const documentosCombinados = [
        ...documentosComunes,
        ...documentosEspecificos
    ];
    
    return generarListaHTML(documentosCombinados);
}

