# 📊 Ecosistema de Dashboards, ETLs y Reportes Empresariales

Repositorio centralizado con todos los proyectos, entornos de análisis de datos, pipelines ETL y dashboards interactivos conectados a la base de datos empresarial (**Saint Enterprise ERP** sobre **PostgreSQL**).

---

## 🏛️ Arquitectura General del Sistema

El ecosistema opera mediante una arquitectura de tres capas: **Extracción (ETL)**, **Almacenamiento/Marts (Parquet/CSV)** y **Visualización/Consumo (Web Dashboards, Power BI y Reportes Automatizados)**.

```
       ┌────────────────────────────────────────────────────────┐
       │   Base de Datos PostgreSQL (Saint Enterprise ERP)      │
       │           Host: 192.168.91.131 / Puerto: 5433          │
       │              Base de Datos: cadm_j5004625301           │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
       ┌───────────────────┐             ┌─────────────────────┐
       │    etl_db.py      │             │etl_db_finance_cashea│
       │(Extracción en     │             │(Extracción Cashea   │
       │ Lotes SQLAlchemy) │             │    Financiamientos) │
       └─────────┬─────────┘             └──────────┬──────────┘
                 │                                  │
                 ▼                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │   Capa de Datos Optimizada (Apache Parquet / CSV)      │
       │  - almayor_sellers.parquet     - financiamientos.parq │
       │  - almayor_clients.parquet     - pays_cashea.parquet  │
       │  - almayor_detail_sales.parq   - phones_cashea.parq   │
       │  - clientes_inactivos_40d.csv  - sales.parquet        │
       └─────────┬──────────────────────────────────┬───────────┘
                 │                                  │
      ┌──────────┴──────────┐            ┌──────────┴──────────┐
      ▼                     ▼            ▼                     ▼
┌──────────────┐   ┌──────────────┐┌──────────────┐   ┌────────────────┐
│  Dashboard   │   │  Dashboard   ││   Power BI   │   │  Generadores   │
│   Clientes   │   │  Inactivos   ││  KPI Cashea  │   │  de Reportes   │
│(MarketPulse) │   │     (40d)    ││   & Envíos   │   │ Excel Avanzado │
└──────────────┘   └──────────────┘└──────────────┘   └────────────────┘
```

---

## 📂 Organización y Clasificación de Proyectos

### 1. 📈 Dashboards Conectados a Base de Datos y Datos Procesados

