/* ═══════════════════════════════════════════════════════
   MarketPulse Dashboard — app.js
   Full logic: CSV parsing, filtering, charts, tables
═══════════════════════════════════════════════════════ */

Chart.register(ChartDataLabels);

// ═══════════════════════════════════════════════════════
// COLUMN NAME MAP
// Aliases normalized: accents removed, lowercase, spaces→_
// ═══════════════════════════════════════════════════════
const COL_ALIASES = {
  // Primer alias = nombre EXACTO de la columna en el CSV del usuario
  rif:          ['RIF_Cedula','rif_cedula','rif','cedula','codigo','code'],
  nombre:       ['Razon_Social','razon_social','razon social','nombre','description','cliente'],
  telefono:     ['Telefono','telefono','phone','tlf','telf','celular'],
  estado:       ['Estado','estado','province','provincia'],
  vendedor:     ['Ultimo_Vendedor','ultimo_vendedor','vendedor','seller','nombre_vendedor'],
  ultimaCompra: ['Ultima_Compra','ultima_compra','ultima compra','last_purchase','fecha'],
  dias:         ['Dias_Sin_Comprar','dias_sin_comprar','dias sin comprar','dias','days'],
  nivel:        ['Nivel_Inactividad','nivel_inactividad','nivel inactividad','nivel','inactividad'],
  unidades:     ['Total_Unidades_Año','Total_Unidades_Ano','total_unidades_ano','total_unidades','unidades','cantidad'],
  facturas:     ['Total_Facturas_Año','Total_Facturas_Ano','total_facturas_ano','total_facturas','facturas'],
  totalBs:      ['Total_Facturado_Bs_Año','Total_Facturado_Bs_Ano','total_facturado_bs_ano','total_facturado_bs','total_bs','monto'],
};

// Mapa resuelto tras leer el CSV { field -> realColumnName }
let colMap = {};

// ═══════════════════════════════════
// STATE
// ═══════════════════════════════════
let rawData      = [];
let filteredData = [];
let charts       = {};
let currentPage  = 1;
const PAGE_SIZE  = 30;

// ═══════════════════════════════════════════════════════
// NORMALIZACIÓN DE TEXTO
// Quita tildes, trim, minúsculas, espacios → guión_bajo
// ═══════════════════════════════════════════════════════
function norm(s) {
  return String(s)
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')   // quita tildes
    .replace(/[^a-z0-9]+/g, '_')       // caracteres no alfanuméricos → _
    .replace(/^_+|_+$/g, '');          // trim guiones extremos
}

// ═══════════════════════════════════════════════════════
// CONSTRUIR MAPA DE COLUMNAS
// Toma los headers reales del CSV y los cruza con aliases
// ═══════════════════════════════════════════════════════
function buildColMap(headers) {
  colMap = {};
  const normHeaders = headers.map(h => ({ real: h, n: norm(h) }));

  for (const [field, aliases] of Object.entries(COL_ALIASES)) {
    for (const alias of aliases) {
      const na = norm(alias);
      const found = normHeaders.find(h => h.n === na);
      if (found) {
        colMap[field] = found.real;
        break;
      }
    }
    // Si no encontró por alias exacto, intenta coincidencia parcial
    if (!colMap[field]) {
      for (const alias of aliases) {
        const na = norm(alias);
        const found = normHeaders.find(h => h.n.includes(na) || na.includes(h.n));
        if (found) { colMap[field] = found.real; break; }
      }
    }
  }

  // Diagnóstico en consola
  console.table(
    Object.entries(COL_ALIASES).map(([f]) => ({
      Campo: f,
      'Columna CSV detectada': colMap[f] || '⚠️ NO ENCONTRADA',
    }))
  );

  return colMap;
}

// Obtiene el valor de un campo usando el mapa resuelto
function getField(row, field) {
  const col = colMap[field];
  if (!col) return '';
  const val = row[col];
  return val === undefined || val === null ? '' : val;
}

