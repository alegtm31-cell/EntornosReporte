# 💳 Finance Cashea: Pipeline ETL y Dashboard Power BI

Solución integral de analítica y monitoreo para las ventas realizadas mediante financiamiento con **Cashea**. Combina un pipeline ETL en Python de alto rendimiento y un modelo analítico en **Power BI (`KPI Cashea.pbix`)**.

---

## 🎯 Componentes del Proyecto

1. **Pipeline ETL (`etl_db_finance_cashea.py`)**:
   * Conecta con la base de datos empresarial **PostgreSQL** (`cadm_j5004625301`).
   * Extrae transacciones asociadas al tipo de pago Cashea, separando monto de inicial y financiamiento diferido.
   * Cruza facturación con el catálogo de equipos celulares vendidos bajo modalidad financiada.
   * Exporta datasets limpios y comprimidos en formato **Apache Parquet** dentro del directorio `data/`:
     * `sales.parquet`: Ventas totales y operaciones generales.
     * `financiamientos.parquet`: Detalle de créditos otorgados.
     * `pays_cashea.parquet`: Pagos e iniciales recibidas.
     * `phones_cashea.parquet`: Modelos, marcas y seriales de smartphones vendidos.
     * `productos_cashea.parquet`: Catálogo de productos disponibles con Cashea.
     * `calendario.parquet`: Tabla de dimensiones temporal para análisis de series de tiempo.

2. **Dashboard Ejecutivo Power BI (`KPI Cashea.pbix`)**:
   * Conexión directa a los archivos Parquet optimizados.
   * Modelado estrella con relaciones DAX avanzadas.
   * Visualización de métricas clave:
     * **GMV (Gross Merchandise Value)** financiado por Cashea vs. pago de contado.
     * **Ticket promedio** de compra y cuota inicial recolectada.
     * **Ranking de modelos de teléfonos más vendidos**.
     * **Tendencias semanales y mensuales** de colocación de financiamiento.

---

## 🚀 Ejecución y Actualización

1. **Actualizar Datos desde PostgreSQL**:
   ```bash
   uv run python etl_db_finance_cashea.py
   ```
2. **Actualizar el Dashboard Power BI**:
   * Abre `KPI Cashea.pbix` en Power BI Desktop.
   * Haz clic en **Actualizar** (Refresh) en la pestaña Inicio. Power BI recargará los datos instantáneamente desde los archivos `.parquet`.
