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
    if (requisitos.length === An:0) {
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
