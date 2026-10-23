/* ═══════════════════════════════════════════════════════
   MarketPulse Dashboard — app.js
   Soporte completo: Excel (.xlsx), CSV, filtros y gráficos
═══════════════════════════════════════════════════════ */

Chart.register(ChartDataLabels);

// ═══════════════════════════════════════════════════════
// MAPA DE ALIAS DE COLUMNAS
// ═══════════════════════════════════════════════════════
const COL_ALIASES = {
  rif: ['RIF / Código', 'RIF_Cedula', 'rif_cedula', 'rif', 'cedula', 'codigo', 'code'],
  nombre: ['Nombre del Cliente', 'Razon_Social', 'razon_social', 'razon social', 'nombre', 'description', 'cliente'],
  telefono: ['Teléfono', 'Telefono', 'telefono', 'phone', 'tlf', 'telf', 'celular'],
  estado: ['Provincia / Estado', 'Estado', 'estado', 'province', 'provincia'],
  vendedor: ['Persona que le Vendió (Última Venta)', 'Ultimo_Vendedor', 'ultimo_vendedor', 'vendedor', 'seller'],
  ultimaCompra: ['Última Compra', 'Ultima_Compra', 'ultima_compra', 'last_purchase', 'fecha'],
  dias: ['Dias_Sin_Comprar', 'dias_sin_comprar', 'dias sin comprar', 'dias', 'days'],
  nivel: ['Nivel_Inactividad', 'nivel_inactividad', 'nivel inactividad', 'nivel', 'inactividad'],
  unidades: ['Total Unidades', 'Total_Unidades_Año', 'total_unidades_ano', 'total_unidades', 'unidades', 'cantidad'],
  facturas: ['Total Facturas', 'Total_Facturas_Año', 'total_facturas_ano', 'total_facturas', 'facturas'],
  totalBs: ['Monto Total Bs.', 'Total_Facturado_Bs_Año', 'total_facturado_bs_ano', 'total_bs', 'monto'],
  totalUsd: ['Monto Total USD ($)', 'monto_total_usd', 'total_usd', 'usd', 'monto usd']
};

let colMap = {};
let rawData = [];
let filteredData = [];
let charts = {};
let currentPage = 1;
const PAGE_SIZE = 30;

function norm(s) {
  return String(s)
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

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
    if (!colMap[field]) {
      for (const alias of aliases) {
        const na = norm(alias);
        const found = normHeaders.find(h => h.n.includes(na) || na.includes(h.n));
        if (found) { colMap[field] = found.real; break; }
      }
    }
  }

  return colMap;
}

function getField(row, field) {
  const col = colMap[field];
  if (!col) return '';
  const val = row[col];
  return val === undefined || val === null ? '' : val;
}

function num(v) {
  if (v === null || v === undefined || v === '') return 0;
  return parseFloat(String(v).replace(/\./g, '').replace(',', '.')) ||
    parseFloat(String(v).replace(',', '.')) || 0;
}

function fmtNum(n) { return new Intl.NumberFormat('es-VE', { maximumFractionDigits: 2 }).format(n); }
function fmtBs(n) { return 'Bs ' + new Intl.NumberFormat('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n); }
function fmtUsd(n) { return '$ ' + new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n); }

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
  const titles = { overview: 'Resumen General', estados: 'Análisis por Estado', inactivos: 'Clientes Inactivos', tabla: 'Tabla Completa' };
  document.getElementById('section-title').textContent = titles[id] || '';
}

// ═══════════════════════════════════
// LECTURA DE ARCHIVOS (EXCEL / CSV)
// ═══════════════════════════════════
function handleFileSelect(file) {
  if (!file) return;
  const fileName = file.name.toLowerCase();

  if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
    parseExcel(file);
  } else if (fileName.endsWith('.csv')) {
    parseCSV(file);
  } else {
    toast('⚠️ Formato no soportado. Usa .xlsx, .xls o .csv', 'error');
  }
}

