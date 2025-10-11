// JavaScript para la página de enmarcado S3

document.addEventListener('DOMContentLoaded', function() {
    // Añadir clases a elementos para mejorar la apariencia
    const form = document.querySelector('form[action="/s3-framework"]');
    if (form) {
        form.classList.add('s3-framework-form');
        
        // Agregar efecto de carga al enviar el formulario
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                // Cambiar el texto del botón y deshabilitarlo
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Analizando proyecto...';
                submitBtn.disabled = true;
                submitBtn.classList.add('loading');
                
                // Volver al estado original después de un tiempo si algo falla
                setTimeout(function() {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                        submitBtn.classList.remove('loading');
                    }
                }, 15000); // 15 segundos como máximo
            }
        });
    }
    
    // Configurar el modal de resultados si existe
    const resultModal = document.getElementById('resultModal');
    if (resultModal) {
        // Crear una instancia de Bootstrap Modal
        const bsModal = new bootstrap.Modal(resultModal, {
            backdrop: 'static',  // Evita que se cierre al hacer clic fuera
            keyboard: false       // Evita que se cierre con la tecla Escape
        });
        
        // Mostrar el modal automáticamente
        bsModal.show();
        
        // Añadir efectos a los elementos internos del modal
        const alertSuccess = resultModal.querySelector('.alert-success');
        if (alertSuccess) {
            // Añadir un pequeño retraso para que la animación sea visible después de que el modal aparezca
            setTimeout(() => {
                alertSuccess.style.transition = 'all 0.3s ease';
                alertSuccess.style.transform = 'translateY(0)';
                alertSuccess.style.opacity = '1';
            }, 300);
        }
        
        // Manejar el cierre del modal
        resultModal.addEventListener('hidden.bs.modal', function() {
            // Opcional: redireccionar o hacer otras acciones al cerrar
            // window.location.href = '/s3-framework';
        });
    }
    
    // Añadir tooltips a los elementos (utilizando Bootstrap si está disponible)
    try {
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    } catch (e) {
        console.log('Bootstrap tooltips no disponibles');
    }
    
    // Mejorar el aspecto de los resultados
    const resultSection = document.querySelector('#result');
    if (resultSection) {
        resultSection.classList.add('s3-framework-result');
        
        const resultTitle = resultSection.querySelector('h3');
        if (resultTitle) {
            resultTitle.classList.add('s3-result-title');
        }
    }
    
    // Añadir funcionalidad para copiar información al portapapeles
    const copyButtons = document.querySelectorAll('.copy-to-clipboard');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy-text');
            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    // Cambiar el texto del botón temporalmente
                    const originalHTML = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check me-1"></i>Copiado';
                    setTimeout(() => {
                        this.innerHTML = originalHTML;
                    }, 2000);
                }).catch(err => {
                    console.error('Error al copiar: ', err);
                });
            }
        });
    });
});
