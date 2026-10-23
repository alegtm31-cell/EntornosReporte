# 🔄 ETL DB: Pipeline Central de Extracción PostgreSQL a Parquet

Motor principal de extracción, transformación y carga (ETL) que alimenta todo el ecosistema de analítica, Power BI y dashboards del departamento comercial.

---

## 🎯 Arquitectura y Funcionamiento

* **Conexión a la Base de Datos**:
  * Motor: PostgreSQL 14+
  * Protocolo: `postgresql+psycopg2` vía `SQLAlchemy`
  * Parámetros de codificación: Compatibilidad dual con `latin1` (heredado de Saint ERP) y `UTF8`.
* **Procesamiento por Lotes (Chunking)**:
  * Las consultas masivas (tablas con cientos de miles de registros como `sales_operation_details` y `sales_operation`) se procesan en lotes de **5.000 a 10.000 registros** mediante `pyarrow.parquet.ParquetWriter`.
  * Esto garantiza un uso mínimo y estable de memoria RAM sin sobrecargar el servidor de base de datos.
* **Almacenamiento en Capa de Datos (Data Lake Local)**:
  * Exporta los datos al directorio `Stored Data Parquet` en formato Apache Parquet con compresión Snappy.
  * Tablas generadas:
    * `almayor_sellers.parquet`: Catálogo de vendedores y asignación de estatus activo/inactivo.
    * `almayor_clients.parquet`: Maestro de clientes con datos de contacto, RIF y región.
    * `almayor_detail_sales.parquet`: Detalle línea a línea de ventas, productos y montos.
    * `provinces.parquet`: Catálogo de división político-territorial.

---

## 🚀 Ejecución

Para ejecutar la extracción completa de la base de datos:
```bash
uv run python etl_db.py
```
O ejecutando el proceso global con:
```bash
..\Entornos_run.bat
```
