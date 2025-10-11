// Función específica para corregir símbolos de euro
function correctEuroSymbols(text) {
    if (!text) return text;
    
    const euroReplacements = {
        '\\u20ac': '€',
        '\u20ac': '€',
        'EUR': '€',
        'euros': '€',
        'Euros': '€',
        'â¬': '€',
        '\\xe2\\x82\\xac': '€',
        '\xe2\x82\xac': '€'
    };
    
    let result = text;
    for (const [old, now] of Object.entries(euroReplacements)) {
        result = result.replace(new RegExp(old, 'g'), now);
    }
    
    return result;
}

// Formatear respuesta para mejor visualización
document.addEventListener('DOMContentLoaded', function() {
    // Procesar la respuesta del asesor
    const responseDiv = document.getElementById('formatted-response');
    if (responseDiv) {
        let originalHtml = responseDiv.innerHTML;
        
        // Primero, detectar y formatear los elementos que comienzan con $
        const dollarRegex = /\$\s*(.*?)(?=<br>|\n|$)/g;
        const dollarMatches = Array.from(originalHtml.matchAll(dollarRegex));
        
        if (dollarMatches && dollarMatches.length > 0) {
            // Reemplazar directamente en el HTML original
            dollarMatches.forEach(match => {
                const fullMatch = match[0];
                const titleText = match[1].trim();
                
                // Crear un ID único para este título
                const titleId = 'title-' + Math.random().toString(36).substring(2, 15);
                
                // Reemplazar en el HTML original
                originalHtml = originalHtml.replace(
                    fullMatch, 
                    `<span id="${titleId}" class="dollar-title">${fullMatch}</span>`
                );
            });
        }

        // Ahora procesamos con el enfoque habitual
        responseDiv.innerHTML = originalHtml;
        
        // Eliminar texto "Resumen en JSON" y la despedida final
        let html = responseDiv.innerHTML;
        html = html.replace(/Resumen en JSON[\s\S]*?Recordatorio importante/g, "### Recordatorio importante");
        html = html.replace(/Espero que esta información[\s\S]*?proyecto![\s\S]*$/g, "");
        
        // Primero, reemplazar las etiquetas <br> literales con saltos de línea reales
        html = html.replace(/<br>/g, '\n');
        
        // Aplicar corrección de símbolos de euro
        html = correctEuroSymbols(html);
        
        // Reemplazar bloques de código JSON
        html = html.replace(/```json\s*([\s\S]*?)\s*```/g, '<pre class="bg-dark text-light p-3 rounded my-3"><code>$1</code></pre>');
        
        // Reemplazar otros bloques de código
        html = html.replace(/```([\w]*)\s*([\s\S]*?)\s*```/g, '<pre class="bg-dark text-light p-3 rounded my-3"><code>$2</code></pre>');
        
        // Dar formato a los títulos
        html = html.replace(/\n# ([^\n]+)/g, '<h2 class="advisor-heading-1 mt-4 mb-3">$1</h2>');
        html = html.replace(/\n## ([^\n]+)/g, '<h3 class="advisor-heading-2 mt-4 mb-3">$1</h3>');
        html = html.replace(/\n### ([^\n]+)/g, '<h4 class="advisor-heading-3 mt-3 mb-2">$1</h4>');
        
        // Mejorar el formato de las recomendaciones
        html = html.replace(/\*\*([^\*]+):\*\*/g, '<h4 class="advisor-program-title mt-4 mb-3">$1</h4>');
        
        // Dar formato a secciones importantes (por ejemplo, nombres de programas)
        html = html.replace(/\*\*([^\*]+)\*\*/g, '<strong class="advisor-highlight">$1</strong>');
        
        // Convertir el texto en formato HTML con estructura correcta
        let formattedHtml = "<div class='advisor-response'>";
        
        // Dividir por líneas para procesar cada una
        const lines = html.split('\n');
        
        // Identificar y procesar bloques de contenido
        let inNumberedList = false;
        let inBulletList = false;
        let itemLevel = 0; // Nivel de anidación
        let currentListType = []; // Pila para rastrear tipos de listas anidadas
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Saltar líneas vacías
            if (!line) {
                if (inNumberedList) {
                    formattedHtml += "</ol>";
                    inNumberedList = false;
                }
                if (inBulletList) {
                    formattedHtml += "</ul>";
                    inBulletList = false;
                }
                itemLevel = 0;
                currentListType = [];
                formattedHtml += "<div class='py-1'></div>"; // Espacio entre párrafos
                continue;
            }
            
            // Aplicar estilo especial para "Consejos para aumentar las probabilidades de éxito"
            if (line.includes("probabilidades de éxito") || line.includes("Consejos para")) {
                formattedHtml += `<h2 class="advisor-heading-1 mt-4 mb-4">${line}</h2>`;
                continue;
            }
            
            // Tratar especialmente la sección de "Recordatorio importante"
            if (line.includes("Recordatorio importante")) {
                if (inNumberedList) {
                    formattedHtml += "</ol>";
                    inNumberedList = false;
                }
                if (inBulletList) {
                    formattedHtml += "</ul>";
                    inBulletList = false;
                }
                
                // Extraer el contenido del recordatorio (todo lo que sigue a esta línea)
                let reminderContent = "";
                let j = i + 1;
                while (j < lines.length && lines[j].trim()) {
                    reminderContent += lines[j] + " ";
                    j++;
                }
                
                formattedHtml += `
                <div class="alert alert-warning advisor-reminder mt-4">
                    <h4 class="alert-heading"><i class="fas fa-exclamation-triangle me-2"></i>Recordatorio importante</h4>
                    <p>${reminderContent.trim()}</p>
                </div>`;
                
                // Saltar las líneas ya procesadas
                i = j - 1;
                continue;
            }
            
            // Manejar líneas que comienzan con el símbolo $ (consejos)
            if (line.startsWith("$")) {
                // Si estamos en una lista, cerrarla primero
                if (inNumberedList) {
                    formattedHtml += "</ol>";
                    inNumberedList = false;
                }
                if (inBulletList) {
                    formattedHtml += "</ul>";
                    inBulletList = false;
                }
                
                // Extraer el título y la descripción
                const title = line.substring(1).trim();
                let description = "";
                let j = i + 1;
                
                // Buscar la descripción en las siguientes líneas
                while (j < lines.length && !lines[j].startsWith("$") && lines[j].trim() !== "") {
                    if (description) description += " ";
                    description += lines[j].trim();
                    j++;
                }
                
                // Crear el HTML para el consejo directamente - SIN USAR CLASES
                formattedHtml += `
                <div style="margin-bottom: 1.5rem; box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1); border: none; overflow: hidden; border-radius: 0.5rem;">
                    <div style="background-color: #2979e7; padding: 1rem; border-radius: 0.5rem 0.5rem 0 0; border: none;">
                        <div style="display: flex; align-items: center;">
                            <div style="background-color: rgba(255, 255, 255, 0.3); color: white; font-weight: bold; width: 30px; height: 30px; display: flex; justify-content: center; align-items: center; border-radius: 50%; margin-right: 0.75rem; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);">$</div>
                            <h5 style="color: white; font-weight: 700; margin-bottom: 0; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);">${title}</h5>
                        </div>
                    </div>
                    <div style="background-color: #f1f8ff; padding: 1rem; border-radius: 0 0 0.5rem 0.5rem; border: 1px solid #e9ecef; border-top: none;">
                        <p style="margin-bottom: 0;">${description}</p>
                    </div>
                </div>
                `;
                
                // Saltar las líneas ya procesadas
                i = j - 1;
                continue;
            }
            
            // Manejar elementos de lista numerada (1. Texto)
            const numberedMatch = line.match(/^(\d+)\.(\s+.+)/);
            if (numberedMatch) {
                const content = numberedMatch[2].trim();
                
                // Cerrar listas si estamos en una diferente
                if (inBulletList) {
                    formattedHtml += "</ul>";
                    inBulletList = false;
                }
                
                // El primer elemento de lista numerada inicia una nueva sección
                if (!inNumberedList) {
                    formattedHtml += "<ol style='list-style: none; padding-left: 0; margin-bottom: 1rem;'>";
                    inNumberedList = true;
                }
                
                // Extraer el nombre del programa
                let programName = content;
                let programDescription = "";
                const splitIndex = content.search(/[:.]/);
                
                if (splitIndex > 0) {
                    programName = content.substring(0, splitIndex).trim();
                    programDescription = content.substring(splitIndex + 1).trim();
                }
                
                // Determinar el color de fondo
                let bgColor = "#2979e7"; // Color azul predeterminado
                
                if (programName.includes("CDTI")) {
                    bgColor = "#198754"; // Verde
                } else if (programName.includes("IDEPA")) {
                    bgColor = "#17a2b8"; // Cyan
                } else if (programName.includes("Europea") || programName.includes("Horizonte")) {
                    bgColor = "#dc3545"; // Rojo
                }
                
                // Crear una tarjeta para cada programa con estilos inline
                formattedHtml += `
                <li>
                    <div style="margin-bottom: 1rem; box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); border-radius: 0.5rem; overflow: hidden; transition: transform 0.2s ease;">
                        <div style="background-color: ${bgColor}; padding: 0.5rem 1rem; border-radius: 0.5rem 0.5rem 0 0;">
                            <div style="display: flex; align-items: center;">
                                <i class="fas fa-dollar-sign me-2" style="color: white;"></i>
                                <h5 style="color: white; font-weight: 700; margin-bottom: 0; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);">${programName}</h5>
                            </div>
                        </div>
                        <div style="padding: 1rem; background-color: white; border: 1px solid #e9ecef; border-top: none; border-radius: 0 0 0.5rem 0.5rem;">
                            ${programDescription ? `<p style="margin-bottom: 0.5rem;">${programDescription}</p>` : ''}
                        </div>
                    </div>
                </li>`;
                continue;
            }
            
            // Manejar elementos de lista con viñetas (- Texto o * Texto)
            const bulletMatch = line.match(/^([\-\*])(\s+.+)/);
            if (bulletMatch) {
                const content = bulletMatch[2].trim();
                
                // Cerrar otras listas si es necesario
                if (inNumberedList) {
                    formattedHtml += "</ol>";
                    inNumberedList = false;
                }
                
                if (!inBulletList) {
                    formattedHtml += "<ul style='margin-left: 1.5rem; margin-bottom: 1rem;'>";
                    inBulletList = true;
                    itemLevel = 0;
                    currentListType = ['bullet'];
                }
                
                formattedHtml += `<li>${content}</li>`;
                continue;
            }
            
            // Manejar elementos de lista anidados con círculos (o Texto)
            const circleMatch = line.match(/^(o)(\s+.+)/);
            if (circleMatch) {
                const content = circleMatch[2].trim();
                
                // Si estamos en una lista, cerrarla primero
                if (inNumberedList) {
                    formattedHtml += "</ol>";
                    inNumberedList = false;
                }
                if (inBulletList) {
                    formattedHtml += "</ul>";
                    inBulletList = false;
                }
                
                // Convertir a título de subsección
                formattedHtml += `<h5 style="color: #0d6efd; font-weight: 500; margin-top: 0.75rem; margin-bottom: 0.5rem;">${content}</h5>`;
                continue;
            }
            
            // Manejar elementos de lista anidados con cuadrados (■ Texto)
            const squareMatch = line.match(/^(\u25a0|\u25a1|\u25aa|\u25ab|\u25fc|\u25fb|■|□|▪|▫)(\s+.+)/);
            if (squareMatch) {
                const content = squareMatch[2].trim();
                
                // Si estamos en una lista, cerrarla primero
                if (inNumberedList) {
                    formattedHtml += "</ol>";
                    inNumberedList = false;
                }
                if (inBulletList) {
                    formattedHtml += "</ul>";
                    inBulletList = false;
                }
                
                // Convertir a etiqueta de detalle
                formattedHtml += `<div style="margin-bottom: 0.5rem; display: flex; align-items: baseline; margin-left: 1.5rem;"><i class="fas fa-square me-2" style="color: #0d6efd;"></i>${content}</div>`;
                continue;
            }
            
            // Tratar secciones que comienzan con etiquetas conocidas de forma especial
            if (line.startsWith("Organismo") || 
                line.startsWith("Tipo de ayuda") || 
                line.startsWith("Intensidad") || 
                line.startsWith("Convocatoria") ||
                line.startsWith("Fechas aproximadas") ||
                line.startsWith("Requisitos") ||
                line.startsWith("Adecuación") ||
                line.startsWith("Nivel de adecuación") ||
                line.startsWith("Justificación") ||
                line.startsWith("Cumplimiento de requisitos") ||
                line.startsWith("Monitorización de convocatorias") ||
                line.startsWith("Proyectos de Innovación IDEPA") ||
                line.startsWith("Networking") ||
                line.startsWith("Cheques de Innovación")) {
                
                // Si estamos en una lista, cerrarla primero
                if (inNumberedList) {
                    formattedHtml += "</ol>";
                    inNumberedList = false;
                }
                if (inBulletList) {
                    formattedHtml += "</ul>";
                    inBulletList = false;
                }
                
                // Crear una etiqueta específica para estos elementos
                const parts = line.split(":");
                if (parts.length > 1) {
                    formattedHtml += `<div style="display: flex; margin-bottom: 0.5rem; padding: 0.3rem 0; border-bottom: 1px dotted #e9ecef;">
                        <div style="font-weight: 700; color: #0a58ca; background-color: #f0f7ff; padding: 0.2rem 0.4rem; border-radius: 0.2rem; width: 150px; flex-shrink: 0;">${parts[0]}:</div>
                        <div>${parts.slice(1).join(":").trim()}</div>
                    </div>`;
                } else {
                    // IMPORTANTE: Usamos estilos inline directos, completamente independientes de clases CSS
                    formattedHtml += `<div style="display: inline-block; color: white; background-color: #0a58ca; padding: 0.4rem 1rem; margin: 0.75rem 0; border-radius: 0.3rem; font-weight: 600; border-left: 3px solid white;">${line}</div>`;
                }
                continue;
            }
            
            // Si llegamos aquí, es un párrafo normal
            if (inNumberedList) {
                formattedHtml += "</ol>";
                inNumberedList = false;
            }
            if (inBulletList) {
                formattedHtml += "</ul>";
                inBulletList = false;
            }
            
            // Comprobar si la línea parece un título o un programa especial
            if ((/^[A-Z][^\.]+(:|$)/.test(line) && line.length < 80) || 
                line.includes("Proyectos de Innovación") ||
                line.includes("IDEPA") ||
                line.includes("Programa") ||
                line.includes("Subvención") ||
                line.includes("CDTI") ||
                line.includes("Ayudas") ||
                line.includes("Cheques de Innovación") ||
                line.includes("Asesoramiento profesional") ||
                line.includes("Networking")) { 
                
                // Es un título importante, formatearlo adecuadamente con estilos inline
                formattedHtml += `<h3 style="color: #0d6efd; font-size: 1.2rem; font-weight: 600; background-color: #f8f9fa; padding: 0.5rem 0.75rem; border-radius: 0.3rem; border-left: 4px solid #0d6efd; margin-top: 1.25rem; margin-bottom: 0.75rem;">${line}</h3>`;
            } else {
                // Es un párrafo normal
                formattedHtml += `<p style="margin-bottom: 0.75rem; text-align: justify;">${line}</p>`;
            }
        }
        
        // Cerrar cualquier lista que quede abierta
        if (inNumberedList) {
            formattedHtml += "</ol>";
        }
        if (inBulletList) {
            formattedHtml += "</ul>";
        }
        
        formattedHtml += "</div>";
        
        responseDiv.innerHTML = formattedHtml;
        
        // POST-PROCESAMIENTO: Buscar todos los elementos $ que pudieron quedar sin procesar
        // Este es un último paso de seguridad para capturar cualquier caso no detectado
        setTimeout(() => {
            // Buscar todos los elementos que podrían contener títulos con $ que quedaron sin formatear
            const allElements = responseDiv.querySelectorAll('*');
            allElements.forEach(element => {
                if (element.textContent && element.textContent.includes('$') && element.textContent.trim().startsWith('$')) {
                    // Encontramos un título con $ sin formatear
                    const fullText = element.textContent.trim();
                    const titleText = fullText.substring(1).trim();
                    
                    // Crear la estructura HTML formateada
                    const newElement = document.createElement('div');
                    newElement.style.cssText = 'margin-bottom: 1.5rem; box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1); border: none; overflow: hidden; border-radius: 0.5rem;';
                    
                    newElement.innerHTML = `
                        <div style="background-color: #2979e7; padding: 1rem; border-radius: 0.5rem 0.5rem 0 0; border: none;">
                            <div style="display: flex; align-items: center;">
                                <div style="background-color: rgba(255, 255, 255, 0.3); color: white; font-weight: bold; width: 30px; height: 30px; display: flex; justify-content: center; align-items: center; border-radius: 50%; margin-right: 0.75rem; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);">$</div>
                                <h5 style="color: white; font-weight: 700; margin-bottom: 0; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);">${titleText}</h5>
                            </div>
                        </div>
                        <div style="background-color: #f1f8ff; padding: 1rem; border-radius: 0 0 0.5rem 0.5rem; border: 1px solid #e9ecef; border-top: none;">
                            <p style="margin-bottom: 0;"></p>
                        </div>
                    `;
                    
                    // Si el elemento está dentro de otro que tiene hijos, reemplazarlo
                    const parentNode = element.parentNode;
                    if (parentNode && parentNode.childNodes.length > 0) {
                        // Buscar hermanos que podrían ser la descripción
                        let nextSibling = element.nextSibling;
                        while (nextSibling && (nextSibling.nodeType === 3 || !nextSibling.textContent.trim().startsWith('$'))) {
                            // Si es un nodo de texto o un elemento sin $ al inicio, considerarlo parte de la descripción
                            if (nextSibling.textContent && nextSibling.textContent.trim()) {
                                const descriptionPara = newElement.querySelector('p');
                                if (descriptionPara) {
                                    descriptionPara.textContent += ' ' + nextSibling.textContent.trim();
                                }
                            }
                            const tempSibling = nextSibling;
                            nextSibling = nextSibling.nextSibling;
                            if (tempSibling.nodeType !== 3) { // No eliminar nodos de texto para evitar problemas
                                parentNode.removeChild(tempSibling);
                            }
                        }
                        
                        // Reemplazar el elemento original
                        parentNode.replaceChild(newElement, element);
                    }
                }
            });
            
            // Segunda pasada: Buscar todos los elementos que contienen "Cumplimiento de requisitos" o "Networking"
            // o cualquier otro término que debería tener un estilo específico
            const specialTerms = [
                "Cumplimiento de requisitos",
                "Networking",
                "Asesoramiento profesional",
                "Monitorización continua"
            ];
            
            allElements.forEach(element => {
                if (element.textContent) {
                    // Corregir símbolos de euro en elementos
                    if (element.textContent.includes('â¬') || 
                        element.textContent.includes('\\u20ac') ||
                        element.textContent.includes('EUR') ||
                        element.textContent.includes('euros') ||
                        element.textContent.includes('Euros')) {
                        element.textContent = correctEuroSymbols(element.textContent);
                    }
                    
                    specialTerms.forEach(term => {
                        if (element.textContent.includes(term) && element.textContent.trim() === term) {
                            // Si es exactamente el término especial y no tiene estilos aplicados
                            if (!element.style || !element.style.color || element.style.color !== "white") {
                                // Aplicar estilo directamente al elemento
                                element.style.cssText = 'display: inline-block; color: white; background-color: #0a58ca; padding: 0.4rem 1rem; margin: 0.75rem 0; border-radius: 0.3rem; font-weight: 600; border-left: 3px solid white;';
                            }
                        }
                    });
                }
            });
            
        }, 0);
    }
});