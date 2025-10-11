// JavaScript mejorado para la guía de herramientas

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initWizard();
    initImpactCalculator();
    initDemoModals();
    initToolCards();
    initAnimations();
});

// Wizard interactivo
function initWizard() {
    let currentStep = 1;
    const totalSteps = 3;
    let wizardData = {};
    
    const steps = document.querySelectorAll('.wizard-step');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const progressBar = document.querySelector('.progress-bar::before') || document.querySelector('.progress-bar');
    const progressText = document.querySelector('.progress-text');
    
    // Manejar selección de opciones
    document.querySelectorAll('.wizard-option').forEach(option => {
        option.addEventListener('click', function() {
            const stepContainer = this.closest('.wizard-step');
            const stepId = stepContainer.id;
            
            // Deseleccionar otras opciones en el mismo paso
            stepContainer.querySelectorAll('.wizard-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Seleccionar esta opción
            this.classList.add('selected');
            
            // Guardar selección
            wizardData[stepId] = this.dataset.value;
            
            // Habilitar botón siguiente
            nextBtn.disabled = false;
            nextBtn.classList.remove('disabled');
        });
    });
    
    // Botón siguiente
    nextBtn.addEventListener('click', function() {
        if (currentStep < totalSteps) {
            currentStep++;
            updateWizardStep();
        } else {
            // Mostrar resultados
            showWizardResults();
        }
    });
    
    // Botón anterior
    prevBtn.addEventListener('click', function() {
        if (currentStep > 1) {
            currentStep--;
            updateWizardStep();
        }
    });
    
    function updateWizardStep() {
        // Ocultar todos los pasos
        steps.forEach(step => step.classList.remove('active'));
        
        // Mostrar paso actual
        const currentStepElement = document.getElementById(`step-${currentStep}`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
        }
        
        // Actualizar navegación
        prevBtn.style.display = currentStep > 1 ? 'block' : 'none';
        
        if (currentStep === totalSteps) {
            nextBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Ver recomendaciones';
        } else {
            nextBtn.innerHTML = 'Siguiente<i class="fas fa-arrow-right ms-2"></i>';
        }
        
        // Actualizar barra de progreso
        const progress = (currentStep / totalSteps) * 100;
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        if (progressText) {
            progressText.textContent = `Paso ${currentStep} de ${totalSteps}`;
        }
        
        // Deshabilitar botón siguiente hasta nueva selección
        const currentStepElement = document.getElementById(`step-${currentStep}`);
        if (currentStepElement && !currentStepElement.querySelector('.wizard-option.selected')) {
            nextBtn.disabled = true;
            nextBtn.classList.add('disabled');
        }
    }
    
    function showWizardResults() {
        // Ocultar todos los pasos
        steps.forEach(step => step.classList.remove('active'));
        
        // Mostrar resultados
        const resultsStep = document.getElementById('results');
        resultsStep.classList.add('active');
        
        // Generar recomendaciones
        const recommendations = generateRecommendations(wizardData);
        const recommendationContent = document.getElementById('recommendation-content');
        recommendationContent.innerHTML = recommendations;
        
        // Ocultar navegación
        document.querySelector('.wizard-navigation').style.display = 'none';
        
        // Añadir animación
        resultsStep.style.animation = 'fadeInUp 0.8s ease-out';
    }
    
    function generateRecommendations(data) {
        const { 'step-1': profile, 'step-2': objective, 'step-3': phase } = data;
        
        let recommendations = '';
        
        // Lógica de recomendaciones basada en las respuestas
        if (objective === 'deduccion') {
            recommendations += createRecommendationCard(
                'Simulador de Deducciones Fiscales',
                'fas fa-calculator',
                'Perfecto para tu objetivo. Esta herramienta te ayudará a evaluar si tu proyecto califica como I+D o IT y calcular el ahorro fiscal potencial.',
                '/welcome',
                'Iniciar simulación',
                'primary'
            );
        }
        
        if (objective === 'financiacion' || phase === 'idea') {
            recommendations += createRecommendationCard(
                'Asesor de Financiación',
                'fas fa-coins',
                'Ideal para encontrar las mejores oportunidades de financiación. Te ayudará a identificar programas compatibles con tu perfil.',
                '/financing-questionnaire',
                'Buscar financiación',
                'success'
            );
        }
        
        if (objective === 'estructura' || phase === 'idea' || phase === 'desarrollo') {
            recommendations += createRecommendationCard(
                'Estructurador de Proyectos',
                'fas fa-project-diagram',
                'Esencial para organizar y documentar correctamente tu proyecto. Te guiará paso a paso en la estructuración.',
                '/estructura',
                'Explorar guías',
                'info'
            );
        }
        
        if (profile === 'pyme' || profile === 'grande') {
            recommendations += createRecommendationCard(
                'Alineación S3 Asturias',
                'fas fa-map-marked-alt',
                'Recomendado para empresas establecidas. Te ayudará a alinear tu proyecto con la estrategia regional.',
                '/s3-framework',
                'Enmarcar proyecto',
                'warning'
            );
        }
        
        // Recomendación de flujo de trabajo
        recommendations += `
            <div class="alert alert-light border mt-3">
                <h5><i class="fas fa-route me-2"></i>Flujo recomendado para ti</h5>
                <p>Basado en tu perfil, te sugerimos seguir este orden:</p>
                <ol class="mb-0">
                    ${getWorkflowSteps(data)}
                </ol>
            </div>
        `;
        
        return recommendations;
    }
    
    function createRecommendationCard(title, icon, description, link, buttonText, buttonType) {
        return `
            <div class="recommendation-card">
                <h4><i class="${icon} me-2"></i>${title}</h4>
                <p>${description}</p>
                <div class="recommendation-actions">
                    <a href="${link}" class="btn btn-${buttonType} btn-sm">
                        <i class="fas fa-arrow-right me-1"></i>${buttonText}
                    </a>
                </div>
            </div>
        `;
    }
    
    function getWorkflowSteps(data) {
        const { 'step-1': profile, 'step-2': objective, 'step-3': phase } = data;
        
        let steps = [];
        
        if (phase === 'idea') {
            steps.push('Estructurar el proyecto con nuestras guías');
        }
        
        if (objective === 'estrategia' || profile === 'pyme') {
            steps.push('Enmarcar en la S3 de Asturias');
        }
        
        if (objective === 'deduccion' || phase === 'desarrollo' || phase === 'finalizado') {
            steps.push('Evaluar deducciones fiscales con el simulador');
        }
        
        if (objective === 'financiacion' || phase === 'idea') {
            steps.push('Buscar financiación complementaria');
        }
        
        steps.push('Contactar con FADE para asesoramiento especializado');
        
        return steps.map(step => `<li>${step}</li>`).join('');
    }
}

// Calculadora de impacto
function initImpactCalculator() {
    const calculateBtn = document.getElementById('calculate-impact');
    const budgetInput = document.getElementById('project-budget');
    const typeSelect = document.getElementById('project-type');
    const sizeSelect = document.getElementById('company-size');
    const resultsDiv = document.getElementById('impact-results');
    const placeholderDiv = document.getElementById('impact-placeholder');
    
    if (!calculateBtn) return;
    
    calculateBtn.addEventListener('click', function() {
        const budget = parseFloat(budgetInput.value) || 0;
        const type = typeSelect.value;
        const size = sizeSelect.value;
        
        if (budget === 0 || !type || !size) {
            alert('Por favor, completa todos los campos para calcular el impacto.');
            return;
        }
        
        const impact = calculateImpact(budget, type, size);
        showImpactResults(impact);
    });
    
    function calculateImpact(budget, type, size) {
        let taxSavings = 0;
        let financingPotential = 0;
        
        // Calcular ahorro fiscal según tipo de proyecto
        switch (type) {
            case 'id':
                taxSavings = budget * 0.25; // 25% base I+D
                // Bonus por personal exclusivo (estimado 30% del presupuesto)
                taxSavings += (budget * 0.3) * 0.17; // 17% adicional
                break;
            case 'it':
                taxSavings = budget * 0.12; // 12% IT
                break;
            case 'mixed':
                taxSavings = (budget * 0.6 * 0.25) + (budget * 0.4 * 0.12); // 60% I+D, 40% IT
                break;
        }
        
        // Calcular potencial de financiación según tamaño de empresa
        switch (size) {
            case 'micro':
                financingPotential = budget * 0.7; // 70% para microempresas
                break;
            case 'small':
                financingPotential = budget * 0.6; // 60% para pequeñas
                break;
            case 'medium':
                financingPotential = budget * 0.5; // 50% para medianas
                break;
            case 'large':
                financingPotential = budget * 0.3; // 30% para grandes
                break;
        }
        
        return {
            taxSavings: Math.round(taxSavings),
            financingPotential: Math.round(financingPotential),
            totalBenefit: Math.round(taxSavings + financingPotential)
        };
    }
    
    function showImpactResults(impact) {
        // Actualizar valores
        document.getElementById('tax-savings').textContent = formatCurrency(impact.taxSavings);
        document.getElementById('financing-potential').textContent = formatCurrency(impact.financingPotential);
        document.getElementById('total-benefit').textContent = formatCurrency(impact.totalBenefit);
        
        // Mostrar resultados con animación
        placeholderDiv.style.display = 'none';
        resultsDiv.style.display = 'block';
        resultsDiv.style.animation = 'fadeInUp 0.6s ease-out';
        
        // Animar los números
        animateNumbers();
    }
    
    function animateNumbers() {
        const numberElements = document.querySelectorAll('.result-value');
        numberElements.forEach(el => {
            const finalValue = el.textContent;
            const numericValue = parseFloat(finalValue.replace(/[^\d.-]/g, ''));
            
            if (numericValue > 0) {
                let currentValue = 0;
                const increment = numericValue / 50;
                const timer = setInterval(() => {
                    currentValue += increment;
                    if (currentValue >= numericValue) {
                        currentValue = numericValue;
                        clearInterval(timer);
                    }
                    
                    if (finalValue.includes('€')) {
                        el.textContent = formatCurrency(Math.round(currentValue));
                    } else {
                        el.textContent = Math.round(currentValue);
                    }
                }, 20);
            }
        });
    }
}

// Demos de herramientas
function initDemoModals() {
    const demoButtons = document.querySelectorAll('.btn-demo');
    const demoModal = document.getElementById('demoModal');
    const demoModalTitle = document.getElementById('demoModalTitle');
    const demoModalBody = document.getElementById('demoModalBody');
    const demoTryButton = document.getElementById('demoTryButton');
    
    if (!demoModal) return;
    
    demoButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tool = this.dataset.tool;
            showDemo(tool);
        });
    });
    
    function showDemo(tool) {
        const demoData = getDemoData(tool);
        
        demoModalTitle.textContent = `Demo: ${demoData.title}`;
        demoModalBody.innerHTML = demoData.content;
        demoTryButton.href = demoData.link;
        demoTryButton.innerHTML = `<i class="fas fa-external-link-alt me-2"></i>${demoData.buttonText}`;
        
        const modal = new bootstrap.Modal(demoModal);
        modal.show();
    }
    
    function getDemoData(tool) {
        const demos = {
            simulator: {
                title: 'Simulador de Deducciones Fiscales',
                content: `
                    <div class="demo-content">
                        <div class="demo-screenshot">
                            <img src="/static/images/demo-simulator.png" class="img-fluid rounded" alt="Demo Simulador" 
                                 onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjhmOWZhIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzZjNzU3ZCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRlbW8gU2ltdWxhZG9yPC90ZXh0Pjwvc3ZnPg==';">
                        </div>
                        <div class="demo-description">
                            <h5>¿Cómo funciona?</h5>
                            <ul>
                                <li><strong>Paso 1:</strong> Responde preguntas sobre tu proyecto y empresa</li>
                                <li><strong>Paso 2:</strong> Indica los gastos de tu proyecto de innovación</li>
                                <li><strong>Paso 3:</strong> Obtén tu calificación (I+D, IT o mixto)</li>
                                <li><strong>Paso 4:</strong> Recibe el cálculo detallado de deducciones</li>
                                <li><strong>Paso 5:</strong> Genera un informe PDF con recomendaciones</li>
                            </ul>
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                <strong>Tiempo estimado:</strong> 10-15 minutos para una evaluación completa
                            </div>
                        </div>
                    </div>
                `,
                link: '/welcome',
                buttonText: 'Probar simulador'
            },
            financing: {
                title: 'Asesor de Financiación',
                content: `
                    <div class="demo-content">
                        <div class="demo-screenshot">
                            <img src="/static/images/demo-financing.png" class="img-fluid rounded" alt="Demo Financiación"
                                 onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmN2ZmIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzAwNjZjYyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRlbW8gRmluYW5jaWFjacOzbjwvdGV4dD48L3N2Zz4=';">
                        </div>
                        <div class="demo-description">
                            <h5>Funcionalidades principales:</h5>
                            <ul>
                                <li><strong>Análisis inteligente:</strong> IA que analiza tu perfil y proyecto</li>
                                <li><strong>Base de datos:</strong> Más de ${window.stats?.programas_financiacion || 150} programas actualizados</li>
                                <li><strong>Recomendaciones:</strong> Programas ordenados por compatibilidad</li>
                                <li><strong>Consejos personalizados:</strong> Estrategias para maximizar probabilidades</li>
                                <li><strong>Análisis de compatibilidad:</strong> Evalúa PDFs de convocatorias</li>
                            </ul>
                            <div class="alert alert-success">
                                <i class="fas fa-chart-line me-2"></i>
                                <strong>Precisión:</strong> 95% de acierto en recomendaciones
                            </div>
                        </div>
                    </div>
                `,
                link: '/financing-questionnaire',
                buttonText: 'Probar asesor'
            },
            structure: {
                title: 'Estructurador de Proyectos',
                content: `
                    <div class="demo-content">
                        <div class="demo-screenshot">
                            <img src="/static/images/demo-structure.png" class="img-fluid rounded" alt="Demo Estructura"
                                 onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZWRmNGZmIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzE3YTJiOCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRlbW8gRXN0cnVjdHVyYTwvdGV4dD48L3N2Zz4=';">
                        </div>
                        <div class="demo-description">
                            <h5>Herramientas incluidas:</h5>
                            <ul>
                                <li><strong>Guía de secciones:</strong> 12 secciones clave explicadas</li>
                                <li><strong>Metodologías:</strong> Enfoques científicos y tecnológicos</li>
                                <li><strong>Checklist interactivo:</strong> +50 puntos de verificación</li>
                                <li><strong>Consejos de redacción:</strong> Cómo documentar efectivamente</li>
                                <li><strong>Planificación presupuestaria:</strong> Categorías de gastos elegibles</li>
                            </ul>
                            <div class="alert alert-warning">
                                <i class="fas fa-lightbulb me-2"></i>
                                <strong>Esencial:</strong> Una buena estructura multiplica las posibilidades de éxito
                            </div>
                        </div>
                    </div>
                `,
                link: '/estructura',
                buttonText: 'Explorar herramientas'
            },
            s3: {
                title: 'Alineación S3 Asturias',
                content: `
                    <div class="demo-content">
                        <div class="demo-screenshot">
                            <img src="/static/images/demo-s3.png" class="img-fluid rounded" alt="Demo S3"
                                 onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZmZmM2NkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iI2ZmYzEwNyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRlbW8gUzMgQXN0dXJpYXM8L3RleHQ+PC9zdmc+';">
                        </div>
                        <div class="demo-description">
                            <h5>Características únicas:</h5>
                            <ul>
                                <li><strong>Análisis con IA:</strong> Gemini AI analiza tu descripción</li>
                                <li><strong>8 ámbitos S3:</strong> Cobertura completa de la estrategia</li>
                                <li><strong>Alineación automática:</strong> Identifica prioridades regionales</li>
                                <li><strong>Informes especializados:</strong> Documentos para convocatorias</li>
                                <li><strong>Ventaja competitiva:</strong> Diferenciación en solicitudes</li>
                            </ul>
                            <div class="alert alert-info">
                                <i class="fas fa-map-marked-alt me-2"></i>
                                <strong>Regional:</strong> Específico para el ecosistema asturiano
                            </div>
                        </div>
                    </div>
                `,
                link: '/s3-framework',
                buttonText: 'Enmarcar proyecto'
            }
        };
        
        return demos[tool] || {
            title: 'Demo no disponible',
            content: '<p>Demo temporalmente no disponible.</p>',
            link: '#',
            buttonText: 'Volver'
        };
    }
}

