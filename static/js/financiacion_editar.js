// Gestión Manual de Convocatorias
document.addEventListener('DOMContentLoaded', function() {
    
    // Event listeners
    document.getElementById('btn-buscar').addEventListener('click', buscar);
    document.getElementById('btn-nuevo').addEventListener('click', abrirNuevo);
    document.getElementById('btn-guardar').addEventListener('click', guardar);
    document.getElementById('btn-eliminar').addEventListener('click', confirmarEliminar);
    
    document.getElementById('search-input').addEventListener('keypress', e => {
        if (e.key === 'Enter') buscar();
    });
    
    // Buscar convocatorias
    async function buscar() {
        const search = document.getElementById('search-input').value;
        const organismo = document.getElementById('filter-organismo').value;
        const estado = document.getElementById('filter-estado').value;
        
        document.getElementById('loading').classList.remove('d-none');
        
        try {
            const params = new URLSearchParams();
            if (search) params.append('search', search);
            if (organismo) params.append('organismo', organismo);
            if (estado) params.append('estado', estado);
            
            const response = await fetch(`/api/programas-financiacion?${params}`);
            const data = await response.json();
            
            if (data.success) {
                mostrarResultados(data.programas);
            }
        } catch (error) {
            alert('Error al buscar');
        } finally {
            document.getElementById('loading').classList.add('d-none');
        }
    }
    
    // Mostrar resultados
    function mostrarResultados(programas) {
        const tbody = document.getElementById('tabla-body');
        document.getElementById('total').textContent = programas.length;
        
        if (programas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No se encontraron resultados</td></tr>';
            return;
        }
        
        tbody.innerHTML = programas.map(p => {
            const nombre = p.nombre_coloquial || p.nombre || '-';
            return `
                <tr>
                    <td><strong>${nombre}</strong></td>
                    <td>${p.organismo || '-'}</td>
                    <td>${p.convocatoria?.estado ? `<span class="badge bg-${getBadge(p.convocatoria.estado)}">${p.convocatoria.estado}</span>` : '-'}</td>
                    <td>${p.codigo_bdns || '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editar('${p.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="eliminar('${p.id}', '${nombre.replace(/'/g, "\\'")}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }
    
    function getBadge(estado) {
        if (estado?.includes('Abierta')) return 'success';
        if (estado?.includes('Cierre próximo')) return 'warning';
        if (estado?.includes('Próxima apertura')) return 'info';
        if (estado?.includes('Pendiente')) return 'warning';
        if (estado?.includes('Cerrada')) return 'secondary';
        return 'secondary';
    }
    
    // Abrir modal nuevo
    function abrirNuevo() {
        document.getElementById('modalTitle').textContent = 'Nueva Convocatoria';
        document.getElementById('edit-id').value = '';
        limpiarFormulario();
        new bootstrap.Modal(document.getElementById('modalEditar')).show();
    }
    
    // Editar
    window.editar = async function(id) {
        try {
            console.log(`[DEBUG] Intentando cargar programa con ID: ${id}`);
            const response = await fetch(`/api/programa/${id}`);
            console.log(`[DEBUG] Response status: ${response.status}`);

            const data = await response.json();
            console.log('[DEBUG] Datos recibidos:', data);

            if (data.success) {
                console.log('[DEBUG] Programa cargado exitosamente:', data.programa);
                cargarDatos(data.programa);
                document.getElementById('modalTitle').textContent = 'Editar Convocatoria';
                new bootstrap.Modal(document.getElementById('modalEditar')).show();
            } else {
                console.error('[ERROR] La API retornó success=false:', data);
                alert('Error al cargar: ' + (data.error || 'Error desconocido'));
            }
        } catch (error) {
            console.error('[ERROR] Excepción al cargar programa:', error);
            console.error('[ERROR] Stack trace:', error.stack);
            alert('Error al cargar: ' + error.message);
        }
    };
    
    // Cargar datos en formulario
    function cargarDatos(p) {
        try {
            console.log('[DEBUG] Iniciando carga de datos en formulario:', p);

            document.getElementById('edit-id').value = p.id || '';
            // Compatibilidad: usar nombre_coloquial o nombre
            document.getElementById('edit-nombre').value = p.nombre_coloquial || p.nombre || '';
            document.getElementById('edit-nombre-oficial').value = p.nombre_oficial || '';
            document.getElementById('edit-bdns').value = p.codigo_bdns || '';
            document.getElementById('edit-organismo').value = p.organismo || '';
            // Compatibilidad: tipo_ayuda puede ser array o string
            let tipoAyuda = p.tipo_ayuda;
            if (Array.isArray(tipoAyuda)) {
                tipoAyuda = tipoAyuda.join(', ');
            }
            document.getElementById('edit-tipo').value = tipoAyuda || '';
            document.getElementById('edit-ambito').value = p.ambito || '';
            document.getElementById('edit-estado').value = p.convocatoria?.estado || 'Abierta';
            document.getElementById('edit-fecha-apertura').value = p.convocatoria?.fecha_apertura || '';
            document.getElementById('edit-fecha-cierre').value = p.convocatoria?.fecha_cierre || '';
            document.getElementById('edit-resumen').value = p.resumen_breve || '';
            document.getElementById('edit-descripcion').value = p.descripcion_detallada || '';
            document.getElementById('edit-comentarios').value = p.comentarios || '';

            // Asegurar que los arrays sean arrays (compatibilidad con datos antiguos)
            const toArray = (value) => {
                if (!value) return [];
                if (Array.isArray(value)) return value;
                if (typeof value === 'string') return [value];
                return [];
            };

            document.getElementById('edit-beneficiarios').value = toArray(p.beneficiarios).join('\n');
            document.getElementById('edit-sectores').value = toArray(p.sectores).join('\n');
            document.getElementById('edit-tipo-proyecto').value = toArray(p.tipo_proyecto).join('\n');
            document.getElementById('edit-requisitos').value = toArray(p.requisitos).join('\n');
            document.getElementById('edit-gastos-subvencionables').value = toArray(p.gastos_subvencionables).join('\n');
            // Compatibilidad: origen_fondos vs fondos_europeos (array)
            let fondos = p.fondos_europeos || p.origen_fondos || '';
            if (Array.isArray(fondos)) {
                fondos = fondos.join(', ');
            }
            document.getElementById('edit-origen-fondos').value = fondos || '';
            document.getElementById('edit-intensidad').value = p.financiacion?.intensidad || '';
            document.getElementById('edit-presupuesto-total').value = p.financiacion?.presupuesto_total || p.financiacion?.importe_maximo || '';
            document.getElementById('edit-presupuesto-minimo').value = p.financiacion?.presupuesto_minimo || '';
            document.getElementById('edit-presupuesto-maximo').value = p.financiacion?.presupuesto_maximo || '';
            document.getElementById('edit-importe-minimo-subvencionable').value = p.financiacion?.importe_minimo_subvencionable || '';
            document.getElementById('edit-importe-maximo-subvencionable').value = p.financiacion?.importe_maximo_subvencionable || '';
            document.getElementById('edit-url-bdns').value = p.enlaces?.url_bdns || '';
            document.getElementById('edit-url-convocatoria').value = p.enlaces?.convocatoria || '';
            document.getElementById('edit-url-bases').value = p.enlaces?.bases_reguladoras || p.enlaces?.bases || '';
            document.getElementById('edit-url-extracto').value = p.enlaces?.extracto || '';

            console.log('[DEBUG] Datos cargados exitosamente en el formulario');
        } catch (error) {
            console.error('[ERROR] Error al cargar datos en formulario:', error);
            console.error('[ERROR] Stack trace:', error.stack);
            throw error; // Re-lanzar el error para que lo capture el catch superior
        }
    }
    
    // Limpiar formulario
    function limpiarFormulario() {
        ['edit-id', 'edit-nombre', 'edit-nombre-oficial', 'edit-bdns', 'edit-organismo', 'edit-tipo', 'edit-ambito',
         'edit-fecha-apertura', 'edit-fecha-cierre', 'edit-resumen', 'edit-descripcion', 'edit-comentarios',
         'edit-beneficiarios', 'edit-sectores', 'edit-tipo-proyecto', 'edit-requisitos', 'edit-gastos-subvencionables',
         'edit-origen-fondos', 'edit-intensidad', 'edit-presupuesto-total', 'edit-presupuesto-minimo', 'edit-presupuesto-maximo',
         'edit-importe-minimo-subvencionable', 'edit-importe-maximo-subvencionable',
         'edit-url-bdns', 'edit-url-convocatoria', 'edit-url-bases', 'edit-url-extracto'].forEach(id => {
            document.getElementById(id).value = '';
        });
        document.getElementById('edit-estado').value = 'Abierta';
    }
    
    // Guardar
    async function guardar() {
        const id = document.getElementById('edit-id').value;
        const datos = obtenerDatos();

        if (!datos.nombre_coloquial || !datos.organismo || !datos.tipo_ayuda || datos.tipo_ayuda.length === 0) {
            alert('Completa los campos obligatorios (nombre, organismo y tipo de ayuda)');
            return;
        }
        
        const btn = document.getElementById('btn-guardar');
        btn.disabled = true;
        btn.textContent = 'Guardando...';
        
        try {
            const response = await fetch(id ? `/api/programa/${id}` : '/api/guardar-programa', {
                method: id ? 'PUT' : 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datos)
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(id ? 'Actualizado' : 'Creado');
                bootstrap.Modal.getInstance(document.getElementById('modalEditar')).hide();
                buscar();
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            alert('Error al guardar');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Guardar';
        }
    }
    
    // Obtener datos del formulario
    function obtenerDatos() {
        const beneficiarios = document.getElementById('edit-beneficiarios').value
            .split('\n').map(s => s.trim()).filter(s => s);
        const sectores = document.getElementById('edit-sectores').value
            .split('\n').map(s => s.trim()).filter(s => s);
        const tipo_proyecto = document.getElementById('edit-tipo-proyecto').value
            .split('\n').map(s => s.trim()).filter(s => s);
        const requisitos = document.getElementById('edit-requisitos').value
            .split('\n').map(s => s.trim()).filter(s => s);
        const gastos_subvencionables = document.getElementById('edit-gastos-subvencionables').value
            .split('\n').map(s => s.trim()).filter(s => s);

        // Tipo de ayuda como array (separado por comas)
        const tipoAyudaStr = document.getElementById('edit-tipo').value || '';
        const tipo_ayuda = tipoAyudaStr.split(',').map(s => s.trim()).filter(s => s);

        // Fondos europeos como array (separado por comas)
        const fondosStr = document.getElementById('edit-origen-fondos').value || '';
        const fondos_europeos = fondosStr.split(',').map(s => s.trim()).filter(s => s);

        // Obtener URLs
        const urlBdns = document.getElementById('edit-url-bdns').value.trim() || null;
        const urlConvocatoria = document.getElementById('edit-url-convocatoria').value.trim() || null;
        const urlBases = document.getElementById('edit-url-bases').value.trim() || null;
        const urlExtracto = document.getElementById('edit-url-extracto').value.trim() || null;

        const nombreColoquial = document.getElementById('edit-nombre').value;
        const nombreOficial = document.getElementById('edit-nombre-oficial').value.trim() || nombreColoquial;

        return {
            // Usar nombre_coloquial como campo principal (compatibilidad hacia atrás)
            nombre_coloquial: nombreColoquial,
            nombre: nombreColoquial,  // Mantener nombre también para compatibilidad
            nombre_oficial: nombreOficial,  // Campo separado para el nombre oficial
            codigo_bdns: document.getElementById('edit-bdns').value || null,
            organismo: document.getElementById('edit-organismo').value,
            tipo_ayuda: tipo_ayuda,  // Ahora es array
            ambito: document.getElementById('edit-ambito').value || null,
            fondos_europeos: fondos_europeos,  // Campo nuevo (array)
            comentarios: document.getElementById('edit-comentarios').value || '',  // Campo nuevo
            convocatoria: {
                estado: document.getElementById('edit-estado').value,
                fecha_apertura: document.getElementById('edit-fecha-apertura').value || null,
                fecha_cierre: document.getElementById('edit-fecha-cierre').value || null
            },
            financiacion: {
                intensidad: document.getElementById('edit-intensidad').value || null,
                presupuesto_total: document.getElementById('edit-presupuesto-total').value || null,
                presupuesto_minimo: document.getElementById('edit-presupuesto-minimo').value || null,
                presupuesto_maximo: document.getElementById('edit-presupuesto-maximo').value || null,
                importe_minimo_subvencionable: document.getElementById('edit-importe-minimo-subvencionable').value || null,  // Campo nuevo
                importe_maximo_subvencionable: document.getElementById('edit-importe-maximo-subvencionable').value || null   // Campo nuevo
            },
            tipo_proyecto: tipo_proyecto,
            resumen_breve: document.getElementById('edit-resumen').value || null,
            descripcion_detallada: document.getElementById('edit-descripcion').value || null,
            beneficiarios: beneficiarios,
            sectores: sectores,
            requisitos: requisitos,
            gastos_subvencionables: gastos_subvencionables,
            enlaces: {
                url_bdns: urlBdns,
                convocatoria: urlConvocatoria,
                bases_reguladoras: urlBases,  // Campo nuevo
                bases: urlBases,  // Mantener para compatibilidad
                extracto: urlExtracto  // Campo nuevo
            }
        };
    }
    
    // Eliminar
    window.eliminar = function(id, nombre) {
        document.getElementById('del-id').value = id;
        document.getElementById('del-nombre').textContent = nombre;
        new bootstrap.Modal(document.getElementById('modalEliminar')).show();
    };
    
    // Confirmar eliminación
    async function confirmarEliminar() {
        const id = document.getElementById('del-id').value;
        const btn = document.getElementById('btn-eliminar');
        
        btn.disabled = true;
        btn.textContent = 'Eliminando...';
        
        try {
            const response = await fetch(`/api/programa/${id}`, { method: 'DELETE' });
            const data = await response.json();
            
            if (data.success) {
                alert('Eliminado');
                bootstrap.Modal.getInstance(document.getElementById('modalEliminar')).hide();
                buscar();
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            alert('Error al eliminar');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Eliminar';
        }
    }
});
