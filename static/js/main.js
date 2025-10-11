/**
 * Script principal para la Herramienta de Evaluación de Deducciones Fiscales I+D+i
 */

// Documento cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            html: true,
            template: '<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner bg-light text-dark border" style="max-width: 300px; text-align: left; padding: 10px;"></div></div>'
        });
    });
    
    // Marcar enlace activo en la navegación
    highlightActiveNavLink();
    
    // Validación de campos numéricos (solo permitir números y punto decimal)
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            // Eliminar caracteres no numéricos excepto el punto decimal
            this.value = this.value.replace(/[^0-9.]/g, '');
            
            // Asegurar que solo hay un punto decimal
            const parts = this.value.split('.');
            if (parts.length > 2) {
                this.value = parts[0] + '.' + parts.slice(1).join('');
            }
        });
    });
    
    // Inicializar campos con formato de moneda
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', formatCurrency);
        input.addEventListener('focus', function() {
            // Al obtener el foco, mostrar solo el número sin formato
            this.value = this.value.replace(/[^\d.]/g, '');
        });
    });
    
    // Mostrar/ocultar campos condicionales
    setupConditionalFields();
    
    // Validar formulario antes de enviar
    setupFormValidation();
});

/**
 * Formatea un campo como moneda
 */
function formatCurrency() {
    let value = this.value.trim();
    
    if (value) {
        // Convertir a número y formatear
        const numValue = parseFloat(value);
        if (!isNaN(numValue)) {
            // Formatear con 2 decimales y separador de miles
            this.value = new Intl.NumberFormat('es-ES', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(numValue);
        }
    }
}

/**
 * Configura campos condicionales (mostrar/ocultar según otras respuestas)
 */
function setupConditionalFields() {
    // Buscar todos los campos condicionales
    const conditionalFields = document.querySelectorAll('[data-conditional-field]');
    
    // Si no hay campos condicionales, salir
    if (conditionalFields.length === 0) return;
    
    // Para cada campo condicional, configurar su visibilidad
    conditionalFields.forEach(function(field) {
        const triggerFieldName = field.dataset.conditionalField;
        const expectedValue = field.dataset.conditionalValue;
        
        // Buscar los elementos de input que pueden disparar la condición
        const triggerElements = document.querySelectorAll(`input[name="${triggerFieldName}"], select[name="${triggerFieldName}"]`);
        
        // Función para actualizar visibilidad
        function updateVisibility() {
            let shouldShow = false;
            
            // Para radio buttons y checkboxes
            if (triggerElements[0] && triggerElements[0].type === 'radio') {
                const checkedInput = document.querySelector(`input[name="${triggerFieldName}"]:checked`);
                shouldShow = checkedInput && checkedInput.value === expectedValue;
            }
            // Para selects
            else if (triggerElements[0] && triggerElements[0].tagName === 'SELECT') {
                shouldShow = triggerElements[0].value === expectedValue;
            }
            // Para otros tipos de inputs
            else if (triggerElements[0]) {
                shouldShow = triggerElements[0].value === expectedValue;
            }
            
            // Actualizar visibilidad
            field.style.display = shouldShow ? 'block' : 'none';
            
            // Si el campo tiene inputs requeridos, actualizar el atributo 'required'
            const requiredInputs = field.querySelectorAll('[required]');
            requiredInputs.forEach(function(input) {
                if (shouldShow) {
                    input.setAttribute('required', 'required');
                } else {
                    input.removeAttribute('required');
                }
            });
        }
        
        // Configurar event listeners para los elementos disparadores
        triggerElements.forEach(function(element) {
            element.addEventListener('change', updateVisibility);
        });
        
        // Actualizar visibilidad inicialmente
        updateVisibility();
    });
    
    // Funcionalidad específica para personal y personal exclusivo
    const personnelInput = document.getElementById('personnel');
    const exclusivePersonnelInput = document.getElementById('exclusive_personnel');
    
    if (personnelInput && exclusivePersonnelInput) {
        // Verificar que el personal exclusivo no sea mayor que el total
        personnelInput.addEventListener('input', function() {
            validateExclusivePersonnel();
        });
        
        exclusivePersonnelInput.addEventListener('input', function() {
            validateExclusivePersonnel();
        });
        
        function validateExclusivePersonnel() {
            const personnelValue = parseFloat(personnelInput.value) || 0;
            const exclusiveValue = parseFloat(exclusivePersonnelInput.value) || 0;
            
            if (exclusiveValue > personnelValue) {
                exclusivePersonnelInput.setCustomValidity('El personal exclusivo no puede ser mayor que el total de personal');
                
                // Mostrar mensaje de error
                const errorContainer = document.getElementById('exclusive_personnel_error');
                if (errorContainer) {
                    errorContainer.textContent = 'El personal exclusivo no puede ser mayor que el total de personal';
                    errorContainer.classList.remove('d-none');
                }
            } else {
                exclusivePersonnelInput.setCustomValidity('');
                
                // Ocultar mensaje de error
                const errorContainer = document.getElementById('exclusive_personnel_error');
                if (errorContainer) {
                    errorContainer.classList.add('d-none');
                }
            }
        }
    }
}

/**
 * Configura la validación del formulario
 */
function setupFormValidation() {
    const form = document.getElementById('questionnaireForm');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            // Verificar campos requeridos
            const requiredFields = form.querySelectorAll('[required]:not([type="hidden"])');
            let isValid = true;
            
            requiredFields.forEach(function(field) {
                // Solo validar campos visibles
                if (field.offsetParent !== null) {  // Si el elemento es visible
                    if (!field.value.trim()) {
                        field.classList.add('is-invalid');
                        isValid = false;
                    } else {
                        field.classList.remove('is-invalid');
                    }
                }
            });
            
            // Verificar campos numéricos
            const numberFields = form.querySelectorAll('input[type="number"]');
            
            numberFields.forEach(function(field) {
                // Solo validar campos visibles con valores
                if (field.offsetParent !== null && field.value) {
                    if (isNaN(parseFloat(field.value))) {
                        field.classList.add('is-invalid');
                        isValid = false;
                    }
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                
                // Mostrar alerta
                const alertContainer = document.getElementById('validation-alert');
                if (alertContainer) {
                    alertContainer.classList.remove('d-none');
                    
                    // Hacer scroll hasta el mensaje de error
                    alertContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                } else {
                    alert('Por favor, corrija los errores en el formulario antes de continuar.');
                }
            }
        });
    }
}