// ─────────────────────────────────────
// MODAL DE DIAGNÓSTICO DE COLUMNAS
// ─────────────────────────────────────
function showColDiagModal(headers) {
  // Elimina modal previo si existe
  const prev = document.getElementById('diag-modal');
  if (prev) prev.remove();

  const mapped   = Object.entries(COL_ALIASES).map(([f]) => ({ field: f, col: colMap[f] || null }));
  const missing  = mapped.filter(x => !x.col);
  const ok       = mapped.filter(x => x.col);

  const fieldLabels = {
    rif:'RIF / Cédula', nombre:'Razón Social', telefono:'Teléfono',
    estado:'Estado', vendedor:'Vendedor', ultimaCompra:'Última Compra',
    dias:'Días Sin Comprar', nivel:'Nivel Inactividad',
    unidades:'Unidades Año', facturas:'Facturas Año', totalBs:'Total Bs Año'
  };

  const modal = document.createElement('div');
  modal.id = 'diag-modal';
  modal.style.cssText = `
    position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.75);
    display:flex;align-items:center;justify-content:center;padding:20px;
    backdrop-filter:blur(8px);
  `;

  modal.innerHTML = `
    <div style="background:#141828;border:1px solid rgba(255,255,255,.12);border-radius:14px;
                padding:28px 32px;max-width:700px;width:100%;max-height:85vh;overflow-y:auto;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">
        <h2 style="font-size:1.1rem;font-weight:800;color:#e2e8f0">🔍 Diagnóstico de columnas CSV</h2>
        <button id="close-diag" style="background:none;border:none;color:#8892a4;font-size:1.4rem;cursor:pointer">✕</button>
      </div>

      <p style="color:#8892a4;font-size:.83rem;margin-bottom:18px">
        El CSV tiene <strong style="color:#00e5ff">${headers.length} columnas</strong>.
        Se detectaron <strong style="color:#39ff8f">${ok.length}</strong> campos correctamente
        y <strong style="color:#ff4d6a">${missing.length}</strong> no pudieron mapearse automáticamente.
      </p>

      <p style="color:#8892a4;font-size:.8rem;margin-bottom:10px">📋 Columnas reales en tu CSV:</p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px">
        ${headers.map(h => `<code style="background:#0f1220;padding:4px 10px;border-radius:6px;
          font-size:.75rem;color:#b57bff;border:1px solid rgba(181,123,255,.2)">${h}</code>`).join('')}
      </div>

      <table style="width:100%;border-collapse:collapse;font-size:.8rem">
        <thead>
          <tr style="border-bottom:1px solid rgba(255,255,255,.07)">
            <th style="padding:8px 10px;text-align:left;color:#8892a4;font-size:.7rem;text-transform:uppercase">Campo del dashboard</th>
            <th style="padding:8px 10px;text-align:left;color:#8892a4;font-size:.7rem;text-transform:uppercase">Columna CSV detectada</th>
            <th style="padding:8px 10px;text-align:left;color:#8892a4;font-size:.7rem;text-transform:uppercase">Estado</th>
          </tr>
        </thead>
        <tbody>
          ${mapped.map(({field, col}) => `
            <tr style="border-bottom:1px solid rgba(255,255,255,.04)">
              <td style="padding:8px 10px;color:#e2e8f0">${fieldLabels[field] || field}</td>
              <td style="padding:8px 10px">
                <code style="color:${col ? '#00e5ff' : '#ff4d6a'};font-size:.78rem">${col || '—'}</code>
              </td>
              <td style="padding:8px 10px">
                ${col
                  ? '<span style="color:#39ff8f;font-size:.75rem;font-weight:700">✓ OK</span>'
                  : '<span style="color:#ff4d6a;font-size:.75rem;font-weight:700">✗ No encontrado</span>'}
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>

      ${missing.length > 0 ? `
        <div style="margin-top:18px;background:rgba(255,77,106,.08);border:1px solid rgba(255,77,106,.2);
                    border-radius:8px;padding:14px 16px;font-size:.8rem;color:#ff4d6a">
          <strong>⚠️ Campos no encontrados:</strong> ${missing.map(x => fieldLabels[x.field]).join(', ')}.<br/>
          Verifica que los nombres de columnas en tu CSV coincidan (pueden tener tildes o espacios distintos).
        </div>
      ` : `
        <div style="margin-top:18px;background:rgba(57,255,143,.08);border:1px solid rgba(57,255,143,.2);
                    border-radius:8px;padding:14px 16px;font-size:.8rem;color:#39ff8f">
          ✅ Todos los campos fueron detectados correctamente.
        </div>
      `}

      <div style="margin-top:20px;display:flex;gap:10px;justify-content:flex-end">
        <button id="close-diag-btn" style="padding:9px 24px;background:#1a1f35;border:1px solid rgba(255,255,255,.12);
          color:#e2e8f0;border-radius:8px;font-size:.85rem;font-weight:600;cursor:pointer">Cerrar</button>
        <button id="proceed-diag-btn" style="padding:9px 24px;background:linear-gradient(135deg,#00e5ff,#00b4cc);
          border:none;color:#000;border-radius:8px;font-size:.85rem;font-weight:700;cursor:pointer">Continuar de todas formas</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  document.getElementById('close-diag').onclick = () => modal.remove();
  document.getElementById('close-diag-btn').onclick = () => modal.remove();
  document.getElementById('proceed-diag-btn').onclick = () => { modal.remove(); initDashboard(); };
}

// ─────────────────────────────────────
// UTILS NUMÉRICOS Y FORMATO
// ─────────────────────────────────────
function num(v) {
  if (v === null || v === undefined || v === '') return 0;
  return parseFloat(String(v).replace(/\./g, '').replace(',', '.')) ||
         parseFloat(String(v).replace(',', '.')) || 0;
}
function fmtNum(n) { return new Intl.NumberFormat('es-VE', { maximumFractionDigits: 2 }).format(n); }
function fmtBs(n)  { return 'Bs ' + new Intl.NumberFormat('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n); }

function toast(msg, type = 'info') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = `toast show ${type}`;
  setTimeout(() => { el.className = 'toast'; }, 4500);
}

function showSection(id) {
  document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
  document.getElementById(`section-${id}`).classList.remove('hidden');
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(`nav-${id}`).classList.add('active');
  const titles = { overview:'Resumen General', estados:'Análisis por Estado', inactivos:'Clientes Inactivos', tabla:'Tabla Completa' };
  document.getElementById('section-title').textContent = titles[id] || '';
}

// ═══════════════════════════════════
// CSV PARSING
// ═══════════════════════════════════
function parseCSV(file) {
  // Intentamos parsear con auto-detección de separador
  // PapaParse maneja comas, puntos y coma y tabulaciones automáticamente
  function doParse(text) {
    Papa.parse(text, {
      header: true,
      delimiter: '',          // '' = PapaParse detecta solo el separador
      quoteChar: '"',
      escapeChar: '"',
      skipEmptyLines: true,
      transformHeader: h => h.trim().replace(/^"/, '').replace(/"$/, ''), // quita comillas del header
      complete: (results) => {
        if (!results.data || results.data.length === 0) {
          toast('⚠️ El archivo está vacío o no se pudo leer.', 'error');
          return;
        }

        // Verificar que no sea una sola columna (fallo de detección)
        const fields = results.meta.fields || [];
        if (fields.length <= 1 && fields[0] && fields[0].includes(',')) {
          // PapaParse falló con auto-detect → forzar coma
          Papa.parse(text, {
            header: true,
            delimiter: ',',
            quoteChar: '"',
            skipEmptyLines: true,
            transformHeader: h => h.trim().replace(/^"|"$/g, ''),
            complete: (r2) => processResults(r2),
            error: () => toast('❌ Error al leer el CSV.', 'error'),
          });
          return;
        }

        processResults(results);
      },
      error: () => toast('❌ Error al leer el CSV.', 'error'),
    });
  }

  function processResults(results) {
    if (!results.data || results.data.length === 0) {
      toast('⚠️ El archivo está vacío.', 'error');
      return;
    }
    rawData = results.data;
    const headers = (results.meta.fields || Object.keys(rawData[0]))
      .map(h => h.trim().replace(/^"|"$/g, '')); // limpia posibles comillas residuales

    // Reconstruir rawData con headers limpios
    if (results.meta.fields) {
      const cleanFields = results.meta.fields.map(h => h.trim().replace(/^"|"$/g, ''));
      rawData = rawData.map(row => {
        const clean = {};
        results.meta.fields.forEach((orig, i) => { clean[cleanFields[i]] = row[orig]; });
        return clean;
      });
    }

    buildColMap(headers);

    const missing = Object.keys(COL_ALIASES).filter(f => !colMap[f]).length;

    if (missing > 0) {
      showColDiagModal(headers);
      toast(`🔍 ${rawData.length} filas cargadas. Revisa el diagnóstico de columnas.`, 'error');
    } else {
      initDashboard();
      toast(`✅ ${rawData.length} clientes cargados correctamente.`, 'success');
    }
  }

  const reader = new FileReader();
  reader.onload = (e) => doParse(e.target.result);
  reader.onerror = () => {
    // Si UTF-8 falla, reintentar con windows-1252
    const r2 = new FileReader();
    r2.onload = (e) => doParse(e.target.result);
    r2.readAsText(file, 'windows-1252');
  };
  reader.readAsText(file, 'UTF-8');
}

// ═══════════════════════════════════
// INIT DASHBOARD
// ═══════════════════════════════════
function initDashboard() {
  document.getElementById('upload-prompt').style.display = 'none';
  document.getElementById('dashboard-content').style.display = 'flex';

  populateFilters();
  applyFilters();
  updateDate();
}

function updateDate() {
  const d = new Date();
  document.getElementById('sidebar-date').textContent =
    d.toLocaleDateString('es-VE', { day:'2-digit', month:'long', year:'numeric' });
}

// ═══════════════════════════════════
// FILTERS
// ═══════════════════════════════════
function populateFilters() {
  const vendedores = [...new Set(rawData.map(r => getField(r,'vendedor')).filter(Boolean))].sort();
  const estados    = [...new Set(rawData.map(r => getField(r,'estado')).filter(Boolean))].sort();

  const selV = document.getElementById('filter-vendedor');
  const selE = document.getElementById('filter-estado');
  selV.innerHTML = '<option value="">Todos los vendedores</option>' +
    vendedores.map(v => `<option value="${v}">${v}</option>`).join('');
  selE.innerHTML = '<option value="">Todos los estados</option>' +
    estados.map(e => `<option value="${e}">${e}</option>`).join('');
}

function applyFilters() {
  const vendedor    = document.getElementById('filter-vendedor').value;
  const estado      = document.getElementById('filter-estado').value;
  const inactividad = document.getElementById('filter-inactividad').value;

  filteredData = rawData.filter(r => {
    const v  = getField(r,'vendedor');
    const e  = getField(r,'estado');
    const ni = getField(r,'nivel');
    return (!vendedor || v === vendedor) &&
           (!estado   || e === estado)   &&
           (!inactividad || ni === inactividad);
  });

  renderAll();
}

// ═══════════════════════════════════
// RENDER ALL
// ═══════════════════════════════════
function renderAll() {
  renderKPIs();
  renderEstadosBar();
  renderEstadosDonut();
  renderAllEstados();
  renderInactivityEstados();
  renderInactivosSection();
  renderInactividadDist();
  renderMainTable();
}

// ═══════════════════════════════════
// KPIs
// ═══════════════════════════════════
function renderKPIs() {
  const data = filteredData;
  const totalBs      = data.reduce((s,r) => s + num(getField(r,'totalBs')), 0);
  const totalUnid    = data.reduce((s,r) => s + num(getField(r,'unidades')), 0);
  const totalFact    = data.reduce((s,r) => s + num(getField(r,'facturas')), 0);
  const inactivos    = data.filter(r => num(getField(r,'dias')) >= 60).length;
  const criticos     = data.filter(r => getField(r,'nivel') === '+6 meses sin comprar').length;

  document.getElementById('kpi-total-clientes').textContent = fmtNum(data.length);
  document.getElementById('kpi-total-bs').textContent       = fmtBs(totalBs);
  document.getElementById('kpi-total-unidades').textContent = fmtNum(totalUnid);
  document.getElementById('kpi-inactivos').textContent      = fmtNum(inactivos);
  document.getElementById('kpi-criticos').textContent       = fmtNum(criticos);
  document.getElementById('kpi-facturas').textContent       = fmtNum(totalFact);
}

// ═══════════════════════════════════
// ESTADOS BAR (TOP 10)
// ═══════════════════════════════════
function renderEstadosBar() {
  const agg = aggregateByEstado(filteredData);
  const top10 = agg.slice(0,10);

  const labels = top10.map(e => e.estado);
  const values = top10.map(e => e.totalBs);

  destroyChart('chart-estados-bar');
  const ctx = document.getElementById('chart-estados-bar').getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, 600, 0);
  gradient.addColorStop(0, 'rgba(0,229,255,0.9)');
  gradient.addColorStop(1, 'rgba(0,180,204,0.4)');

  charts['chart-estados-bar'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Total Bs',
        data: values,
        backgroundColor: gradient,
        borderRadius: 6,
        borderSkipped: false,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        datalabels: {
          anchor: 'end', align: 'end',
          color: 'rgba(0,229,255,0.8)',
          font: { size: 10, weight: '700' },
          formatter: v => fmtNum(v),
        },
        tooltip: {
          callbacks: { label: ctx => ' ' + fmtBs(ctx.parsed.x) }
        }
      },
      scales: {
        x: { ticks: { color: '#8892a4', font: { size: 10 }, callback: v => fmtNum(v) }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#e2e8f0', font: { size: 11, weight: '600' } }, grid: { display: false } }
      }
    }
  });
}

// ═══════════════════════════════════
// ESTADOS DONUT
// ═══════════════════════════════════
function renderEstadosDonut() {
  const agg    = aggregateByEstado(filteredData);
  const top8   = agg.slice(0,8);
  const resto  = agg.slice(8).reduce((s,e) => s + e.totalBs, 0);
  const labels = top8.map(e => e.estado);
  const values = top8.map(e => e.totalBs);
  if (resto > 0) { labels.push('Otros'); values.push(resto); }

  const COLORS = ['#00e5ff','#b57bff','#39ff8f','#ff9f43','#4dabf7','#ff4d6a','#ffd43b','#f06595','#74c0fc'];

  destroyChart('chart-estados-donut');
  const ctx = document.getElementById('chart-estados-donut').getContext('2d');
  charts['chart-estados-donut'] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: COLORS.slice(0, labels.length),
        borderColor: '#141828',
        borderWidth: 3,
        hoverBorderWidth: 0,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#8892a4', font: { size: 10 }, padding: 12, boxWidth: 12 }
        },
        datalabels: {
          color: '#fff',
          font: { size: 10, weight: '700' },
          formatter: (v, ctx) => {
            const total = ctx.dataset.data.reduce((a,b)=>a+b,0);
            const pct = ((v/total)*100).toFixed(1);
            return pct >= 5 ? pct + '%' : '';
          }
        },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${fmtBs(ctx.parsed)}` } }
      }
    }
  });
}