function parseExcel(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: 'array' });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];

      rawData = XLSX.utils.sheet_to_json(worksheet, { defval: "" });
      if (rawData.length === 0) {
        toast('⚠️ El archivo Excel está vacío.', 'error');
        return;
      }

      // Calcular días de inactividad si no existen explícitamente en el Excel
      rawData.forEach(r => {
        if (!getField(r, 'dias') && getField(r, 'ultimaCompra')) {
          const fechaU = new Date(getField(r, 'ultimaCompra'));
          if (!isNaN(fechaU)) {
            const diffTime = Math.abs(new Date() - fechaU);
            r['Dias_Sin_Comprar_Calc'] = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          }
        }
      });

      const headers = Object.keys(rawData[0]);
      buildColMap(headers);
      initDashboard();
      toast(`✅ ${rawData.length} registros cargados correctamente desde Excel.`, 'success');
    } catch (err) {
      console.error(err);
      toast('❌ Error al procesar el archivo Excel.', 'error');
    }
  };
  reader.readAsArrayBuffer(file);
}

function parseCSV(file) {
  Papa.parse(file, {
    header: true,
    skipEmptyLines: true,
    complete: (results) => {
      if (!results.data || results.data.length === 0) {
        toast('⚠️ El archivo está vacío.', 'error');
        return;
      }
      rawData = results.data;
      const headers = results.meta.fields || Object.keys(rawData[0]);
      buildColMap(headers);
      initDashboard();
      toast(`✅ ${rawData.length} clientes cargados desde el CSV.`, 'success');
    },
    error: () => toast('❌ Error al leer el CSV.', 'error')
  });
}

// ═══════════════════════════════════
// DASHBOARD LOGIC
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
    d.toLocaleDateString('es-VE', { day: '2-digit', month: 'long', year: 'numeric' });
}

function populateFilters() {
  const vendedores = [...new Set(rawData.map(r => getField(r, 'vendedor')).filter(Boolean))].sort();
  const estados = [...new Set(rawData.map(r => getField(r, 'estado')).filter(Boolean))].sort();

  const selV = document.getElementById('filter-vendedor');
  const selE = document.getElementById('filter-estado');
  selV.innerHTML = '<option value="">Todos los vendedores</option>' +
    vendedores.map(v => `<option value="${v}">${v}</option>`).join('');
  selE.innerHTML = '<option value="">Todos los estados</option>' +
    estados.map(e => `<option value="${e}">${e}</option>`).join('');
}

function applyFilters() {
  const vendedor = document.getElementById('filter-vendedor').value;
  const estado = document.getElementById('filter-estado').value;
  const inactividad = document.getElementById('filter-inactividad').value;

  filteredData = rawData.filter(r => {
    const v = getField(r, 'vendedor');
    const e = getField(r, 'estado');
    const ni = getField(r, 'nivel');
    return (!vendedor || v === vendedor) &&
      (!estado || e === estado) &&
      (!inactividad || ni === inactividad);
  });

  renderAll();
}

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
  const totalBs = data.reduce((s, r) => s + num(getField(r, 'totalBs')), 0);
  const totalUsd = data.reduce((s, r) => s + num(getField(r, 'totalUsd')), 0);
  const totalUnid = data.reduce((s, r) => s + num(getField(r, 'unidades')), 0);
  const totalFact = data.reduce((s, r) => s + num(getField(r, 'facturas')), 0);
  const inactivos = data.filter(r => num(getField(r, 'dias')) >= 60).length;
  const criticos = data.filter(r => String(getField(r, 'nivel')).includes('+6')).length;

  document.getElementById('kpi-total-clientes').textContent = fmtNum(data.length);
  document.getElementById('kpi-total-bs').textContent = fmtBs(totalBs);
  document.getElementById('kpi-total-usd').textContent = fmtUsd(totalUsd);
  document.getElementById('kpi-total-unidades').textContent = fmtNum(totalUnid);
  document.getElementById('kpi-inactivos').textContent = fmtNum(inactivos);
  document.getElementById('kpi-criticos').textContent = fmtNum(criticos);
}

