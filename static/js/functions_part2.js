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
