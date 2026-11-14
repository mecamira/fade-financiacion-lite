/**
 * Ficha de convocatoria (solo administración): prepara un correo para socios.
 *
 * Genera un correo con el estilo de FADE a partir de los datos de la ficha. Los textos se rellenan
 * solos pero se pueden editar, y el resultado se copia con formato (para pegarlo en Outlook o Gmail)
 * o como código HTML. Incluye el enlace a la ficha concreta para fomentar que se consulte la herramienta.
 */
(function () {
    'use strict';

    const boton = document.getElementById('btn-correo');
    if (!boton) return;

    const P = JSON.parse(document.getElementById('datos-programa').textContent);
    const $ = id => document.getElementById(id);

    // ------------------------------------------------------------------ utilidades
    const AZUL = '#0078BF', AZUL_OSC = '#005A91', TEXTO = '#1F2D3A', GRIS = '#5B6B7A';
    const vacio = v => v === null || v === undefined || v === '' || v === 'null' || v === 'nan';
    const arr = v => Array.isArray(v) ? v.filter(x => !vacio(x)) : (vacio(v) ? [] : [v]);
    const num = v => (vacio(v) || isNaN(parseFloat(v))) ? null : parseFloat(v);
    const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    const parrafos = t => esc(t).replace(/\n/g, '<br>');
    const eur = n => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 })
        .format(n).replace(/[  ]/g, ' ');

    function fechaISO(f) {
        const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(f || '');
        return m ? new Date(+m[1], +m[2] - 1, +m[3]) : null;
    }
    // Recorta en el último espacio, para no cortar a mitad de palabra
    const recorta = (t, n) => t.length <= n ? t : t.slice(0, n).replace(/\s+\S*$/, '').replace(/[\s,;:(]+$/, '') + '…';
    const larga = d => d.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
    const sinAnio = d => d.toLocaleDateString('es-ES', { day: 'numeric', month: 'long' });

    const urlFicha = location.origin + '/financiacion/programa/' + encodeURIComponent(P.id);
    const urlLogo = location.origin + '/static/images/fade_logo_marca_blanco.png';
    const URL_ALTA = 'https://fade.es/login/';

    // ------------------------------------------------------------------ textos automáticos
    function medioInferido() {
        const e = P.enlaces || {};
        const enlace = [e.extracto, e.convocatoria, e.url_bdns].filter(x => !vacio(x)).join(' ');
        if (/boe\.es/i.test(enlace)) return 'BOE';
        if (/bopa|sede\.asturias\.es/i.test(enlace)) return 'BOPA';
        return 'OTRO';
    }

    // "RESOLUCIÓN DE 7/5/2026, DE LA AGENCIA…" -> "Resolución de 7/5/2026, de la agencia…"
    function casoFrase(t) {
        const letras = t.replace(/[^A-Za-zÁÉÍÓÚÑáéíóúñ]/g, '');
        const mayus = letras.replace(/[^A-ZÁÉÍÓÚÑ]/g, '').length;
        if (letras.length && mayus / letras.length > 0.7) {
            t = t.toLowerCase();
            t = t.charAt(0).toUpperCase() + t.slice(1);
        }
        return t;
    }

    function parrafoPublicacion() {
        const medio = $('corr-medio').value;
        const f = fechaISO($('corr-fecha').value);
        const nombreMedio = medio === 'OTRO' ? 'diario oficial' : medio;
        const sujeto = f ? `El ${nombreMedio} del ${larga(f)} publicó` : `El ${nombreMedio} de hoy publica`;

        let oficial = (P.nombre_oficial || '').trim();
        if (!oficial) return `${sujeto} la convocatoria «${P.nombre_coloquial || P.nombre || ''}».`;
        oficial = casoFrase(oficial.replace(/^extracto\s+(?:de\s+)?(?:la\s+|el\s+)?/i, ''));
        const primera = oficial.split(/\s+/)[0].toLowerCase().replace(/[^a-záéíóúñ]/g, '');
        const fem = ['resolución', 'orden', 'convocatoria', 'corrección', 'modificación'];
        const masc = ['acuerdo', 'anuncio', 'decreto', 'real', 'extracto'];
        const art = fem.includes(primera) ? 'la ' : (masc.includes(primera) ? 'el ' : '');
        return `${sujeto} el extracto de ${art}${oficial.replace(/\.$/, '')}.`;
    }

    function parrafoDestinatarios() {
        if (!vacio(P.resumen_breve)) return String(P.resumen_breve).trim();
        const b = arr(P.beneficiarios);
        return b.length ? `La convocatoria se dirige a: ${b.join(', ')}.` : '';
    }

    function dotacion() {
        const f = P.financiacion || {};
        const base = num(f.presupuesto_total) ?? num(f.importe_maximo);
        const ampl = arr(P.ampliaciones_credito).reduce((s, a) => s + (num(a.importe) || 0), 0);
        if (base === null) return '';
        return ampl ? `${eur(base + ampl)} (tras ampliar el crédito en ${eur(ampl)})` : eur(base);
    }

    function plazo() {
        const c = P.convocatoria || {};
        const ap = fechaISO(c.fecha_apertura), ci = fechaISO(c.fecha_cierre);
        const hoy = new Date(); hoy.setHours(0, 0, 0, 0);
        let t = '';
        if (ap && ci) t = `Del ${sinAnio(ap)} al ${larga(ci)}`;
        else if (ci) t = `Hasta el ${larga(ci)}`;
        else if (ap) t = `Desde el ${larga(ap)}`;
        if (ci && ci >= hoy && !/cerrad/i.test(c.estado || '')) {
            const dias = Math.round((ci - hoy) / 86400000);
            t += dias === 0 ? ' (hoy es el último día)' : ` (quedan ${dias} día${dias === 1 ? '' : 's'})`;
        }
        return t;
    }

    function estado() {
        const e = (P.convocatoria || {}).estado || '';
        if (!e) return null;
        const l = e.toLowerCase();
        const color = l.includes('cierre próximo') ? ['#8A5A00', '#FFF1CC']
            : l.includes('abierta') ? ['#1B6E3A', '#DDF3E4']
            : (l.includes('próxima') || l.includes('pendiente')) ? ['#005A91', '#DCEEFA']
            : ['#4A5662', '#E8ECEF'];
        return { texto: e, fg: color[0], bg: color[1] };
    }

    function filasDatos() {
        const f = P.financiacion || {};
        const filas = [];
        const org = arr(P.organismo).join(', ');
        if (org) filas.push(['Organismo', org]);
        if (dotacion()) filas.push(['Dotación', dotacion()]);
        if (plazo()) filas.push(['Plazo de solicitud', plazo()]);
        if (!vacio(f.intensidad)) filas.push(['Intensidad de la ayuda', recorta(String(f.intensidad), 170)]);
        const benef = arr(P.beneficiarios);
        if (benef.length) filas.push(['Dirigida a', benef.slice(0, 6).join(', ') + (benef.length > 6 ? '…' : '')]);
        return filas;
    }

    // ------------------------------------------------------------------ construcción del correo
    function leerOpciones() {
        return {
            saludo: $('corr-saludo').value,
            p1: $('corr-p1').value.trim(),
            p2: $('corr-p2').value.trim(),
            nota: $('corr-nota').value.trim(),
            tarjeta: $('corr-tarjeta').checked,
            pdf: $('corr-pdf').checked,
            alta: $('corr-alta').checked,
            firma: $('corr-firma').value.trim()
        };
    }

    function htmlCorreo(o) {
        const p = 'margin:0 0 14px 0;';
        const e = estado();
        const nombre = P.nombre_coloquial || P.nombre || 'Convocatoria';

        const cabecera = `
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${AZUL}" style="background:${AZUL};border-radius:8px 8px 0 0;">
  <tr>
    <td style="padding:16px 22px;"><img src="${urlLogo}" alt="FADE" height="30" style="display:block;height:30px;border:0;"></td>
    <td align="right" style="padding:16px 22px;color:#FFFFFF;font-family:Arial,Helvetica,sans-serif;font-size:13px;letter-spacing:.4px;">Buscador de subvenciones</td>
  </tr>
</table>`;

        const filas = o.tarjeta ? filasDatos().map(([k, v]) => `
      <tr>
        <td valign="top" style="padding:7px 12px 7px 0;color:${GRIS};font-size:13px;white-space:nowrap;width:150px;">${esc(k)}</td>
        <td valign="top" style="padding:7px 0;color:${TEXTO};font-size:14px;font-weight:bold;">${esc(v)}</td>
      </tr>`).join('') : '';

        const tarjeta = o.tarjeta ? `
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 20px 0;border:1px solid #D5E3EE;border-left:4px solid ${AZUL};border-radius:6px;background:#F5FAFE;">
  <tr><td style="padding:16px 18px;">
    <div style="font-size:16px;font-weight:bold;color:${AZUL_OSC};margin:0 0 8px 0;">${esc(nombre)}${e ? ` &nbsp;<span style="display:inline-block;font-size:11px;font-weight:bold;padding:2px 9px;border-radius:10px;background:${e.bg};color:${e.fg};">${esc(e.texto)}</span>` : ''}</div>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">${filas}
    </table>
  </td></tr>
</table>` : '';

        const boton = `
<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 20px 0;">
  <tr><td bgcolor="${AZUL}" style="background:${AZUL};border-radius:6px;">
    <a href="${esc(urlFicha)}" style="display:inline-block;padding:12px 24px;color:#FFFFFF;font-weight:bold;font-size:15px;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">Ver la ficha completa en el Buscador &rarr;</a>
  </td></tr>
</table>`;

        const acceso = [
            o.pdf ? 'Tienes toda la información en el PDF de resumen adjunto.' : '',
            'Y en el Buscador de Subvenciones de FADE encontrarás esta y el resto de convocatorias vigentes, con filtros y comparador.',
            'El acceso al Área Privada de FADE es un beneficio exclusivo para socios.'
        ].filter(Boolean).join(' ');

        const alta = o.alta
            ? `<p style="${p}">¿Todavía no tienes acceso? Puedes darte de alta <a href="${URL_ALTA}" style="color:${AZUL};font-weight:bold;">aquí</a>.</p>` : '';

        return `<div style="font-family:Arial,Helvetica,sans-serif;color:${TEXTO};font-size:15px;line-height:1.55;max-width:640px;">
${cabecera}
<div style="border:1px solid #D5E3EE;border-top:0;border-radius:0 0 8px 8px;padding:22px 24px;">
<p style="${p}">${esc(o.saludo)}</p>
${o.p1 ? `<p style="${p}">${parrafos(o.p1)}</p>` : ''}
${o.p2 ? `<p style="${p}">${parrafos(o.p2)}</p>` : ''}
${o.nota ? `<p style="${p}">${parrafos(o.nota)}</p>` : ''}
${tarjeta}${boton}
<p style="${p}">${esc(acceso)}</p>
${alta}
<p style="margin:18px 0 0 0;">${parrafos(o.firma)}</p>
</div>
<p style="font-size:11px;color:${GRIS};margin:10px 4px 0 4px;">Información orientativa: confirma siempre los requisitos y plazos en las bases oficiales.</p>
</div>`;
    }

    function textoCorreo(o) {
        const datos = o.tarjeta ? filasDatos().map(([k, v]) => `- ${k}: ${v}`).join('\n') : '';
        return [o.saludo, o.p1, o.p2, o.nota, datos, `Ficha completa: ${urlFicha}`,
            [o.pdf ? 'Tienes toda la información en el PDF de resumen adjunto.' : '',
                'En el Buscador de Subvenciones de FADE encontrarás esta y el resto de convocatorias vigentes.',
                'El acceso al Área Privada de FADE es un beneficio exclusivo para socios.'].filter(Boolean).join(' '),
            o.alta ? `¿Todavía no tienes acceso? Date de alta aquí: ${URL_ALTA}` : '', o.firma]
            .filter(Boolean).join('\n\n');
    }

    // ------------------------------------------------------------------ interfaz
    let p1Editado = false, p2Editado = false;

    function refrescar() {
        $('corr-preview').innerHTML = htmlCorreo(leerOpciones());
    }

    function regenerarAutomaticos() {
        if (!p1Editado) $('corr-p1').value = parrafoPublicacion();
        if (!p2Editado) $('corr-p2').value = parrafoDestinatarios();
    }

    function abrir() {
        $('corr-medio').value = medioInferido();
        $('corr-fecha').value = '';
        $('corr-saludo').value = new Date().getHours() < 14 ? 'Buenos días:' : 'Buenas tardes:';
        if (!$('corr-firma').value) $('corr-firma').value = 'Un saludo,';
        p1Editado = p2Editado = false;
        regenerarAutomaticos();
        refrescar();
        $('corr-estado').textContent = '';
        bootstrap.Modal.getOrCreateInstance($('modalCorreo')).show();
    }

    function aviso(texto, ok) {
        const el = $('corr-estado');
        el.textContent = texto;
        el.className = 'small ms-2 ' + (ok ? 'text-success' : 'text-danger');
    }

    async function copiarConFormato() {
        const o = leerOpciones(), html = htmlCorreo(o), texto = textoCorreo(o);
        try {
            if (navigator.clipboard && window.ClipboardItem) {
                await navigator.clipboard.write([new ClipboardItem({
                    'text/html': new Blob([html], { type: 'text/html' }),
                    'text/plain': new Blob([texto], { type: 'text/plain' })
                })]);
            } else {
                // Respaldo: seleccionar la vista previa y copiar
                const rango = document.createRange();
                rango.selectNodeContents($('corr-preview'));
                const sel = window.getSelection();
                sel.removeAllRanges(); sel.addRange(rango);
                document.execCommand('copy');
                sel.removeAllRanges();
            }
            aviso('Copiado. Pégalo en el correo (Ctrl+V).', true);
        } catch (e) {
            aviso('No se pudo copiar automáticamente. Selecciona la vista previa y copia con Ctrl+C.', false);
        }
    }

    async function copiarCodigo() {
        try {
            await navigator.clipboard.writeText(htmlCorreo(leerOpciones()));
            aviso('Código HTML copiado.', true);
        } catch (e) {
            aviso('No se pudo copiar el código.', false);
        }
    }

    boton.addEventListener('click', abrir);
    ['corr-medio', 'corr-fecha'].forEach(id => $(id).addEventListener('input', () => { regenerarAutomaticos(); refrescar(); }));
    $('corr-p1').addEventListener('input', () => { p1Editado = true; refrescar(); });
    $('corr-p2').addEventListener('input', () => { p2Editado = true; refrescar(); });
    ['corr-saludo', 'corr-nota', 'corr-tarjeta', 'corr-pdf', 'corr-alta', 'corr-firma']
        .forEach(id => $(id).addEventListener('input', refrescar));
    $('corr-restaurar').addEventListener('click', () => { p1Editado = p2Editado = false; regenerarAutomaticos(); refrescar(); });
    $('corr-copiar').addEventListener('click', copiarConFormato);
    $('corr-copiar-html').addEventListener('click', copiarCodigo);
})();