// ═══════════════════════════════════
// CHARTS
// ═══════════════════════════════════
function renderEstadosBar() {
  const agg = aggregateByEstado(filteredData);
  const top10 = agg.slice(0, 10);

  const labels = top10.map(e => e.estado);
  const values = top10.map(e => e.totalUsd || e.totalBs);

  destroyChart('chart-estados-bar');
  const ctx = document.getElementById('chart-estados-bar').getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, 600, 0);
  gradient.addColorStop(0, 'rgba(0,229,255,0.9)');
  gradient.addColorStop(1, 'rgba(0,180,204,0.4)');

  charts['chart-estados-bar'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'Total USD', data: values, backgroundColor: gradient, borderRadius: 6 }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        datalabels: { anchor: 'end', align: 'end', color: 'rgba(0,229,255,0.8)', formatter: v => fmtNum(v) },
        tooltip: { callbacks: { label: ctx => ' ' + fmtUsd(ctx.parsed.x) } }
      },
      scales: {
        x: { ticks: { color: '#8892a4', callback: v => fmtNum(v) }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#e2e8f0' }, grid: { display: false } }
      }
    }
  });
}

function renderEstadosDonut() {
  const agg = aggregateByEstado(filteredData);
  const top8 = agg.slice(0, 8);
  const resto = agg.slice(8).reduce((s, e) => s + (e.totalUsd || e.totalBs), 0);
  const labels = top8.map(e => e.estado);
  const values = top8.map(e => e.totalUsd || e.totalBs);
  if (resto > 0) { labels.push('Otros'); values.push(resto); }

  const COLORS = ['#00e5ff', '#b57bff', '#39ff8f', '#ff9f43', '#4dabf7', '#ff4d6a', '#ffd43b', '#f06595', '#74c0fc'];

  destroyChart('chart-estados-donut');
  const ctx = document.getElementById('chart-estados-donut').getContext('2d');
  charts['chart-estados-donut'] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: COLORS.slice(0, labels.length), borderColor: '#141828', borderWidth: 3 }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: { position: 'bottom', labels: { color: '#8892a4', padding: 12, boxWidth: 12 } },
        datalabels: {
          color: '#fff',
          formatter: (v, ctx) => {
            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
            const pct = ((v / total) * 100).toFixed(1);
            return pct >= 5 ? pct + '%' : '';
          }
        },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${fmtUsd(ctx.parsed)}` } }
      }
    }
  });
}

function renderAllEstados() {
  const agg = aggregateByEstado(filteredData);
  const labels = agg.map(e => e.estado);
  const values = agg.map(e => e.totalUsd || e.totalBs);

  destroyChart('chart-all-estados');
  const ctx = document.getElementById('chart-all-estados').getContext('2d');
  charts['chart-all-estados'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: 'rgba(181,123,255,0.7)', borderRadius: 5 }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, datalabels: { display: false } },
      scales: {
        x: { ticks: { color: '#8892a4', callback: v => fmtNum(v) }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#e2e8f0' }, grid: { display: false } }
      }
    }
  });
}

function renderInactivityEstados() {
  const byEstado = {};
  filteredData.forEach(r => {
    const e = getField(r, 'estado') || 'Sin Estado';
    const d = num(getField(r, 'dias'));
    if (!byEstado[e]) byEstado[e] = [];
    byEstado[e].push(d);
  });
  const agg = Object.entries(byEstado)
    .map(([e, arr]) => ({ estado: e, avgDias: arr.reduce((s, v) => s + v, 0) / arr.length }))
    .filter(x => x.avgDias > 0)
    .sort((a, b) => b.avgDias - a.avgDias)
    .slice(0, 15);

  const labels = agg.map(e => e.estado);
  const values = agg.map(e => Math.round(e.avgDias));

  destroyChart('chart-inactivity-estados');
  const ctx = document.getElementById('chart-inactivity-estados').getContext('2d');
  charts['chart-inactivity-estados'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: 'rgba(255,77,106,0.75)', borderRadius: 5 }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, datalabels: { anchor: 'end', align: 'end', color: '#8892a4', formatter: v => v + 'd' } },
      scales: {
        x: { ticks: { color: '#8892a4' }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#e2e8f0' }, grid: { display: false } }
      }
    }
  });
}

function renderInactivosSection() {
  const n40m = filteredData.filter(r => String(getField(r, 'nivel')).includes('40-59')).length;
  const n2m = filteredData.filter(r => String(getField(r, 'nivel')).includes('2 meses')).length;
  const n3m = filteredData.filter(r => String(getField(r, 'nivel')).includes('3 meses')).length;
  const n45m = filteredData.filter(r => String(getField(r, 'nivel')).includes('4-5')).length;
  const n6m = filteredData.filter(r => String(getField(r, 'nivel')).includes('+6')).length;

  document.getElementById('mk-40m').textContent = n40m;
  document.getElementById('mk-2m').textContent = n2m;
  document.getElementById('mk-3m').textContent = n3m;
  document.getElementById('mk-45m').textContent = n45m;
  document.getElementById('mk-6m').textContent = n6m;

  const criticos = [...filteredData]
    .filter(r => num(getField(r, 'dias')) >= 60)
    .sort((a, b) => num(getField(b, 'dias')) - num(getField(a, 'dias')))
    .slice(0, 50);

  const tbody = document.getElementById('tbody-criticos');
  tbody.innerHTML = criticos.map(r => `
    <tr>
      <td title="${getField(r, 'nombre')}">${truncate(getField(r, 'nombre'), 28)}</td>
      <td>${getField(r, 'estado') || '—'}</td>
      <td>${getField(r, 'vendedor') || '—'}</td>
      <td>${getField(r, 'ultimaCompra') || '—'}</td>
      <td style="text-align:center;font-weight:700;color:${diasColor(num(getField(r, 'dias')))}">${getField(r, 'dias') || '—'}</td>
      <td>${nivelBadge(getField(r, 'nivel'))}</td>
      <td>${fmtUsd(num(getField(r, 'totalUsd')))}</td>
    </tr>
  `).join('');
}

function renderInactividadDist() {
  const n40m = filteredData.filter(r => String(getField(r, 'nivel')).includes('40-59')).length;
  const n2m = filteredData.filter(r => String(getField(r, 'nivel')).includes('2 meses')).length;
  const n3m = filteredData.filter(r => String(getField(r, 'nivel')).includes('3 meses')).length;
  const n45m = filteredData.filter(r => String(getField(r, 'nivel')).includes('4-5')).length;
  const n6m = filteredData.filter(r => String(getField(r, 'nivel')).includes('+6')).length;
  const nOk = filteredData.filter(r => num(getField(r, 'dias')) < 40).length;

  destroyChart('chart-inactividad-dist');
  const ctx = document.getElementById('chart-inactividad-dist').getContext('2d');
  charts['chart-inactividad-dist'] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['< 40 días', '40-59 días', '2 meses', '3 meses', '4-5 meses', '+6 meses'],
      datasets: [{
        data: [nOk, n40m, n2m, n3m, n45m, n6m],
        backgroundColor: ['#39ff8f', '#00e5ff', '#ffd43b', '#ff9f43', '#ff4d6a', '#ff2050'],
        borderColor: '#141828',
        borderWidth: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '62%',
      plugins: { legend: { position: 'bottom', labels: { color: '#8892a4', padding: 10, boxWidth: 12 } } }
    }
  });
}

// ═══════════════════════════════════
// MAIN TABLE
// ═══════════════════════════════════
let tableData = [];
function renderMainTable() {
  const search = (document.getElementById('search-input').value || '').toLowerCase();
  tableData = filteredData.filter(r => {
    const hay = [
      getField(r, 'rif'), getField(r, 'nombre'),
      getField(r, 'estado'), getField(r, 'vendedor')
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
      <td>${getField(r, 'rif') || '—'}</td>
      <td title="${getField(r, 'nombre')}">${truncate(getField(r, 'nombre'), 32)}</td>
      <td>${getField(r, 'telefono') || '—'}</td>
      <td>${getField(r, 'estado') || '—'}</td>
      <td>${getField(r, 'vendedor') || '—'}</td>
      <td>${getField(r, 'ultimaCompra') || '—'}</td>
      <td style="text-align:center;font-weight:700;color:${diasColor(num(getField(r, 'dias')))}">${getField(r, 'dias') || '0'}</td>
      <td>${nivelBadge(getField(r, 'nivel'))}</td>
      <td style="text-align:right">${fmtNum(num(getField(r, 'unidades')))}</td>
      <td style="text-align:right">${fmtNum(num(getField(r, 'facturas')))}</td>
      <td style="text-align:right;font-weight:600;color:#39ff8f">${fmtUsd(num(getField(r, 'totalUsd')))}</td>
      <td style="text-align:right">${fmtBs(num(getField(r, 'totalBs')))}</td>
    </tr>
  `).join('');

  renderPagination();
}