// ═══════════════════════════════════
// ALL ESTADOS (full bar)
// ═══════════════════════════════════
function renderAllEstados() {
  const agg    = aggregateByEstado(filteredData);
  const labels = agg.map(e => e.estado);
  const values = agg.map(e => e.totalBs);

  destroyChart('chart-all-estados');
  const ctx = document.getElementById('chart-all-estados').getContext('2d');
  charts['chart-all-estados'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: 'rgba(181,123,255,0.7)',
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        datalabels: { display: false },
        tooltip: { callbacks: { label: c => ' ' + fmtBs(c.parsed.x) } }
      },
      scales: {
        x: { ticks: { color: '#8892a4', font: { size: 10 }, callback: v => fmtNum(v) }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#e2e8f0', font: { size: 10 } }, grid: { display: false } }
      }
    }
  });
}

// ═══════════════════════════════════
// INACTIVIDAD POR ESTADO (avg days)
// ═══════════════════════════════════
function renderInactivityEstados() {
  const byEstado = {};
  filteredData.forEach(r => {
    const e = getField(r,'estado') || 'Sin Estado';
    const d = num(getField(r,'dias'));
    if (!byEstado[e]) byEstado[e] = [];
    byEstado[e].push(d);
  });
  const agg = Object.entries(byEstado)
    .map(([e, arr]) => ({ estado: e, avgDias: arr.reduce((s,v)=>s+v,0)/arr.length }))
    .filter(x => x.avgDias > 0)
    .sort((a,b) => b.avgDias - a.avgDias)
    .slice(0, 15);

  const labels = agg.map(e => e.estado);
  const values = agg.map(e => Math.round(e.avgDias));

  const colors = values.map(v =>
    v >= 180 ? 'rgba(255,32,80,0.8)' :
    v >= 120 ? 'rgba(255,77,106,0.75)' :
    v >= 90  ? 'rgba(255,159,67,0.75)' :
               'rgba(255,212,59,0.75)'
  );

  destroyChart('chart-inactivity-estados');
  const ctx = document.getElementById('chart-inactivity-estados').getContext('2d');
  charts['chart-inactivity-estados'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        datalabels: {
          anchor: 'end', align: 'end',
          color: '#8892a4',
          font: { size: 10 },
          formatter: v => v + ' días',
        },
        tooltip: { callbacks: { label: c => ` Promedio: ${c.parsed.x} días sin comprar` } }
      },
      scales: {
        x: { ticks: { color: '#8892a4', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#e2e8f0', font: { size: 10 } }, grid: { display: false } }
      }
    }
  });
}

