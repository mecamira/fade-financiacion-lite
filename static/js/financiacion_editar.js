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
        
        tbody.innerHTML = programas.map(p => `
            <tr>
                <td><strong>${p.nombre || '-'}</strong></td>
                <td>${p.organismo || '-'}</td>
                <td>${p.convocatoria?.estado ? `<span class="badge bg-${getBadge(p.convocatoria.estado)}">${p.convocatoria.estado}</span>` : '-'}</td>
                <td>${p.codigo_bdns || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="editar('${p.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="eliminar('${p.id}', '${(p.nombre || '').replace(/'/g, "\\'")}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }
    
    function getBadge(estado) {
        if (estado?.includes('Abierta')) return 'success';
        if (estado?.includes('Pendiente')) return 'warning';
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
            const response = await fetch(`/api/programa/${id}`);
            const data = await response.json();
            
            if (data.success) {
                cargarDatos(data.programa);
                document.getElementById('modalTitle').textContent = 'Editar Convocatoria';
                new bootstrap.Modal(document.getElementById('modalEditar')).show();
            }
        } catch (error) {
            alert('Error al cargar');
        }
    };
    
    // Cargar datos en formulario
    function cargarDatos(p) {
        document.getElementById('edit-id').value = p.id || '';
        document.getElementById('edit-nombre').value = p.nombre || '';
        document.getElementById('edit-bdns').value = p.codigo_bdns || '';
        document.getElementById('edit-organismo').value = p.organismo || '';
        document.getElementById('edit-tipo').value = p.tipo_ayuda || '';
        document.getElementById('edit-ambito').value = p.ambito || '';
        document.getElementById('edit-estado').value = p.convocatoria?.estado || 'Abierta';
        document.getElementById('edit-fecha-apertura').value = p.convocatoria?.fecha_apertura || '';
        document.getElementById('edit-fecha-cierre').value = p.convocatoria?.fecha_cierre || '';
        document.getElementById('edit-resumen').value = p.resumen_breve || '';
        document.getElementById('edit-descripcion').value = p.descripcion_detallada || '';
        document.getElementById('edit-beneficiarios').value = (p.beneficiarios || []).join('\n');
        document.getElementById('edit-sectores').value = (p.sectores || []).join('\n');
        document.getElementById('edit-url-bdns').value = p.enlaces?.url_bdns || '';
        document.getElementById('edit-url-convocatoria').value = p.enlaces?.convocatoria || '';
        document.getElementById('edit-url-bases').value = p.enlaces?.bases || '';
    }
    
    // Limpiar formulario
    function limpiarFormulario() {
        ['edit-id', 'edit-nombre', 'edit-bdns', 'edit-organismo', 'edit-tipo', 'edit-ambito',
         'edit-fecha-apertura', 'edit-fecha-cierre', 'edit-resumen', 'edit-descripcion',
         'edit-beneficiarios', 'edit-sectores', 'edit-url-bdns', 'edit-url-convocatoria', 'edit-url-bases'].forEach(id => {
            document.getElementById(id).value = '';
        });
        document.getElementById('edit-estado').value = 'Abierta';
    }
    
    // Guardar
    async function guardar() {
        const id = document.getElementById('edit-id').value;
        const datos = obtenerDatos();
        
        if (!datos.nombre || !datos.organismo || !datos.tipo_ayuda) {
            alert('Completa los campos obligatorios');
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
        
        // Obtener URLs
        const urlBdns = document.getElementById('edit-url-bdns').value.trim() || null;
        const urlConvocatoria = document.getElementById('edit-url-convocatoria').value.trim() || null;
        const urlBases = document.getElementById('edit-url-bases').value.trim() || null;
        
        return {
            nombre: document.getElementById('edit-nombre').value,
            codigo_bdns: document.getElementById('edit-bdns').value || null,
            organismo: document.getElementById('edit-organismo').value,
            tipo_ayuda: document.getElementById('edit-tipo').value,
            ambito: document.getElementById('edit-ambito').value || null,
            convocatoria: {
                estado: document.getElementById('edit-estado').value,
                fecha_apertura: document.getElementById('edit-fecha-apertura').value || null,
                fecha_cierre: document.getElementById('edit-fecha-cierre').value || null
            },
            financiacion: {},
            tipo_proyecto: null,
            resumen_breve: document.getElementById('edit-resumen').value || null,
            descripcion_detallada: document.getElementById('edit-descripcion').value || null,
            beneficiarios: beneficiarios,
            sectores: sectores,
            requisitos: [],
            tags: [],
            enlaces: {
                url_bdns: urlBdns,
                convocatoria: urlConvocatoria,
                bases: urlBases
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