/**
 * Configura modales para guardar y cargar evaluaciones
 */
function setupModals() {
    // Modal para guardar evaluación
    const saveModal = document.getElementById('saveModal');
    if (saveModal) {
        saveModal.addEventListener('shown.bs.modal', function() {
            // Enfocar el campo de nombre de archivo
            document.getElementById('filename').focus();
        });
    }
    
    // Modal de confirmación para reiniciar
    const resetModal = document.getElementById('resetModal');
    if (resetModal) {
        const resetButton = document.getElementById('confirmReset');
        if (resetButton) {
            resetButton.addEventListener('click', function() {
                window.location.href = resetButton.getAttribute('data-url');
            });
        }
    }
}

// Función para copiar recomendaciones al portapapeles
function copyRecommendations() {
    const recommendationsContainer = document.getElementById('recommendations-container');
    
    if (recommendationsContainer) {
        // Crear un elemento temporal
        const tempElement = document.createElement('textarea');
        tempElement.value = Array.from(recommendationsContainer.querySelectorAll('.list-group-item'))
            .map(item => item.textContent.trim())
            .join('\n\n');
            
        document.body.appendChild(tempElement);
        tempElement.select();
        document.execCommand('copy');
        document.body.removeChild(tempElement);
        
        // Mostrar confirmación
        alert('Recomendaciones copiadas al portapapeles');
    }
}

// Función para imprimir resultados
function printResults() {
    window.print();
}

/**
 * Resalta el enlace activo en la navegación según la URL actual
 */
function highlightActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        // Remover clase activa de todos los enlaces
        link.classList.remove('active');
        
        // Obtener la ruta del enlace
        const linkPath = link.getAttribute('href');
        
        // Comprobar si la URL actual coincide con el enlace
        if (linkPath === currentPath) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        } 
        // Manejar casos especiales
        else if (currentPath.startsWith('/questionnaire') && link.getAttribute('href').includes('/welcome')) {
            // Marcar "Simula tus deducciones" como activo si estamos en el cuestionario
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
        else if (currentPath === '/results' && link.getAttribute('href').includes('/welcome')) {
            // Marcar "Simula tus deducciones" como activo si estamos en resultados
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
    });
}
