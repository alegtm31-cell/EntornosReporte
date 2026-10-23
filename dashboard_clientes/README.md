# 📊 Dashboard de Clientes al Mayor (MarketPulse)

Tablero web interactivo de análisis comercial y retención de clientes al mayor. Diseñado para ofrecer una visión ejecutiva 360° de la cartera de clientes, niveles de actividad/inactividad, desempeño por vendedor y distribución geográfica.

---

## 🎯 Objetivo y Funcionalidades

El dashboard permite a la gerencia comercial y al equipo de ventas:
* **Monitorear KPIs en Tiempo Real**: Facturación total en USD y Bolívares (VES), volumen de unidades despachadas, total de facturas emitidas y conteo de clientes activos vs. inactivos.
* **Segmentación de Inactividad**: Clasificación automática de clientes según los días transcurridos desde su última compra (e.g., Activo, 15-30 días, 30-60 días, Crítico +60 días).
* **Desempeño de la Fuerza de Ventas**: Comparativa visual de ventas y facturación acumulada por cada asesor comercial al mayor.
* **Distribución Geográfica**: Análisis de ventas y presencia de clientes por estado/provincia a nivel nacional.
* **Explorador y Búsqueda de Clientes**: Tabla con paginación dinámica, búsqueda instantánea por RIF/Nombre/Teléfono y filtros combinados.

---

## 🔌 Conexión con la Base de Datos

Los datos que alimentan este dashboard provienen directamente de la base de datos **Saint Enterprise ERP (PostgreSQL)**:
1. **Extracción**: El script `generar_reporte_almayor.py` o el pipeline `etl_db.py` ejecuta consultas directas a las tablas transaccionales:
   * `public.sales_operation` (encabezados de factura y tipos de operación).
   * `public.sales_operation_details` (unidades y artículos).
   * `public.sales_operation_coins` (conversión de moneda y tasa oficial del día).
   * `public.sellers` (fuerza de ventas activa).
   * `public.clients` (catálogo y datos de contacto de clientes).
2. **Generación del Dataset**: Se produce un archivo consolidado estructurado en `.csv` o `.xlsx` (`clientes_almayor_consolidado.csv` o `Reporte_Clientes_AlMayor_Completo.xlsx`).
3. **Consumo en el Dashboard**: El archivo `app.js` contiene un motor inteligente de normalización de cabeceras (`COL_ALIASES`) que mapea automáticamente los nombres de columnas sin importar variaciones en el origen de datos.

---

## 🛠️ Tecnologías Utilizadas

* **HTML5**: Estructura semántica moderna con diseño responsive.
* **CSS3**: Estilos avanzados, diseño en cuadrícula (CSS Grid / Flexbox), paleta de colores corporativa y soporte responsivo.
* **JavaScript (ES6+)**: Lógica de cálculo de métricas, filtrado en memoria, paginación y renderizado dinámico.
* **Chart.js + ChartDataLabels**: Visualización interactiva de gráficos circulares (doughnut) y de barras.
* **SheetJS (xlsx.full.min.js)** / **PapaParse**: Procesamiento en el cliente de archivos de datos Excel y CSV.

---

## 🚀 Cómo Ejecutar

1. Abre el archivo `index.html` en cualquier navegador web.
2. Si los datos no cargan automáticamente, haz clic en el botón de carga o arrastra el archivo CSV/Excel generado desde la base de datos.
3. Utiliza los filtros superiores por vendedor, estatus o estado para segmentar la información.
