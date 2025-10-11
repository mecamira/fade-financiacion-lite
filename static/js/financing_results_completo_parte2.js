    // Ajustar ejemplos según el tipo de programa
    if (nombreLower.includes('cdti') || nombreLower.includes('i+d') || nombreLower.includes('idi')) {
        return `
        <p>Este programa suele financiar proyectos como:</p>
        <ul>
            <li>Desarrollo de nuevos productos o servicios con base tecnológica</li>
            <li>Mejora sustancial de procesos productivos mediante la aplicación de tecnologías emergentes</li>
            <li>Proyectos de investigación industrial o desarrollo experimental en colaboración con centros tecnológicos</li>
            <li>Validación de prototipos y escalado de tecnologías innovadoras</li>
        </ul>
        `;
    } 
    else if (nombreLower.includes('innovación') || nombreLower.includes('innova')) {
        return `
        <p>Este programa suele financiar proyectos como:</p>
        <ul>
            <li>Incorporación de tecnologías innovadoras a procesos o productos existentes</li>
            <li>Desarrollo de nuevos modelos de negocio basados en innovación</li>
            <li>Mejoras organizativas y de proceso con un componente innovador</li>
            <li>Innovación en marketing, diseño o servicios</li>
        </ul>
        `;
    }
    else if (nombreLower.includes('digital') || nombreLower.includes('kit')) {
        return `
        <p>Este programa suele financiar proyectos como:</p>
        <ul>
            <li>Implementación de soluciones de comercio electrónico</li>
            <li>Desarrollo o mejora de sitio web y presencia online</li>
            <li>Implantación de sistemas de gestión empresarial</li>
            <li>Adopción de herramientas de ciberseguridad</li>
            <li>Digitalización de procesos internos de negocio</li>
        </ul>
        `;
    }
    else if (nombreLower.includes('emprendimiento') || nombreLower.includes('emprend') || nombreLower.includes('startup')) {
        return `
        <p>Este programa suele financiar proyectos como:</p>
        <ul>
            <li>Creación y puesta en marcha de nuevas empresas innovadoras</li>
            <li>Validación de modelos de negocio escalables</li>
            <li>Desarrollo de prototipos y productos mínimos viables (MVP)</li>
            <li>Primeras fases de comercialización y acceso al mercado</li>
        </ul>
        `;
    }
    else if (nombreLower.includes('sostenib') || nombreLower.includes('verde') || nombreLower.includes('circular') || nombreLower.includes('energ')) {
        return `
        <p>Este programa suele financiar proyectos como:</p>
        <ul>
            <li>Mejora de la eficiencia energética en procesos productivos</li>
            <li>Implementación de sistemas de energía renovable</li>
            <li>Rediseño de productos para reducir su impacto ambiental</li>
            <li>Desarrollo de modelos de negocio de economía circular</li>
            <li>Incorporación de tecnologías limpias o bajas en carbono</li>
        </ul>
        `;
    }
    else if (tipoLower.includes('capital') || tipoLower.includes('participativo')) {
        return `
        <p>Este programa suele financiar proyectos como:</p>
        <ul>
            <li>Expansión y crecimiento de empresas con modelo de negocio probado</li>
            <li>Internacionalización de empresas con potencial de escalado</li>
            <li>Desarrollo de nuevas líneas de producto/servicio con alto potencial</li>
            <li>Adquisición de activos estratégicos para el crecimiento</li>
        </ul>
        `;
    }
    else {
        // Caso genérico para otros tipos de programas
        return `
        <p>Este programa puede financiar diversos tipos de proyectos como:</p>
        <ul>
            <li>Mejora de procesos productivos o servicios existentes</li>
            <li>Desarrollo e introducción de nuevos productos o servicios</li>
            <li>Adopción de tecnologías que mejoren la competitividad</li>
            <li>Inversión en equipamiento y capacitación para mejora empresarial</li>
        </ul>
        `;
    }
}

/**
 * Genera consejos para la presentación de solicitudes
 */