| Proyecto | Tipo de Dashboard | Fuente de Datos / Conexión | Descripción y Funcionalidad |
| :--- | :--- | :--- | :--- |
| [**`dashboard_clientes/`**](file:///C:/Users/YARBED/Desktop/Entornos/dashboard_clientes/README.md) | **Web Dashboard (HTML5/CSS3/JS/Chart.js)** | PostgreSQL (vía exportación/CSV de `generar_reporte_almayor.py` y `etl_db.py`) | **MarketPulse**: Tablero analítico integral de clientes al mayor. Visualiza facturación total en USD y Bs, unidades vendidas, distribución por vendedor, nivel de inactividad de clientes y mapa geográfico por estado. |
| [**`dashboard_40d/`**](file:///C:/Users/YARBED/Desktop/Entornos/dashboard_40d/README.md) | **Web Dashboard (HTML5/CSS3/JS)** | `consulta_clientes_almayor_inactivos.sql` / CSV procesado | **Retención de Clientes**: Tablero enfocado en el seguimiento de cuentas inactivas con más de 40 días sin comprar. Permite filtrado por vendedor para gestión de cobranza y reactivación comercial. |
| [**`finance_cashea/`**](file:///C:/Users/YARBED/Desktop/Entornos/finance_cashea/README.md) | **Power BI (`KPI Cashea.pbix`) + ETL Python** | PostgreSQL (`etl_db_finance_cashea.py`) | **KPI Financieros Cashea**: Tablero ejecutivo que mide transacciones financiadas con Cashea, cobranza, iniciales, modelos de teléfonos vendidos, desempeño de ventas y conciliación de pagos. |
| [**`clientes_asoc/`**](file:///C:/Users/YARBED/Desktop/Entornos/clientes_asoc/README.md) | **Power BI (`Envio de productos.pbix`) + Python** | Ingesta de despachos / Base de datos comercial | **Logística de Envíos y Clientes Asociados**: Tablero interactivo de seguimiento de despachos de mercancía, tiempos de entrega, volumen de bultos y cumplimiento por cliente asociado. |
| **`consulta_clientes_almayor_grafana.sql`** | **Telemetría SQL para Grafana** | PostgreSQL Directo (`sales_operation`, `sellers`, `clients`) | Query optimizada para conectar tableros en **Grafana**, monitoreando en tiempo real las ventas diarias al mayor, tasa de cambio del BCV aplicada y rendimiento por asesor. |

---

### 2. ⚙️ Motores ETL y Extracción de Base de Datos

* **[`etl_db/`](file:///C:/Users/YARBED/Desktop/Entornos/etl_db/README.md)**:
  * Motor central de extracción masiva conectado a la base de datos `cadm_j5004625301`.
  * Utiliza `SQLAlchemy` y `psycopg2` con lectura por lotes (chunks de 5.000 a 10.000 registros).
  * Convierte tablas relacionales transaccionales a formato columnar **Apache Parquet**, reduciendo el tamaño en un 85% y acelerando las consultas analíticas hasta 50x.
* **`generar_reporte_almayor.py`**:
  * Script de conexión directa a PostgreSQL para consolidar ventas al mayor, cálculo automático de la tasa de cambio en USD del día de emisión, y generación de libros Excel estilizados con tablas dinámicas y formato condicional.
* **`reporte_clientes_nuevos_recurrentes.py`**:
  * Algoritmo de clasificación de cohortes de clientes (Nuevos vs. Recurrentes) por vendedor y mes, calculando tasas de retención y recompra.

---

### 3. 📊 Módulos de Analítica y Estadísticas Especializadas

* **`almayor_stats/`**: Estadísticas de ventas al mayor, categorización de productos y exportación de reportes ejecutivos (`almayor.xlsx`).
* **`cashea_stats/`**: Desglose transaccional del método de pago Cashea, tickets promedio y comportamiento de compra.
* **`clientes_almayor/`**: Segmentación de cartera de clientes y asignación automática de clientes activos/inactivos a la fuerza de ventas activa.
* **`facturaciones/`**: Auditoría de facturación, limpieza de reportes en PDF (`limpieza_pdf`) y conciliación fiscal.
* **`kpi_monthly/`**: Consolidación mensual de KPIs corporativos comparativos entre ventas detal y ventas al mayor.
* **`metas_rrhh/`**: Monitoreo de cumplimiento de metas de ventas para cálculo de comisiones y métricas de talento humano (`resultados.sql`).
* **`mrw_cashea/`**: Conciliación y rastreo de envíos realizados mediante encomiendas **MRW** para compras con financiamiento.
* **`sending_zoom/`**: Integración y seguimiento de guías de despacho enviadas a través del operador logístico **ZOOM**.

---

## 🚀 Guía de Uso y Ejecución

### 1. Requisitos Previos
* **Python 3.11+**
* Gestor de paquetes ultrarrápido **`uv`** (o `pip`)
* Acceso de red local a la base de datos PostgreSQL (`192.168.91.131:5433`)

### 2. Ejecución Automatizada de Todo el Flujo
Para ejecutar la extracción completa de la base de datos y la regeneración de todos los reportes analíticos, ejecuta el archivo batch:

```powershell
.\Entornos_run.bat
```

Este script procesa secuencialmente:
1. `etl_db.py`: Extracción y actualización de archivos Parquet desde PostgreSQL.
2. `cashea_stats.py`: Estadísticas de financiamientos Cashea.
3. `sending_zoom.py`: Métricas de envíos Zoom.
4. `kpi_monthly.py`: Consolidación de KPIs mensuales.
5. `almayor_stats.py`: Estadísticas de clientes y ventas al mayor.

### 3. Uso de los Web Dashboards
1. Navega a `dashboard_clientes/` o `dashboard_40d/`.
2. Abre `index.html` en cualquier navegador web moderno (Chrome, Edge, Opera, Firefox).
3. Permite cargar directamente los datos consolidados en formato `.csv` o `.xlsx` para visualizar métricas en tiempo real.

---

## 🔒 Buenas Prácticas de Seguridad y Configuración
* Las credenciales locales y contraseñas de conexión no se incluyen en el repositorio público (controladas mediante `.gitignore`).
* Los archivos binarios pesados (`.parquet`, `.pbix`, `.xlsx`) se gestionan localmente como capas de datos temporales/marts para optimizar el almacenamiento del repositorio Git.