// ═══════════════════════════════════
// SECTION INACTIVOS — mini KPIs
// ═══════════════════════════════════
function renderInactivosSection() {
  const n2m  = filteredData.filter(r => getField(r,'nivel') === '2 meses sin comprar').length;
  const n3m  = filteredData.filter(r => getField(r,'nivel') === '3 meses sin comprar').length;
  const n45m = filteredData.filter(r => getField(r,'nivel') === '4-5 meses sin comprar').length;
  const n6m  = filteredData.filter(r => getField(r,'nivel') === '+6 meses sin comprar').length;

  document.getElementById('mk-2m').textContent  = n2m;
  document.getElementById('mk-3m').textContent  = n3m;
  document.getElementById('mk-45m').textContent = n45m;
  document.getElementById('mk-6m').textContent  = n6m;

  // Tabla de críticos
  const criticos = [...filteredData]
    .filter(r => num(getField(r,'dias')) >= 60)
    .sort((a,b) => num(getField(b,'dias')) - num(getField(a,'dias')))
    .slice(0, 50);

  const tbody = document.getElementById('tbody-criticos');
  tbody.innerHTML = criticos.map(r => `
    <tr>
      <td title="${getField(r,'rif')}">${truncate(getField(r,'nombre'), 28)}</td>
      <td>${getField(r,'estado') || '—'}</td>
      <td>${getField(r,'vendedor') || '—'}</td>
      <td>${getField(r,'ultimaCompra') || '—'}</td>
      <td style="text-align:center;font-weight:700;color:${diasColor(num(getField(r,'dias')))}">${getField(r,'dias') || '—'}</td>
      <td>${nivelBadge(getField(r,'nivel'))}</td>
      <td>${fmtBs(num(getField(r,'totalBs')))}</td>
    </tr>
  `).join('');
}