// Animaciones para las cards de herramientas
function initToolCards() {
    const toolCards = document.querySelectorAll('.tool-card');
    
    // Intersection Observer para animaciones al scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                entry.target.style.opacity = '1';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    toolCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.animationDelay = `${index * 0.1}s`;
        observer.observe(card);
    });
    
    // Efectos hover avanzados
    toolCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Animaciones generales
function initAnimations() {
    // Parallax effect para el hero
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('.hero-section');
        if (parallax) {
            const speed = scrolled * 0.5;
            parallax.style.transform = `translateY(${speed}px)`;
        }
    });
    
    // Contador animado para estadísticas del hero
    const statsNumbers = document.querySelectorAll('.stat-number');
    let hasAnimated = false;
    
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !hasAnimated) {
                animateStatsNumbers();
                hasAnimated = true;
            }
        });
    });
    
    if (statsNumbers.length > 0) {
        statsObserver.observe(statsNumbers[0].closest('.hero-stats'));
    }
    
    function animateStatsNumbers() {
        statsNumbers.forEach(stat => {
            const finalValue = stat.textContent;
            const numericValue = parseFloat(finalValue.replace(/[^\d.-]/g, ''));
            
            if (numericValue > 0) {
                let currentValue = 0;
                const increment = numericValue / 30;
                const timer = setInterval(() => {
                    currentValue += increment;
                    if (currentValue >= numericValue) {
                        currentValue = numericValue;
                        clearInterval(timer);
                        stat.textContent = finalValue; // Restaurar formato original
                    } else {
                        const suffix = finalValue.includes('%') ? '%' : 
                                     finalValue.includes('+') ? '+' : '';
                        stat.textContent = Math.round(currentValue) + suffix;
                    }
                }, 50);
            }
        });
    }
}

// Funciones de utilidad
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Hacer que las estadísticas estén disponibles globalmente
window.stats = window.stats || {
    programas_financiacion: 150
};