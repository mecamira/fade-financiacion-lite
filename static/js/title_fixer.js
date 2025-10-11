// Script específico para corregir problemas de formato en los títulos
document.addEventListener('DOMContentLoaded', function() {
    // Esperar a que la página se cargue completamente con un poco de retraso para asegurar que
    // el formatting.js ya ha terminado su trabajo
    setTimeout(function() {
        // Función para aplicar estilo a cualquier elemento que coincida con ciertos criterios
        function fixTitleStyles() {
            const problemTerms = [
                "Cumplimiento de requisitos",
                "Networking",
                "Asesoramiento profesional",
                "Monitorización continua",
                "Preparación exhaustiva",
                "Colaboración efectiva",
                "Presentación impecable",
                "Plan de negocio sólido"
            ];
            
            // Buscar todos los elementos en la página
            const allElements = document.querySelectorAll('*');
            
            // Recorrer todos los elementos
            allElements.forEach(element => {
                // Verificar si el contenido de texto coincide con alguno de los términos problemáticos
                if (element.textContent) {
                    const trimmedText = element.textContent.trim();
                    
                    // Comprobar si el texto coincide exactamente con alguno de los términos problemáticos
                    const foundTerm = problemTerms.find(term => trimmedText.includes(term));
                    
                    if (foundTerm) {
                        // Verificar si este elemento es un título (no un párrafo o parte de otro elemento)
                        // Buscamos elementos que sean h1-h6, div, span, p, strong, o que estén dentro de un encabezado de tarjeta
                        const isHeadingElement = 
                            /^h[1-6]$/i.test(element.tagName) || 
                            element.tagName === 'DIV' || 
                            element.tagName === 'SPAN' ||
                            element.tagName === 'STRONG' ||
                            element.tagName === 'P' ||
                            element.closest('.card-header');
                        
                        // Si es un posible encabezado y no tiene estilos de color blanco
                        if (isHeadingElement && 
                            (!element.style.color || element.style.color !== 'white')) {
                            
                            // Buscar hasta 3 niveles para encontrar el padre correcto para aplicar los estilos
                            let targetElement = element;
                            let parent = element.parentElement;
                            let level = 0;
                            
                            // Buscar un elemento padre que podría ser un encabezado o contenedor
                            while (parent && level < 3) {
                                // Si el padre es una tarjeta o tiene un fondo azul, usar el elemento actual
                                if (parent.classList.contains('card') || 
                                    parent.classList.contains('card-header') ||
                                    (parent.style && parent.style.backgroundColor && 
                                     parent.style.backgroundColor.includes('blue'))) {
                                    break;
                                }
                                
                                // Si el padre es más específico (como un div con ciertos estilos)
                                if (parent.style && 
                                    (parent.style.display === 'flex' || 
                                     parent.style.display === 'inline-block')) {
                                    targetElement = parent;
                                    break;
                                }
                                
                                parent = parent.parentElement;
                                level++;
                            }
                            
                            // Comprobar si el elemento está dentro de un elemento que comienza con $
                            const dollarParent = findDollarAncestor(targetElement);
                            if (dollarParent) {
                                // Ya está dentro de un elemento $ formateado, no hacer nada
                                return;
                            }
                            
                            // Verificar si el elemento ya tiene estilos de formato correctos
                            const hasCorrectStyles = 
                                (targetElement.style && targetElement.style.backgroundColor === '#0a58ca') ||
                                targetElement.classList.contains('bg-primary');
                            
                            if (!hasCorrectStyles) {
                                // Comprobar si este elemento está relacionado con el símbolo $
                                if (isDollarRelated(targetElement)) {
                                    // Crear un div principal para la tarjeta
                                    const cardDiv = document.createElement('div');
                                    cardDiv.style.cssText = 'margin-bottom: 1.5rem; box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1); border: none; overflow: hidden; border-radius: 0.5rem;';
                                    
                                    // Crear el encabezado de la tarjeta
                                    const headerDiv = document.createElement('div');
                                    headerDiv.style.cssText = 'background-color: #2979e7; padding: 1rem; border-radius: 0.5rem 0.5rem 0 0; border: none;';
                                    
                                    // Crear contenedor flex para el símbolo $ y el título
                                    const flexDiv = document.createElement('div');
                                    flexDiv.style.cssText = 'display: flex; align-items: center;';
                                    
                                    // Crear el símbolo $
                                    const dollarSpan = document.createElement('div');
                                    dollarSpan.textContent = '$';
                                    dollarSpan.style.cssText = 'background-color: rgba(255, 255, 255, 0.3); color: white; font-weight: bold; width: 30px; height: 30px; display: flex; justify-content: center; align-items: center; border-radius: 50%; margin-right: 0.75rem; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);';
                                    
                                    // Crear el título
                                    const titleH5 = document.createElement('h5');
                                    titleH5.textContent = trimmedText;
                                    titleH5.style.cssText = 'color: white; font-weight: 700; margin-bottom: 0; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);';
                                    
                                    // Ensamblar la estructura
                                    flexDiv.appendChild(dollarSpan);
                                    flexDiv.appendChild(titleH5);
                                    headerDiv.appendChild(flexDiv);
                                    cardDiv.appendChild(headerDiv);
                                    
                                    // Crear el cuerpo de la tarjeta
                                    const bodyDiv = document.createElement('div');
                                    bodyDiv.style.cssText = 'background-color: #f1f8ff; padding: 1rem; border-radius: 0 0 0.5rem 0.5rem; border: 1px solid #e9ecef; border-top: none;';
                                    
                                    // Si hay una descripción tras el título, añadirla al cuerpo
                                    const nextElement = targetElement.nextElementSibling;
                                    if (nextElement && !isDollarRelated(nextElement)) {
                                        const paragraph = document.createElement('p');
                                        paragraph.textContent = nextElement.textContent.trim();
                                        paragraph.style.marginBottom = '0';
                                        bodyDiv.appendChild(paragraph);
                                        
                                        // Ocultar el elemento original de la descripción
                                        nextElement.style.display = 'none';
                                    }
                                    
                                    cardDiv.appendChild(bodyDiv);
                                    
                                    // Reemplazar el elemento original con la nueva estructura
                                    targetElement.parentNode.insertBefore(cardDiv, targetElement);
                                    targetElement.style.display = 'none';
                                } else {
                                    // Aplicar estilo directamente para el caso de títulos simples
                                    targetElement.style.cssText = 'display: inline-block; color: white; background-color: #0a58ca; padding: 0.4rem 1rem; margin: 0.75rem 0; border-radius: 0.3rem; font-weight: 600; border-left: 3px solid white;';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Función auxiliar para verificar si un elemento está relacionado con el símbolo $
        function isDollarRelated(element) {
            // Verificar si el elemento o sus hijos contienen el símbolo $
            return element.textContent.includes('$') || 
                   (element.previousElementSibling && 
                    element.previousElementSibling.textContent.includes('$'));
        }
        
        // Función auxiliar para encontrar un ancestro que contenga el símbolo $
        function findDollarAncestor(element) {
            let current = element;
            let level = 0;
            
            while (current && level < 5) {
                if (current.textContent && current.textContent.includes('$')) {
                    // Verificar si es un elemento de tarjeta
                    if (current.classList.contains('card') || 
                        current.style.boxShadow || 
                        current.style.borderRadius) {
                        return current;
                    }
                }
                current = current.parentElement;
                level++;
            }
            
            return null;
        }
        
        // Ejecutar la función para corregir los estilos
        fixTitleStyles();
        
        // En algunos casos, el contenido podría cargarse dinámicamente, así que volvemos a ejecutar
        // después de un breve retraso para asegurarnos de que todo está procesado
        setTimeout(fixTitleStyles, 500);
    }, 100); // Esperar 100ms para asegurarse de que todo el contenido está cargado
});