// ═══════════════════════════════════
// DISTRIBUCIÓN INACTIVIDAD DONUT
// ═══════════════════════════════════
function renderInactividadDist() {
  const n2m  = filteredData.filter(r => getField(r,'nivel') === '2 meses sin comprar').length;
  const n3m  = filteredData.filter(r => getField(r,'nivel') === '3 meses sin comprar').length;
  const n45m = filteredData.filter(r => getField(r,'nivel') === '4-5 meses sin comprar').length;
  const n6m  = filteredData.filter(r => getField(r,'nivel') === '+6 meses sin comprar').length;
  const nOk  = filteredData.filter(r => !getField(r,'nivel')).length;

  const labels = ['Activos (< 60 d.)', '2 meses', '3 meses', '4-5 meses', '+6 meses'];
  const values = [nOk, n2m, n3m, n45m, n6m];
  const colors = ['rgba(57,255,143,0.8)','rgba(255,212,59,0.8)','rgba(255,159,67,0.8)','rgba(255,77,106,0.8)','rgba(255,32,80,0.9)'];

  destroyChart('chart-inactividad-dist');
  const ctx = document.getElementById('chart-inactividad-dist').getContext('2d');
  charts['chart-inactividad-dist'] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderColor: '#141828',
        borderWidth: 3,
        hoverBorderWidth: 0,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '62%',
      plugins: {
        legend: { position: 'bottom', labels: { color: '#8892a4', font: { size: 10 }, padding: 10, boxWidth: 12 } },
        datalabels: {
          color: '#fff',
          font: { size: 11, weight: '700' },
          formatter: (v, ctx) => {
            const total = ctx.dataset.data.reduce((a,b)=>a+b,0);
            return v > 0 ? v : '';
          }
        },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} clientes` } }
      }
    }
  });
}

// ═══════════════════════════════════
// MAIN TABLE (paginated + search)
// ═══════════════════════════════════
let tableData = [];
function renderMainTable() {
  const search = (document.getElementById('search-input').value || '').toLowerCase();
  tableData = filteredData.filter(r => {
    const hay = [
      getField(r,'rif'), getField(r,'nombre'),
      getField(r,'estado'), getField(r,'vendedor')
    ].join(' ').toLowerCase();
    return hay.includes(search);
  });

  document.getElementById('table-count').textContent = tableData.length;
  renderPage(1);
}

function renderPage(page) {
  currentPage = page;
  const start = (page - 1) * PAGE_SIZE;
  const slice = tableData.slice(start, start + PAGE_SIZE);

  const tbody = document.getElementById('tbody-main');
  tbody.innerHTML = slice.map(r => `
    <tr>
      <td>${getField(r,'rif') || '—'}</td>
      <td title="${getField(r,'nombre')}">${truncate(getField(r,'nombre'), 32)}</td>
      <td>${getField(r,'telefono') || '—'}</td>
      <td>${getField(r,'estado') || '—'}</td>
      <td>${getField(r,'vendedor') || '—'}</td>
      <td>${getField(r,'ultimaCompra') || '—'}</td>
      <td style="text-align:center;font-weight:700;color:${diasColor(num(getField(r,'dias')))}">${getField(r,'dias') || '0'}</td>
      <td>${nivelBadge(getField(r,'nivel'))}</td>
      <td style="text-align:right">${fmtNum(num(getField(r,'unidades')))}</td>
      <td style="text-align:right">${fmtNum(num(getField(r,'facturas')))}</td>
      <td style="text-align:right;font-weight:600">${fmtBs(num(getField(r,'totalBs')))}</td>
    </tr>
  `).join('');

  renderPagination();
}

function renderPagination() {
  const total = Math.ceil(tableData.length / PAGE_SIZE);
  if (total <= 1) { document.getElementById('pagination').innerHTML = ''; return; }

  let html = `<button class="page-btn" onclick="renderPage(${currentPage-1})" ${currentPage===1?'disabled':''}>‹</button>`;
  const range = pagRange(currentPage, total);
  range.forEach(p => {
    if (p === '...') html += `<span style="color:#8892a4;padding:6px 4px">…</span>`;
    else html += `<button class="page-btn ${p===currentPage?'active':''}" onclick="renderPage(${p})">${p}</button>`;
  });
  html += `<button class="page-btn" onclick="renderPage(${currentPage+1})" ${currentPage===total?'disabled':''}>›</button>`;
  document.getElementById('pagination').innerHTML = html;
}

function pagRange(cur, total) {
  const delta = 2, range = [], rangeWithDots = [];
  for (let i = Math.max(2,cur-delta); i <= Math.min(total-1,cur+delta); i++) range.push(i);
  if (range[0] > 2) rangeWithDots.push(1,'...');
  else rangeWithDots.push(1);
  rangeWithDots.push(...range);
  if (range[range.length-1] < total-1) rangeWithDots.push('...',total);
  else rangeWithDots.push(total);
  return rangeWithDots;
}

// ═══════════════════════════════════
// EXPORT CSV
// ═══════════════════════════════════
function exportCSV() {
  if (filteredData.length === 0) { toast('No hay datos para exportar.', 'error'); return; }
  const fields = Object.keys(filteredData[0]);
  const rows   = [fields.join(';')].concat(
    filteredData.map(r => fields.map(f => `"${String(r[f]||'').replace(/"/g,'""')}"`).join(';'))
  );
  const blob = new Blob(['\uFEFF' + rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'), { href: url, download: `clientes_mayor_filtrado.csv` });
  a.click();
  URL.revokeObjectURL(url);
  toast('✅ CSV exportado correctamente.', 'success');
}

// ═══════════════════════════════════
// HELPERS
// ═══════════════════════════════════
function aggregateByEstado(data) {
  const byEstado = {};
  data.forEach(r => {
    const e = getField(r,'estado') || 'Sin Estado';
    if (!byEstado[e]) byEstado[e] = { estado: e, totalBs: 0, clientes: 0, unidades: 0 };
    byEstado[e].totalBs   += num(getField(r,'totalBs'));
    byEstado[e].clientes  += 1;
    byEstado[e].unidades  += num(getField(r,'unidades'));
  });
  return Object.values(byEstado).sort((a,b) => b.totalBs - a.totalBs);
}

function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

function truncate(str, n) {
  str = str || '';
  return str.length > n ? str.slice(0, n) + '…' : str;
}

function diasColor(d) {
  if (d >= 180) return '#ff2050';
  if (d >= 120) return '#ff4d6a';
  if (d >= 90)  return '#ff9f43';
  if (d >= 60)  return '#ffd43b';
  return '#39ff8f';
}

function nivelBadge(nivel) {
  if (!nivel) return '<span class="badge badge-none">Activo</span>';
  if (nivel.includes('2 meses'))   return `<span class="badge badge-2m">🟡 2 meses</span>`;
  if (nivel.includes('3 meses'))   return `<span class="badge badge-3m">🟠 3 meses</span>`;
  if (nivel.includes('4-5'))       return `<span class="badge badge-45m">🔴 4-5 meses</span>`;
  if (nivel.includes('+6') || nivel.includes('6'))  return `<span class="badge badge-6m">🚨 +6 meses</span>`;
  return `<span class="badge badge-none">${nivel}</span>`;
}

// ═══════════════════════════════════
// EVENT LISTENERS
// ═══════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {

  // Date
  updateDate();

  // CSV upload
  document.getElementById('csv-input').addEventListener('change', e => {
    const file = e.target.files[0];
    if (file) parseCSV(file);
    e.target.value = '';
  });

  // Drag & drop
  document.body.addEventListener('dragover', e => { e.preventDefault(); document.body.classList.add('drag-over'); });
  document.body.addEventListener('dragleave', () => document.body.classList.remove('drag-over'));
  document.body.addEventListener('drop', e => {
    e.preventDefault();
    document.body.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) parseCSV(file);
    else toast('⚠️ Solo se aceptan archivos .csv', 'error');
  });

  // Filters
  ['filter-vendedor','filter-estado','filter-inactividad'].forEach(id => {
    document.getElementById(id).addEventListener('change', applyFilters);
  });

  // Navigation
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', e => {
      e.preventDefault();
      const sec = item.dataset.section;
      showSection(sec);
    });
  });

  // Sidebar toggle
  document.getElementById('sidebar-toggle').addEventListener('click', () => {
    const sb = document.getElementById('sidebar');
    const mc = document.querySelector('.main-content');
    sb.classList.toggle('open');
    sb.classList.toggle('collapsed');
    mc.classList.toggle('full');
  });

  // Search
  document.getElementById('search-input').addEventListener('input', renderMainTable);

  // Export
  document.getElementById('export-btn').addEventListener('click', exportCSV);
});
