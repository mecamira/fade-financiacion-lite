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
