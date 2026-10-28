/**
 * Ficha de convocatoria:
 *  - Exportar la ficha a PDF (jsPDF + autotable, todo en el navegador)
 *  - Registro manual (solo administración) de ampliaciones de crédito y resoluciones
 */
(function () {
    'use strict';

    const ctx = document.getElementById('ficha-ctx');
    const P = JSON.parse(document.getElementById('datos-programa').textContent);
    const ID = ctx.dataset.id;
    const ES_ADMIN = ctx.dataset.admin === '1';

    // ------------------------------------------------------------------ utilidades
    const vacio = v => v === null || v === undefined || v === '' || v === 'null' || v === 'nan';
    const arr = v => Array.isArray(v) ? v.filter(x => !vacio(x)) : (vacio(v) ? [] : [v]);
    const num = v => (vacio(v) || isNaN(parseFloat(v))) ? null : parseFloat(v);
    const eur = n => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' })
        .format(n).replace(/[  ]/g, ' ');
    const fecha = f => {
        const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(f || '');
        return m ? `${m[3]}/${m[2]}/${m[1]}` : (vacio(f) ? '' : String(f));
    };

    // ------------------------------------------------------------------ PDF
    function exportarPDF() {
        if (!window.jspdf || !window.jspdf.jsPDF) {
            alert('No se pudo cargar el generador de PDF. Comprueba tu conexión e inténtalo de nuevo.');
            return;
        }
        const doc = new window.jspdf.jsPDF({ unit: 'mm', format: 'a4' });
        const W = 210, H = 297, M = 16, AN = W - 2 * M;
        const AZUL = [0, 94, 163], TEXTO = [40, 50, 60], GRIS = [100, 110, 120];
        let y = 0;

        const hueco = n => { if (y + n > H - 18) { doc.addPage(); y = 20; } };
        const fuente = (tam, negrita, color) => {
            doc.setFont('helvetica', negrita ? 'bold' : 'normal'); doc.setFontSize(tam); doc.setTextColor(...color);
        };
        const seccion = t => {
            hueco(16); y += 3; fuente(12, true, AZUL); doc.text(t, M, y);
            doc.setDrawColor(...AZUL); doc.setLineWidth(0.3); doc.line(M, y + 1.6, W - M, y + 1.6); y += 7;
        };
        const parrafo = (t, tam = 10) => {
            fuente(tam, false, TEXTO);
            doc.splitTextToSize(String(t), AN).forEach(l => { hueco(5); doc.text(l, M, y); y += 4.7; });
            y += 1.5;
        };
        const lista = items => {
            fuente(10, false, TEXTO);
            items.forEach(it => {
                doc.splitTextToSize(String(it), AN - 6).forEach((l, i) => {
                    hueco(5); if (i === 0) doc.text('•', M + 1, y); doc.text(l, M + 6, y); y += 4.7;
                });
                y += 0.8;
            });
            y += 1.5;
        };
        const tabla = (cabecera, filas, opciones) => {
            hueco(20);
            doc.autoTable(Object.assign({
                startY: y, head: cabecera ? [cabecera] : undefined, body: filas,
                theme: cabecera ? 'striped' : 'plain',
                styles: { fontSize: 9, cellPadding: 1.8, overflow: 'linebreak', valign: 'top', textColor: TEXTO },
                headStyles: { fillColor: AZUL, textColor: 255 },
                margin: { left: M, right: M, bottom: 18 }
            }, opciones || {}));
            y = doc.lastAutoTable.finalY + 4;
        };

        // --- cabecera
        const nombre = P.nombre_coloquial || P.nombre || 'Convocatoria';
        fuente(17, true, [255, 255, 255]);
        const lTitulo = doc.splitTextToSize(nombre, AN);
        const organismo = arr(P.organismo).join(', ');
        const alto = 14 + lTitulo.length * 7.2 + (P.nombre_oficial ? 6 : 0) + (organismo ? 8 : 0);
        doc.setFillColor(...AZUL); doc.rect(0, 0, W, alto, 'F');
        y = 15; lTitulo.forEach(l => { doc.text(l, M, y); y += 7.2; });
        if (P.nombre_oficial) {
            fuente(9, false, [214, 235, 250]);
            let of = doc.splitTextToSize(P.nombre_oficial, AN);
            doc.text(of.length > 1 ? of[0].replace(/\s*\S*$/, '') + '…' : of[0], M, y - 0.5); y += 6;
        }
        if (organismo) { fuente(11, true, [255, 255, 255]); doc.text(doc.splitTextToSize(organismo, AN)[0], M, y); }
        y = alto + 8;

        // --- resumen y descripción
        if (!vacio(P.resumen_breve)) { seccion('Resumen'); parrafo(P.resumen_breve, 10.5); }
        if (!vacio(P.descripcion_detallada)) { seccion('Descripción detallada'); parrafo(P.descripcion_detallada); }
        if (!vacio(P.comentarios)) { seccion('Comentarios'); parrafo(P.comentarios); }

        // --- datos clave
        const f = P.financiacion || {}, c = P.convocatoria || {};
        const ampl = arr(P.ampliaciones_credito);
        const base = num(f.presupuesto_total) ?? num(f.importe_maximo);
        const totalAmpl = ampl.reduce((s, a) => s + (num(a.importe) || 0), 0);
        const filas = [];
        const dato = (k, v) => { if (!vacio(v) && v !== '') filas.push([k, v]); };
        dato('Estado', c.estado);
        dato('Tipo de ayuda', arr(P.tipo_ayuda).join(', '));
        dato('Ámbito', P.ambito);
        dato('Código BDNS', P.codigo_bdns);
        dato('Fecha de apertura', fecha(c.fecha_apertura));
        dato('Fecha de cierre', fecha(c.fecha_cierre));
        dato('Publicada en la BDNS', fecha(P.fecha_publicacion_bdns));
        if (base !== null) dato(totalAmpl ? 'Dotación inicial' : 'Dotación total', eur(base));
        if (totalAmpl) {
            dato('Ampliaciones de crédito', '+ ' + eur(totalAmpl));
            if (base !== null) dato('Dotación actual', eur(base + totalAmpl));
        }
        dato('Intensidad de la ayuda', f.intensidad);
        if (num(f.importe_minimo_subvencionable) !== null) dato('Importe mínimo subvencionable', eur(num(f.importe_minimo_subvencionable)));
        if (num(f.importe_maximo_subvencionable) !== null) dato('Importe máximo subvencionable', eur(num(f.importe_maximo_subvencionable)));
        if (num(f.presupuesto_minimo) !== null) dato('Presupuesto mínimo del proyecto', eur(num(f.presupuesto_minimo)));
        if (num(f.presupuesto_maximo) !== null) dato('Presupuesto máximo del proyecto', eur(num(f.presupuesto_maximo)));
        if (filas.length) {
            seccion('Datos clave');
            tabla(null, filas, { columnStyles: { 0: { fontStyle: 'bold', cellWidth: 55, textColor: GRIS } } });
        }

        // --- a quién va dirigida
        const grupos = [['Beneficiarios', P.beneficiarios], ['Sectores', P.sectores],
            ['Tipo de proyecto', P.tipo_proyecto], ['Fondos europeos', P.fondos_europeos || P.origen_fondos]];
        const filasGrupos = grupos.map(([k, v]) => [k, arr(v).join(', ')]).filter(r => r[1]);
        if (filasGrupos.length) {
            seccion('A quién va dirigida');
            tabla(null, filasGrupos, { columnStyles: { 0: { fontStyle: 'bold', cellWidth: 55, textColor: GRIS } } });
        }

        // --- requisitos y gastos
        if (arr(P.requisitos).length) { seccion('Requisitos'); lista(arr(P.requisitos)); }
        if (arr(P.gastos_subvencionables).length) { seccion('Gastos subvencionables'); lista(arr(P.gastos_subvencionables)); }

        // --- ampliaciones y resoluciones (registro manual)
        if (ampl.length) {
            seccion('Ampliaciones de crédito presupuestario');
            tabla(['Fecha', 'Importe', 'Observaciones'],
                ampl.map(a => [fecha(a.fecha), '+ ' + eur(num(a.importe) || 0), a.nota || '']),
                { columnStyles: { 0: { cellWidth: 26 }, 1: { cellWidth: 38, halign: 'right' } } });
        }
        const resos = arr(P.resoluciones_manuales);
        if (resos.length) {
            seccion('Resoluciones');
            tabla(['Tipo', 'Fecha', 'Importe concedido', 'Beneficiarios', 'Observaciones'],
                resos.map(r => [r.tipo ? r.tipo.charAt(0).toUpperCase() + r.tipo.slice(1) : '', fecha(r.fecha),
                    num(r.importe_concedido) !== null ? eur(num(r.importe_concedido)) : '',
                    r.num_beneficiarios ?? '', r.nota || '']),
                { columnStyles: { 0: { cellWidth: 24 }, 1: { cellWidth: 24 }, 2: { cellWidth: 34, halign: 'right' }, 3: { cellWidth: 26, halign: 'center' } } });
        }

        // --- concesiones detectadas en la BDNS (resumen)
        const conc = arr(P.concesiones);
        if (P.resuelta && conc.length) {
            const totalAdj = conc.reduce((s, x) => s + (num(x.importe) || 0), 0);
            seccion('Concesiones registradas en la BDNS');
            parrafo(`${P.total_concesiones || conc.length} concesiones` + (totalAdj ? ` · total adjudicado: ${eur(totalAdj)}` : '') +
                '. La lista completa está disponible en la BDNS.');
        }

        // --- enlaces
        const e = P.enlaces || {};
        const enlaces = [['Página BDNS', e.url_bdns], ['Extracto oficial', e.extracto],
            ['Convocatoria (resolución)', e.convocatoria], ['Bases reguladoras', e.bases_reguladoras || e.bases]]
            .filter(([, u]) => !vacio(u));
        if (enlaces.length) {
            seccion('Enlaces');
            enlaces.forEach(([k, u]) => {
                hueco(6); fuente(9.5, true, GRIS); doc.text(k + ':', M, y);
                fuente(9, false, AZUL);
                const l = doc.splitTextToSize(u, AN - 46);
                doc.textWithLink(l[0], M + 46, y, { url: u }); y += 5;
                l.slice(1).forEach(t => { hueco(5); doc.text(t, M + 46, y); y += 4.5; });
            });
        }

        // --- pie de cada página
        const hoy = new Date().toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
        const n = doc.getNumberOfPages();
        for (let i = 1; i <= n; i++) {
            doc.setPage(i); fuente(8, false, [120, 130, 140]);
            doc.text('Información orientativa: confirma siempre requisitos y plazos en las bases oficiales.', M, H - 11);
            doc.text(`Programas de Financiación · FADE · generado el ${hoy}`, M, H - 7);
            doc.text(`${i} / ${n}`, W - M, H - 7, { align: 'right' });
        }

        const slug = nombre.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^A-Za-z0-9]+/g, '_')
            .replace(/^_|_$/g, '').slice(0, 60);
        doc.save(`ficha_${slug || 'convocatoria'}.pdf`);
    }

    const btnPdf = document.getElementById('btn-export-pdf');
    if (btnPdf) btnPdf.addEventListener('click', exportarPDF);

    // ------------------------------------------------------------------ registro manual (admin)
    if (!ES_ADMIN) return;

    let A = JSON.parse(JSON.stringify(arr(P.ampliaciones_credito)));
    let R = JSON.parse(JSON.stringify(arr(P.resoluciones_manuales)));
    const $ = id => document.getElementById(id);
    const modal = id => bootstrap.Modal.getOrCreateInstance($(id));

    // Admite "12.500,50", "12500,5", "12500.5" o "12.500" (miles)
    function importe(txt) {
        let t = String(txt || '').replace(/[€\s]/g, '');
        if (t === '') return '';
        if (t.includes(',') || /^\d{1,3}(\.\d{3})+$/.test(t)) t = t.replace(/\./g, '').replace(',', '.');
        return t;
    }

    async function guardar(msgEl) {
        try {
            const r = await fetch(`/api/programa/${encodeURIComponent(ID)}/datos-manuales`, {
                method: 'PUT', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ampliaciones_credito: A, resoluciones_manuales: R })
            });
            const d = await r.json().catch(() => ({}));
            if (!r.ok || !d.success) throw new Error(d.error || 'No se pudo guardar');
            location.reload();
        } catch (e) {
            if (msgEl) { msgEl.textContent = e.message; msgEl.classList.remove('d-none'); } else { alert(e.message); }
            return false;
        }
    }

    // --- ampliaciones
    function abrirAmpl(id) {
        const a = A.find(x => x.id === id) || {};
        $('ampl-id').value = a.id || '';
        $('ampl-fecha').value = a.fecha || '';
        $('ampl-importe').value = a.importe ?? '';
        $('ampl-nota').value = a.nota || '';
        $('ampl-enlace').value = a.enlace || '';
        $('ampl-error').classList.add('d-none');
        $('ampl-titulo').textContent = id ? 'Editar ampliación de crédito' : 'Nueva ampliación de crédito';
        modal('modalAmpl').show();
    }
    $('btn-add-ampl').addEventListener('click', () => abrirAmpl(''));
    $('btn-guardar-ampl').addEventListener('click', async () => {
        const id = $('ampl-id').value;
        const item = { id, fecha: $('ampl-fecha').value, importe: importe($('ampl-importe').value),
            nota: $('ampl-nota').value, enlace: $('ampl-enlace').value };
        if (!item.fecha || !item.importe) {
            $('ampl-error').textContent = 'Indica la fecha y el importe de la ampliación.';
            $('ampl-error').classList.remove('d-none'); return;
        }
        const i = A.findIndex(x => x.id === id);
        if (i >= 0) A[i] = item; else A.push(item);
        if (await guardar($('ampl-error')) === false) { if (i < 0) A.pop(); }
    });

    // --- resoluciones
    function abrirReso(id) {
        const r = R.find(x => x.id === id) || {};
        $('reso-id').value = r.id || '';
        $('reso-tipo').value = r.tipo || 'definitiva';
        $('reso-fecha').value = r.fecha || '';
        $('reso-importe').value = r.importe_concedido ?? '';
        $('reso-benef').value = r.num_beneficiarios ?? '';
        $('reso-nota').value = r.nota || '';
        $('reso-enlace').value = r.enlace || '';
        $('reso-error').classList.add('d-none');
        $('reso-titulo').textContent = id ? 'Editar resolución' : 'Nueva resolución';
        modal('modalReso').show();
    }
    $('btn-add-reso').addEventListener('click', () => abrirReso(''));
    $('btn-guardar-reso').addEventListener('click', async () => {
        const id = $('reso-id').value;
        const item = { id, tipo: $('reso-tipo').value, fecha: $('reso-fecha').value,
            importe_concedido: importe($('reso-importe').value), num_beneficiarios: $('reso-benef').value,
            nota: $('reso-nota').value, enlace: $('reso-enlace').value };
        if (!item.fecha) {
            $('reso-error').textContent = 'Indica la fecha de la resolución.';
            $('reso-error').classList.remove('d-none'); return;
        }
        const i = R.findIndex(x => x.id === id);
        if (i >= 0) R[i] = item; else R.push(item);
        if (await guardar($('reso-error')) === false) { if (i < 0) R.pop(); }
    });

    // --- editar / borrar desde las tablas
    document.addEventListener('click', ev => {
        const b = ev.target.closest('[data-accion]');
        if (!b) return;
        const { accion, id } = b.dataset;
        if (accion === 'editar-ampl') abrirAmpl(id);
        else if (accion === 'editar-reso') abrirReso(id);
        else if (accion === 'borrar-ampl' && confirm('¿Eliminar esta ampliación de crédito?')) {
            A = A.filter(x => x.id !== id); guardar();
        } else if (accion === 'borrar-reso' && confirm('¿Eliminar esta resolución?')) {
            R = R.filter(x => x.id !== id); guardar();
        }
    });
})();