function generarConsejosPresentacion(programName, tipoAyuda) {
    const nombreLower = programName.toLowerCase();
    
    // Consejos genéricos aplicables a todos los programas
    let consejosHTML = `
    <ol>
        <li><strong>Revise detenidamente los requisitos y criterios de evaluación</strong> antes de presentar su solicitud.</li>
        <li><strong>Presente una memoria técnica clara y bien estructurada</strong>, destacando los aspectos innovadores y los resultados esperados.</li>
        <li><strong>Asegure la coherencia</strong> entre el objetivo del proyecto, las actividades propuestas y el presupuesto solicitado.</li>
        <li><strong>Prepare toda la documentación administrativa</strong> con suficiente antelación para evitar problemas de última hora.</li>
    `;
    
    // Consejos específicos según el programa
    if (nombreLower.includes('cdti') || nombreLower.includes('i+d') || nombreLower.includes('idi')) {
        consejosHTML += `
        <li><strong>Destaque claramente el nivel de novedad tecnológica</strong> de su proyecto frente al estado del arte actual.</li>
        <li><strong>Detalle los retos tecnológicos</strong> a superar y su estrategia para abordarlos.</li>
        <li><strong>Incluya un plan de explotación</strong> de resultados con estimaciones realistas de retorno de la inversión.</li>
        `;
    } 
    else if (nombreLower.includes('digital')) {
        consejosHTML += `
        <li><strong>Elabore un diagnóstico digital</strong> previo que muestre claramente las necesidades de su empresa.</li>
        <li><strong>Seleccione cuidadosamente a su agente digitalizador</strong>, verificando su experiencia y referencias.</li>
        <li><strong>Documente el antes y después</strong> de la implantación para demostrar la mejora obtenida.</li>
        `;
    }
    else if (nombreLower.includes('emprendimiento') || nombreLower.includes('startup')) {
        consejosHTML += `
        <li><strong>Demuestre la escalabilidad</strong> de su modelo de negocio con datos y proyecciones realistas.</li>
        <li><strong>Presente un equipo con capacidades complementarias</strong> y experiencia relevante.</li>
        <li><strong>Incluya evidencias de tracción</strong> (clientes, ventas preliminares, etc.) si ya cuenta con ellas.</li>
        `;
    }
    else if (nombreLower.includes('local') || nombreLower.includes('ayuntamiento') || nombreLower.includes('municipal')) {
        consejosHTML += `
        <li><strong>Destaque el impacto local</strong> del proyecto en términos de empleo, economía o sostenibilidad.</li>
        <li><strong>Verifique los requisitos específicos municipales</strong> que puedan variar respecto a otras convocatorias.</li>
        <li><strong>Consulte previamente</strong> con los técnicos municipales para resolver dudas específicas.</li>
        `;
    }
    
    // Cierre de consejos
    consejosHTML += `
        <li><strong>No espere al último momento</strong> para presentar su solicitud, previendo posibles incidencias técnicas.</li>
        <li><strong>Si es posible, solicite una revisión</strong> por parte de un consultor especializado en el programa.</li>
    </ol>
    <p class="alert alert-info mt-3 mb-0">
        <i class="fas fa-lightbulb me-2"></i>
        Recuerde que nuestros asesores especializados pueden ayudarle a preparar su solicitud y maximizar sus posibilidades de éxito.
    </p>
    `;
    
    return consejosHTML;
}

/**
 * Configura la funcionalidad de impresión
 */
function setupPrintFunctionality() {
    const printButtons = document.querySelectorAll('button[onclick="window.print()"]');
    
    printButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Añadir clase para optimizar impresión
            document.body.classList.add('printing');
            
            // Imprimir
            window.print();
            
            // Quitar clase después de imprimir
            setTimeout(() => {
                document.body.classList.remove('printing');
            }, 1000);
        });
    });
}

/**
 * Muestra una notificación tipo toast
 */
function showNotification(message) {
    // Buscar si ya existe una notificación
    let notification = document.querySelector('.toast-notification');
    
    if (!notification) {
        // Crear elemento de notificación
        notification = document.createElement('div');
        notification.className = 'toast-notification';
        notification.innerHTML = `
            <div class="toast-icon">
                <i class="fas fa-check-circle"></i>
            </div>
            <div class="toast-message"></div>
        `;
        document.body.appendChild(notification);
    }
    
    // Actualizar mensaje
    notification.querySelector('.toast-message').textContent = message;
    
    // Mostrar con animación
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Ocultar después de un tiempo
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

/**
 * Formatea la respuesta original del asesor (si existe)
 * Utilizamos un enfoque simplificado para formatear el texto
 */
function formatOriginalResponse() {
    const originalResponseDiv = document.getElementById('formatted-response');
    
    if (!originalResponseDiv) return;
    
    const responseText = originalResponseDiv.innerHTML;
    
    // Formatear títulos
    let formattedText = responseText
        .replace(/###\s+([^\n]+)/g, '<h4 class="mb-3 mt-4 border-bottom pb-2">$1</h4>')
        .replace(/##\s+([^\n]+)/g, '<h3 class="mb-3 mt-4">$1</h3>')
        .replace(/#\s+([^\n]+)/g, '<h2 class="mb-3 mt-4">$1</h2>');
    
    // Formatear listas
    formattedText = formattedText
        .replace(/^\s*-\s+(.+)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>\n)+/g, '<ul class="mb-3">$&</ul>');
    
    // Formatear párrafos
    formattedText = formattedText
        .replace(/^(?!<[hu]|<li|<ul)(.+)$/gm, '<p>$1</p>');
    
    // Actualizar contenido
    originalResponseDiv.innerHTML = formattedText;
}