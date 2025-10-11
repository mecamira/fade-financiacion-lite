/**
 * Funciones JavaScript para la herramienta de estructura de proyectos
 */

// Variables globales
let checklistState = {};
let totalItems = 0;
let checkedItems = 0;

/**
 * Inicializa la funcionalidad de la lista de verificación
 */
function initChecklist() {
    // Cargar estado guardado
    loadChecklistState();
    
    // Manejar clicks en checkboxes
    document.querySelectorAll('.checklist-check').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateProgress();
            saveChecklistState();
        });
    });
    
    // Manejar el botón de reinicio
    const resetButton = document.getElementById('reset-checklist');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            if (confirm('¿Estás seguro de que quieres reiniciar la verificación? Se perderá todo el progreso actual.')) {
                resetChecklist();
            }
        });
    }
    
    // Inicializar progreso
    updateProgress();
}

/**
 * Actualiza la barra de progreso y el resumen de la lista de verificación
 */
function updateProgress() {
    totalItems = document.querySelectorAll('.checklist-check').length;
    checkedItems = document.querySelectorAll('.checklist-check:checked').length;
    const percentage = Math.round((checkedItems / totalItems) * 100);
    
    // Actualizar barra de progreso general
    const progressBar = document.getElementById('checklist-progress');
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.textContent = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
    }
    
    // Actualizar progreso por secciones
    const sections = {};
    document.querySelectorAll('.checklist-item').forEach(item => {
        const sectionId = item.dataset.section;
        if (!sections[sectionId]) {
            sections[sectionId] = { total: 0, checked: 0 };
        }
        sections[sectionId].total++;
        
        const checkbox = item.querySelector('.checklist-check');
        if (checkbox.checked) {
            sections[sectionId].checked++;
        }
    });
    
    // Actualizar badges de secciones
    document.querySelectorAll('.section-progress').forEach(badge => {
        const sectionId = badge.dataset.section;
        if (sections[sectionId]) {
            badge.textContent = sections[sectionId].checked + '/' + sections[sectionId].total;
            
            // Cambiar color si está completa
            if (sections[sectionId].checked === sections[sectionId].total) {
                badge.classList.remove('bg-secondary');
                badge.classList.add('bg-success');
            } else {
                badge.classList.remove('bg-success');
                badge.classList.add('bg-secondary');
            }
        }
    });
    
    // Actualizar resumen
    updateSummary(totalItems, checkedItems, percentage, sections);
}

/**
 * Actualiza el resumen de la verificación
 */
function updateSummary(totalItems, checkedItems, percentage, sections) {
    const completedItemsCount = document.getElementById('completed-items-count');
    const totalItemsCount = document.getElementById('total-items-count');
    const completedPercentage = document.getElementById('completed-percentage');
    
    if (completedItemsCount) completedItemsCount.textContent = checkedItems;
    if (totalItemsCount) totalItemsCount.textContent = totalItems;
    if (completedPercentage) completedPercentage.textContent = percentage + '%';
    
    const summaryElement = document.getElementById('checklist-summary');
    const completeElement = document.getElementById('checklist-complete');
    const incompleteElement = document.getElementById('checklist-incomplete');
    
    if (checkedItems === totalItems) {
        // Todo completado
        if (summaryElement) summaryElement.classList.add('d-none');
        if (completeElement) completeElement.classList.remove('d-none');
        if (incompleteElement) incompleteElement.classList.add('d-none');
    } else if (checkedItems > 0) {
        // Progreso parcial
        if (summaryElement) summaryElement.classList.add('d-none');
        if (completeElement) completeElement.classList.add('d-none');
        if (incompleteElement) incompleteElement.classList.remove('d-none');
        
        // Mostrar secciones a mejorar
        const sectionsToImprove = document.getElementById('sections-to-improve');
        if (sectionsToImprove) {
            sectionsToImprove.innerHTML = '';
            
            for (const sectionId in sections) {
                if (sections[sectionId].checked < sections[sectionId].total) {
                    const sectionTitle = document.querySelector(`#headingCheck${sectionId} .accordion-button strong`).textContent;
                    const li = document.createElement('li');
                    li.innerHTML = `<strong>${sectionTitle}</strong>: ${sections[sectionId].checked}/${sections[sectionId].total} completados`;
                    sectionsToImprove.appendChild(li);
                }
            }
        }
    } else {
        // Nada completado
        if (summaryElement) summaryElement.classList.remove('d-none');
        if (completeElement) completeElement.classList.add('d-none');
        if (incompleteElement) incompleteElement.classList.add('d-none');
    }
}

/**
 * Guarda el estado actual de la lista de verificación en localStorage
 */
function saveChecklistState() {
    const state = {};
    document.querySelectorAll('.checklist-check').forEach(checkbox => {
        const item = checkbox.closest('.checklist-item');
        const sectionId = item.dataset.section;
        const itemId = item.dataset.item;
        state[`${sectionId}_${itemId}`] = checkbox.checked;
    });
    
    localStorage.setItem('project_checklist_state', JSON.stringify(state));
}

/**
 * Carga el estado guardado de la lista de verificación desde localStorage
 */
function loadChecklistState() {
    const savedState = localStorage.getItem('project_checklist_state');
    if (savedState) {
        const state = JSON.parse(savedState);
        
        document.querySelectorAll('.checklist-check').forEach(checkbox => {
            const item = checkbox.closest('.checklist-item');
            const sectionId = item.dataset.section;
            const itemId = item.dataset.item;
            const key = `${sectionId}_${itemId}`;
            
            if (state[key] !== undefined) {
                checkbox.checked = state[key];
            }
        });
    }
}

/**
 * Reinicia la lista de verificación
 */
function resetChecklist() {
    document.querySelectorAll('.checklist-check').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    localStorage.removeItem('project_checklist_state');
    updateProgress();
}

/**
 * Inicializa todos los componentes cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar la lista de verificación si estamos en esa página
    if (document.querySelector('.checklist-check')) {
        initChecklist();
    }
    
    // Manejar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});