function renderPagination() {
  const total = Math.ceil(tableData.length / PAGE_SIZE);
  if (total <= 1) { document.getElementById('pagination').innerHTML = ''; return; }

  let html = `<button class="page-btn" onclick="renderPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>‹</button>`;
  for (let p = 1; p <= total; p++) {
    if (p === 1 || p === total || (p >= currentPage - 2 && p <= currentPage + 2)) {
      html += `<button class="page-btn ${p === currentPage ? 'active' : ''}" onclick="renderPage(${p})">${p}</button>`;
    }
  }
  html += `<button class="page-btn" onclick="renderPage(${currentPage + 1})" ${currentPage === total ? 'disabled' : ''}>›</button>`;
  document.getElementById('pagination').innerHTML = html;
}

function exportCSV() {
  if (filteredData.length === 0) { toast('No hay datos para exportar.', 'error'); return; }
  const fields = Object.keys(filteredData[0]);
  const rows = [fields.join(';')].concat(
    filteredData.map(r => fields.map(f => `"${String(r[f] || '').replace(/"/g, '""')}"`).join(';'))
  );
  const blob = new Blob(['\uFEFF' + rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement('a'), { href: url, download: `reporte_clientes_al_mayor.csv` });
  a.click();
  URL.revokeObjectURL(url);
  toast('✅ CSV exportado correctamente.', 'success');
}

function aggregateByEstado(data) {
  const byEstado = {};
  data.forEach(r => {
    const e = getField(r, 'estado') || 'Sin Estado';
    if (!byEstado[e]) byEstado[e] = { estado: e, totalBs: 0, totalUsd: 0, clientes: 0 };
    byEstado[e].totalBs += num(getField(r, 'totalBs'));
    byEstado[e].totalUsd += num(getField(r, 'totalUsd'));
    byEstado[e].clientes += 1;
  });
  return Object.values(byEstado).sort((a, b) => (b.totalUsd || b.totalBs) - (a.totalUsd || a.totalBs));
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
  if (d >= 90) return '#ff9f43';
  if (d >= 60) return '#ffd43b';
  if (d >= 40) return '#00e5ff';
  return '#39ff8f';
}

function nivelBadge(nivel) {
  const n = String(nivel);
  if (!n) return '<span class="badge badge-none">Activo</span>';
  if (n.includes('40-59')) return `<span class="badge badge-pre">⚠️ 40-59 días</span>`;
  if (n.includes('2 meses')) return `<span class="badge badge-2m">🟧 2 meses</span>`;
  if (n.includes('3 meses')) return `<span class="badge badge-3m">🟧 3 meses</span>`;
  if (n.includes('4-5')) return `<span class="badge badge-45m">🟥 4-5 meses</span>`;
  if (n.includes('+6') || n.includes('6')) return `<span class="badge badge-6m">🚨 +6 meses</span>`;
  return `<span class="badge badge-none">${n}</span>`;
}

// ═══════════════════════════════════
// LISTENERS
// ═══════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  updateDate();

  document.getElementById('csv-input').addEventListener('change', e => {
    handleFileSelect(e.target.files[0]);
    e.target.value = '';
  });

  document.body.addEventListener('dragover', e => { e.preventDefault(); document.body.classList.add('drag-over'); });
  document.body.addEventListener('dragleave', () => document.body.classList.remove('drag-over'));
  document.body.addEventListener('drop', e => {
    e.preventDefault();
    document.body.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) handleFileSelect(e.dataTransfer.files[0]);
  });

  ['filter-vendedor', 'filter-estado', 'filter-inactividad'].forEach(id => {
    document.getElementById(id).addEventListener('change', applyFilters);
  });

  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', e => {
      e.preventDefault();
      showSection(item.dataset.section);
    });
  });

  document.getElementById('sidebar-toggle').addEventListener('click', () => {
    const sb = document.getElementById('sidebar');
    const mc = document.querySelector('.main-content');
    sb.classList.toggle('open');
    sb.classList.toggle('collapsed');
    mc.classList.toggle('full');
  });

  document.getElementById('search-input').addEventListener('input', renderMainTable);
  document.getElementById('export-btn').addEventListener('click', exportCSV);
});