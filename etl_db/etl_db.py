# %%
# Importar librerias
print('Leyendo librerias')
import psycopg2
from psycopg2 import OperationalError, sql
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL
import urllib.parse
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import time
print("Librerias leidas") 

# %%
# Conexión con sqlalchemy
print('Estableciendo conexion')
drivername="postgresql+psycopg2" # o "postgresql+psycopg"
username="postgres"
host="192.168.91.131"
port="5433"
database="cadm_j5004625301"
#CHRYSTAL
password=r"""Soloyo1234*-"""
url_nopassword = f"{drivername}://{username}@{host}:{port}/{database}"
engine = create_engine(
    url_nopassword,
    connect_args={
        "password": password,
        "client_encoding": "latin1"
    }
)
engine_2 = create_engine(
    url_nopassword,
    connect_args={
        "password": password,
        "client_encoding": "UTF8"
    }
)
print("Conexion establecida")

# %%
# Definición de los vendedores al mayor
query_seller = text("""
SELECT
 code,
 description,
 CASE
  WHEN code IN (
 '25625528', '25411189', '23225823', '22974980', '281502778', '24057112', '28386523'
  ) THEN 'ACTIVOS'
  ELSE 'INACTIVOS'
 END AS status_seller
FROM public.sellers
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL MAYOR\almayor_sellers.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_seller, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Vendedores al mayor exportados")

# %%
# Definición de los usuario
query_users = text("""
SELECT
code,
description
FROM users
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\users.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_users, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Usuarios exportados")

# %%
# Definición de los estatus de los clientes
query_status = text("""
SELECT
 code,
 description
FROM public.status
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\status.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_status, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Estatus de los clientes exportados")

# %%
# Definición de los estados del país
query_provinces = text("""
SELECT
 code,
 description,
 CASE
  WHEN code IN ('10','14','16') THEN 'CAPITAL'
  WHEN code IN ('04','07','08') THEN 'CENTRAL'
  WHEN code IN ('11','13','23') THEN 'CENTROCCIDENTAL'
  WHEN code IN ('01','06','09') THEN 'GUAYANA'
  WHEN code IN ('18') THEN 'INSULAR'
  WHEN code IN ('15','21','22') THEN 'LOS ANDES'
  WHEN code IN ('03','05','12','19') THEN 'LOS LLANOS'
  WHEN code IN ('02','17','20') THEN 'NORORIENTAL'
  WHEN code IN ('24') THEN 'ZULIANA'
  ELSE 'OTROS'
 END AS region_province
FROM public.provinces
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\provinces.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_provinces, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Estados del pais exportados")

# %%
# Definición de los países
query_countries = text("""
SELECT 
 code, 
 description
FROM public.countrys
;                    
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\countries.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_countries, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Paises exportados")

# %%
# Definición de los productos, sus marcas y departamentos
query_products = text("""
SELECT 
 code, 
 description, 
 department, 
 mark,
 status
FROM public.products
;                    
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\products.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_products, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Productos exportados")

# %%
# Definición= de los depositos y tiendas
query_stores_stocks = text("""
WITH stocks AS (
SELECT
product_code,
store,
stock
FROM products_stock
),
stores AS (
SELECT
*,
CASE
 WHEN LEFT(description,3) = 'DEP' THEN 'DEPOSITOS'
 WHEN LEFT(description,6) = 'TIENDA' THEN 'TIENDAS'
 ELSE 'ANULAR'
END AS store_type
FROM store
),
stores_selected AS (
SELECT
*
FROM stores
WHERE store_type <> 'ANULAR'
)
SELECT
sk.product_code,
sk.stock,
ss.code,
ss.description,
ss.store_type
FROM stocks sk
INNER JOIN stores_selected ss
ON sk.store = ss.code
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\stores_stocks.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_stores_stocks, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Existencias por tiendas y depositos exportadas")

# %%
# Definición de los departamentos
query_department = text("""
SELECT 
 code, 
 description, 
 father_department
FROM public.department
;                    
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\department.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_department, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Departamentos exportados")

# %%
# Definición de los departamentos-padre
query_father_department = text("""
WITH father AS (
SELECT DISTINCT(father_department)
FROM public.department
ORDER BY father_department
),
son AS (
SELECT
code,
description,
father_department
FROM public.department d
)
SELECT
f.father_department,
s.description
FROM father f
INNER JOIN son s
ON f.father_department = s.code
ORDER BY f.father_department
;                  
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\father_department.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_father_department, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Departamentos padre exportados")

# %%
# Histórico de tasas
query_coin_history = text("""
WITH full_dates AS (
 SELECT generate_series('2022-10-02'::date, DATE(NOW()), '1 day'::interval)::date AS fecha
),
tax_dates AS (
SELECT
 register_date,
 register_hour,
 sales_aliquot
FROM coin_history
WHERE
 main_code = '02'
 AND register_date >= '2022-10-02'
),
full_taxes AS (
SELECT
 f.fecha AS fecha_tasa,
 t.register_date,
 t.register_hour AS hora_tasa,
 t.sales_aliquot AS tasa,
 COUNT(t.sales_aliquot) OVER (ORDER BY f.fecha, t.register_hour) AS grupo
FROM full_dates f
LEFT JOIN tax_dates t
ON f.fecha = t.register_date
)
SELECT
 fecha_tasa,
 hora_tasa,
 COALESCE(
  tasa,
  FIRST_VALUE(tasa) OVER (PARTITION BY grupo ORDER BY fecha_tasa, hora_tasa)
 ) AS tasa_completa
FROM full_taxes
WHERE fecha_tasa BETWEEN '2022-10-02' AND CURRENT_DATE - INTERVAL '1 day'
;                  
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\coin_history_correccion.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_coin_history, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Historico de tasas exportados")

# %%
# Facturaciones de Cashea
query_cashea_bills = text("""
WITH facturas_cashea AS (
SELECT
emission_date AS fecha,
register_hour AS hora,
document_no AS factura,
user_code AS usuario
FROM sales_operation
WHERE
document_no ~ '^X[0-9]+$'
AND emission_date >= '2026-08-11'
),
full_dates AS (
 SELECT generate_series('2026-08-11'::date, DATE(NOW()), '1 day'::interval)::date AS fecha
),
tax_dates AS (
SELECT
 register_date,
 register_hour,
 sales_aliquot
FROM coin_history
WHERE
 main_code = '02'
 AND register_date >= '2026-08-11'
),
full_taxes AS (
SELECT
 f.fecha AS fecha_tasa,
 t.register_date,
 t.register_hour AS hora_tasa,
 t.sales_aliquot AS tasa,
 COUNT(t.sales_aliquot) OVER (ORDER BY f.fecha, t.register_hour) AS grupo
FROM full_dates f
LEFT JOIN tax_dates t
ON f.fecha = t.register_date
),
date_coin_full AS (
SELECT
 fecha_tasa,
 hora_tasa,
 COALESCE(
  tasa,
  FIRST_VALUE(tasa) OVER (PARTITION BY grupo ORDER BY fecha_tasa, hora_tasa)
 ) AS tasa_completa
FROM full_taxes
WHERE fecha_tasa >= '2026-08-11'
),
facturas_validadas AS (
SELECT
 f.factura,
 f.usuario,
 f.fecha,
 dc.fecha_tasa,
 f.hora,
 dc.hora_tasa,
 dc.tasa_completa,
 CASE
  WHEN dc.hora_tasa IS NULL THEN 0
  WHEN f.hora > dc.hora_tasa THEN 1
  ELSE 0
 END AS tasa_validada,
 CASE
  WHEN dc.hora_tasa IS NULL THEN NULL
  WHEN f.hora > dc.hora_tasa THEN tasa_completa
  ELSE NULL
 END AS tasa_corregida
FROM facturas_cashea f
INNER JOIN date_coin_full dc
ON f.fecha = dc.fecha_tasa
),
facturas_secuenciadas AS (
SELECT
 factura,
 fecha,
 hora,
 tasa_corregida,
 ROW_NUMBER() OVER (PARTITION BY factura ORDER BY tasa_validada DESC, fecha ASC, hora ASC) AS vn,
 COUNT(tasa_corregida) OVER (ORDER BY fecha, hora) AS gp
FROM facturas_validadas
),
facturas_identificadas AS (
SELECT
*
FROM facturas_secuenciadas
WHERE vn = 1
)
SELECT 
fecha,
hora,
factura,
COALESCE(
  tasa_corregida,
  FIRST_VALUE(tasa_corregida) OVER (PARTITION BY gp ORDER BY fecha, hora),
  NULL
) AS tasa_autocompletada
FROM facturas_identificadas
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\cashea_bills_correccion.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_cashea_bills, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Facturaciones de cashea exportadas")

# %%
# Facturas detalladas de Cashea
query_cashea_bills_details = text("""
WITH facturaciones_cashea AS (
SELECT
so.document_no AS factura,
sd.amount AS unidad,
sd.total_net AS monto,
sd.code_product AS producto,
us.description AS vendedor
FROM sales_operation so
INNER JOIN sales_operation_details sd
ON so.correlative = sd.main_correlative
LEFT JOIN users us
ON us.code = so.user_code
WHERE
so.document_no ~ '^X[0-9]+$'
AND so.emission_date >= '2026-08-11'
)
SELECT
factura,
unidad,
monto,
producto,
vendedor
FROM facturaciones_cashea
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\cashea_bills_details.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_cashea_bills_details, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Facturas detalladas en cashea exportadas")

# %%
# Financiamientos de cashea
query_finance_cashea = text("""
WITH pay_cashea AS (
SELECT
 w.main_correlative,
 s.document_no AS factura,
 w.amount AS monto_dolar,
 w.amount_local AS monto_bs,
 w.emission_date AS fecha
FROM way_to_pay_details w
INNER JOIN way_to_pay wp
ON w.main_correlative = wp.correlative
INNER JOIN sales_operation s
ON wp.correlative_related = s.correlative
WHERE
 w.type_operation = 'TRANSFER'
 AND w.coin_code = '06'
 AND w.emission_date BETWEEN '2026-04-01' AND (CURRENT_DATE - INTERVAL '1 day')
),
pays_coin AS (
SELECT
 fecha,
 factura,
 SUM(monto_bs) AS monto_bs,
 SUM(monto_dolar) AS monto_dolar
FROM pay_cashea
GROUP BY fecha, factura
)
SELECT
 fecha,
 factura,
 monto_dolar,
 ROUND((monto_bs/monto_dolar)::NUMERIC, 2) AS tasa_factura
FROM pays_coin
ORDER BY fecha
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\finance_cashea.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_finance_cashea, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Financiamientos de cashea exportados")

# %%
# Pagos realizados con cashea
query_pays = text("""
WITH pay_cashea AS (
SELECT
 s.document_no
FROM way_to_pay_details w
INNER JOIN way_to_pay wp
ON w.main_correlative = wp.correlative
INNER JOIN sales_operation s
ON wp.correlative_related = s.correlative
WHERE
 w.type_operation = 'TRANSFER'
 AND w.coin_code = '06'
 AND w.emission_date BETWEEN '2026-04-01' AND (CURRENT_DATE - INTERVAL '1 day')
ORDER BY w.emission_date, s.document_no
),
pay_customer AS (
SELECT
 s.document_no,
 w.type_operation,
 w.coin_code,
 w.emission_date,
 w.amount,
 w.amount_local,
 CASE
  WHEN w.type_operation = 'CHANGE' THEN 'DEUDA'
  ELSE 'SALDO'
 END resume
FROM way_to_pay_details w
INNER JOIN way_to_pay wp
ON w.main_correlative = wp.correlative
INNER JOIN sales_operation s
ON wp.correlative_related = s.correlative
INNER JOIN pay_cashea p
ON s.document_no = p.document_no
WHERE 
 w.emission_date BETWEEN '2026-04-01' AND (CURRENT_DATE - INTERVAL '1 day')
 AND NOT (
  w.type_operation = 'TRANSFER'
 AND w.coin_code = '06'
)
),
pay_bills AS (
SELECT
document_no AS factura,
resume,
emission_date AS fecha,
SUM(amount_local) AS monto_bs
FROM pay_customer
GROUP BY document_no, resume, emission_date
),
negative_income AS (
SELECT
factura,
fecha,
monto_bs AS deuda
FROM pay_bills
WHERE
resume = 'DEUDA'
),
positive_income AS (
SELECT
factura,
fecha,
monto_bs AS saldo
FROM pay_bills
WHERE
resume = 'SALDO'
)
SELECT
p.fecha,
p.factura,
CASE
 WHEN n.deuda IS NULL THEN p.saldo
 ELSE p.saldo-n.deuda
END saldo_total
FROM positive_income p
LEFT JOIN negative_income n
ON p.factura = n.factura
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\pays_cashea.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_pays, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Pagos realizados por cashea exportados")

# %%
# Ventas de telefonos por cashea
query_phones_cashea = text("""
WITH pay_cashea AS (
SELECT
 w.amount AS monto_dolar,
 w.amount_local AS monto_bs,
 EXTRACT(MONTH FROM w.emission_date) AS mes,
 sd.amount AS cantidad,
 p.mark AS marca
FROM way_to_pay_details w
INNER JOIN way_to_pay wp
ON w.main_correlative = wp.correlative
INNER JOIN sales_operation s
ON wp.correlative_related = s.correlative
INNER JOIN sales_operation_details sd
ON s.correlative = sd.main_correlative
INNER JOIN products p
ON sd.code_product = p.code
WHERE
 w.type_operation = 'TRANSFER'
 AND w.coin_code = '06'
 AND w.emission_date BETWEEN '2026-04-01' AND (CURRENT_DATE - INTERVAL '1 day')
 AND UPPER(LEFT(p.description,8)) = 'TELEFONO'
 AND s.operation_type = 'BILL'
 AND s.client_name <> 'ANULADO'
)
SELECT
 marca,
 mes,
 SUM(monto_dolar) AS monto_dolar,
 SUM(cantidad) AS cantidad
FROM pay_cashea
GROUP BY mes, marca
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\phones_cashea.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_phones_cashea, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Telefonos vendidos por cashea exportados")

# %%
# Definición de clientes nuevos al mayor
query_new_clients = text("""
WITH clientes_nuevos AS (
SELECT
emission_date,
register_hour,
client_code,
ROW_NUMBER() OVER(PARTITION BY client_code ORDER BY emission_date ASC, register_hour ASC) AS rowid
FROM sales_operation
WHERE
operation_type = 'BILL'
AND client_name <> 'ANULADO'
AND user_code = 'ALMAYOR'
)
SELECT
emission_date,
client_code
FROM clientes_nuevos
WHERE rowid = 1 AND emission_date >= '2026-01-01'
GROUP BY emission_date, client_code
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\new_clients.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_new_clients, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Clientes nuevos exportados")

# %%
# Definición de clientes al mayor
query_clients = text("""
WITH datescluster_almayor_clients AS (
SELECT
c.code,
c.status,
c.client_group,
c.province,
c.country,
c.phone,
c.description,
c.address,
c.created_at,
c.created_by,
c.created_in,
ROW_NUMBER() OVER(PARTITION BY c.code ORDER BY s.emission_date ASC, s.register_hour ASC) AS "rowid",
EXTRACT(YEAR FROM emission_date) AS year_emission,
EXTRACT(MONTH FROM emission_date) AS month_emission,
EXTRACT(YEAR FROM NOW()) AS year_now,
EXTRACT(MONTH FROM NOW()) AS month_now
FROM public.clients c
INNER JOIN public.sales_operation s
ON c.code = s.client_code
WHERE
s.user_code = 'ALMAYOR'
AND s.client_name <> 'ANULADO'
AND s.operation_type = 'BILL'
),
-- CTE que define y entrega la segmentacion de los clientes entre recurrentes, nuevos del año y nuevos en los ultimos 2 meses (aprox 2.5k clientes)
cluster_almayor_clients AS (
SELECT
d.code,
d.status,
d.client_group,
d.province,
d.country,
d.phone,
d.description,
d.address,
d.created_at,
d.created_by,
d.created_in,
CASE
 WHEN d.code = '00' THEN 'GENERICO'
 WHEN d.year_emission < d.year_now THEN 'RECURRENTES'
 -- "month_now-2" refleja el lapso de 2 meses atrás a la fecha actual
 WHEN d.year_emission = d.year_now AND (d.month_now-2) <= d.month_emission THEN 'NUEVOS A 2 MESES'
 ELSE 'NUEVOS AL AÑO'
END AS case_client
FROM datescluster_almayor_clients d
WHERE rowid = 1
),
-- CTE que entrega la lista de clientes al mayor no duplicados y no gestionables (aprox 1.3k clientes)
no_trash_clients AS (
SELECT
code,
CAST('Cliente no basura' AS VARCHAR(55)) AS status_client
FROM cluster_almayor_clients
WHERE code NOT IN (
 '84587877', 'E-84587877', 'V199250759', '24883911', '8819029', 'V212472618',
 'HASSAN CITY MUNDO', '12717075', '11059190', '5000036779', '13041794', '179897624',
 '17989762', '27377859', 'E461883', '27979975', '25583193', '18474495',
 '184744950', 'JOSE NAVARRETE', 'JOSE NAVAREYTE', '6948077', '26040898',
 '17243990', 'J-294107796', '14100381', '19470697', 'J504412562', '27275280',
 '17857501', '18573440', '16995746', '9494368', 'J41237909-7', '27879044', 
 '17556636', '248929384', '10379262', '14571708', '18637343', 
 '20558701', '18214910', 'J22316353-6', 'J-412747606', '26012291',
 '25317642', '12941806', '1121855004', '31344121', '23687338', '27472787',
 '27309008', 'P309898', '29583193', '15685562', '19565106', '17106204',
 '27136110', 'J413197111', 'J500837674', '0011650353', '17024553',
 '182553561', '20522218', '26838287', 'CITY CELL GSM',
 'J-309950541', 'J40974590', 'J412786059', 'J-412786059', 'J-500211228',
 'JORRGE MORA', 'JORGE MORA', 'TODOCELL', '407031228', '98012908331',
 '17757892', '429470', 'J503898119', '28708035', '19941729', '-J40703122-8',
 '27519497', 'V-14346553', '31416375-0', 'J411942596', '27941720', 'J297733337',
 '305822840', '264544444', '13496441', '21001044', '28024146', '84610888', 
 '27373717', '20753333', 'E96033008897', '448357', '12898731', '16939574', 
 'GERLINA DIGITEL', 'LUIS TUCUPITA', 'JEAN HABIBI', 'MIGUEL SOSA', 'NELTAGE',
 'GILBERTO', 'SALIM', 'WILLI ', 'JOSE METROCENTER', 'DANIEL GONZALES', 'EDIBEL',
 'ROLFER RUIZ', 'BLACK TECH', 'MIGUEL', 'LUIS FLORES', 'ISABEL', 'FIDEL GARCIA',
 'SHADY', 'KARIM ESTABA', 'ISAIAS', 'LILLIAM ', 'HECYELI', 'DANIELA  URBINA',
 'FRANCYS GOCHOS', 'FELIPE RADIO', 'MARGARITA', 'SHAFIK CHARCHAR', 'MARI CARMEN',
 'PCELL', 'JOSE MANUEL', 'MAQUINAS FISCSLEA', 'JOSE LLANERO', 'EDGAR GOMEZ',
 'DAVID ', 'DANIEL GONLAEZ', '0120', 'CARLOS SALINAS', 'SALINA', 'RAUL',
 'JULIO', 'BIT MERCADO', 'TECHNOLOGY', 'WILLY', 'VICTOR ', 'JOSE CABELLO',
 'BITMERCADO DIGITAL', 'GUSTAVO GARCIA', 'FELIPE', '1', '01', 'GILBERTO ', 
 'FELIPE HERNANDEZ', 'TALAL EL VISTAZO', 'CELUYMAS', 'ALEJANDRO',
 'DEIVYS', 'CHINO ', 'SHARIS ASAF', 'WILMER', 'SAUL MARQUEZ', 'ANAMILETH',
 'FELIX GONZALEZ', 'GOCHOS', 'MIGUEL VARGAS', 'DARY', 'LILLIAM',
 'CLIENTE BARINAS', 'ANTHONI', 'AL MAYOR', 'MARTIN LEDEZMA',
 'JOHAN ZAMBRANO', 'TYL CELULARES', 'COMPUGRAPHI', 'AMER ABDUL',
 'ISAMAR', 'SABRINA', 'ZOL', '3429', 'MARCO HAPPY PHONE', 'CARLOS PADRON',
 'REFIGERACION ', 'V19530953', 'V18834223', 'V25934937', 'V16659276', 'V20874867',
 '24302364', 'V21071357', '27068256', '31978825', 'V27858239', 'V15795106',
 'J314850520', 'J411090727', 'J404794344', 'V28331830', 'V26838287', 'V22502862',
 'J506955547', 'J506856395', 'J504227463', 'V12044804', '21207852', 'J200001178',
 'V30964722', 'V25740802', 'J298990023', 'J502771077', 'J317523849', 'V31024020',
 'V12607697', 'V30806369', 'V18827324', 'V26128170', 'V28595519', 'V27239854',
 '14393669', '24656062', 'J310141432', 'V16354731', 'V10040207', '20786813',
 'V16054354', 'V29875806', 'V32777701', 'V17075167', 'V26888750', 'V28231382',
 'V26717255', 'J410002875', 'V26700028', 'J411078050', 'J299339652', 'J506513595',
 '27975952', '19625820', 'V26529754', '18616761', 'V23691821', 
 'V23607704', 'V15648751', ' 25566789', '26369997', 'J400869501', 'V080665853',
 'E473634', '13385046', 'R005259', 'L934926', 'V79491744', 'P564520', 'E85000632',
 '26919619', 'V8747970', '27406100', 'V30810086', '19008932', 'V138047993',
 '19088843', 'V176172777', 'V201234898', 'V175003335', 'P839031', 'V135872942',
 'V178585866', 'R485271', 'V171613015', 'V26012291', 'V27693035', 'V296795891',
 '17268497', 'L369198', 'J505293591', 'V15587538', '28518643', '19505967',
 '29925089-9', '223163536', 'V27529171', '21505974', '17907504', 'P01269530',
 'J090270000', '504160695', 'J408984865', '133636720', '17371845', 'J412793330',
 'A00774858', 'J503501928', '18639188', '178315648', 'J411697826', '413220660',
 '19958427', '502140069', '0J504758817', 'V191914615', 'J40401568980', '17691521-4',
 'J003258458', '1252488', '27460468', '25846833', 'V17303797', '27363491',
 '17073309', '84569847', '18204489', '20096422', '25367246', '20717124',
 'V24905920', '27107853', '28164818', '30188122', '24459089', 'V24459089',
 'V17840043', '30300266', 'V30815339', 'J406977349', 'V4835504', '27789444',
 'V27646342', 'J-400340756', 'J504926124', '11681227', 'V20616127', '31101811',
 '19228275', '19360291', '254545569', '26482246', '501356408', 'J-29459455-7',
 'J-304820038', 'J-307980486', 'J-30798048-6', 'J-313678295', 'J31546666-0',
 'J-315814889', 'J40034075-6', 'J40473769', 'J-410560037', 'J-50064113-3',
 'J-501356408', 'J50150936-0', 'J-502651411', '27000289', '18745139',
 '29615892', '27819019', '27268275', 'M571832', '29948893', 'V28554461', '28465092',
 'M152704', '19527235', 'M263615', 'V267494416', '473634', '25656247', '27309394',
 '29665857', '19740591', 'L544025', '043266299', '34174054', '22279438', '25286352',
 '23916461', '8468666', '19087122', '19729842', 'J41285716', '14166186',
 '18255356', '12160525', '19607353', '31960824', '32067021', 'V242068110', 
 '21057142','199161130', '19916130', 'V239871778', '29702183', '25130703',
 '24705985', '24931613', '28745306', '22283370', '18328622', '13111439', 'M705774',
 '26741745', 'V214140256', '30157871', '8509642', '18167399', '19759755', '30471395',
 'V14679172', '505216570', '6366732', '16701176', '19829628', 'L926934', '27561806',
 '25260788', '10281031', '26738426', '28058541', '473389', '6929178', '13308277',
 '18474950', '30510817', 'E473389', '18912651', 'J412874080', '18924508', '24501294',
 '14183735', 'L318357', 'J502431462', 'J408478277', 'J296802394', '17871674', 
 'M311026', '27309325', '12607697', '88032529484', '14746742', '20531884', '26440486',
 '20799580', '24073867', '20615445', '17609616', '17108050', 'E445356', '26620255',
 '29948014', '30155867', '20330769', '17504457', 'V076203483', '16012110', 'P407242',
 '18756137', '25696753', '14552036', '25658361', 'V26444516', 'V25813800', 
 '27297101', 'V208042803', '25504442', 'V26942692', '17106606', '30063446', 
 'J506111616', '14872037', '16095518', 'E446025', '17078676', 'E 397533', '31998095',
 '18018072', '17587128', '18959761', '20866516', '20886516', '25223481', '13986555',
 '19361240', '22888629', '18394206', '24900643', '10039354', 'V280632771',
 '18326715', '184171803', '14949587', '17622875', '450948', '20781751', '84404875',
 '26176087', '313095680', '16531316', '29893428', 'R040230', 'E411399', '13114595',
 '6448327', 'K4090007', '18586347', '28423033', 'J002453281', 'J500381980',
 'E428469', '12563438', '31506840', '15757938', '19455257', 'L235164', '22909137',
 '14194731', '20362894', '26061872', '15023744', '25417213', '19954425', '10237554',
 '29960417', '84558211','MUNDO MOVIL', '502617256', '25524432',
 'V18978038', 'V27918677', '15962833', '24806372', '84498242', 'E84498242',
 'J303077978', '26818426', '401838090', 'J40948768', 'J50064113-3', 'J500636750',
 '26161979', 'V31960824', 'V17045690', '17211114', '22778495',
 'J504395544', 'J306842675', '26454444', '22561766', '25454569', '26482946',
 '30111566', '17584476', '11166808', 'J501852596', 'J403074461', '25839812',
 '17105917', 'J504615510', '26397667', '13376244', '19223101',
 'J505662392', 'J505645730', '19818450', '19152114', '16682084', '106972105',
 '23616721', '30563418', '29533543', 'J402648960', '19228277', '17599812',
 '24795636', '27051927', 'J500445989', '20789378', 'J505434993',
 'J404204300', 'J506312107', '31263062', '20365422', '21251630',
 '15269332', '24435639', 'V22398928', '10539192', 'V25646118', '17605414',
 '19899789', '19740731', '23607176', '13326021', 'V23749010', '29549150',
 '12790006', '25252035', '18018073', '15152662', 'V030786234',
 '18236975', '32296618', '18586437', '27243396', 'J411536393', '16531317',
 '21011773', '19865354', '24578026', '20716136', '10036573', '20430101',
 '23951260', '16450184', 'V14566916', 'V27558741', 'J410110340', 'J30381261-9',
 '25361162', '19163156', '19500873', '22316353', '37023541', '23729983',
 '26430769', '0025350604', '158520441', '184661585',
 '20233708', '26497362', '29288320', '25566789', '309950541', '297235450',
 '31360909', '400648505', '401568990', '404204300', '412501550', '412786059',
 '500132905', '502466452', '502552880', '503565063', 'J-294298834',
 'J2958663458', 'J313203203092', 'J31572738-2', 'J-400729734', 'J41276970',
 'J40699595-6', 'J-412874080', 'J503655063', 'J-50412585-7', 'P:1031798',
 'V17935226', '012065512', '10381743',
 '10500573', '11161842', '11407130', '11817065', '12163578', '12187555', '12721229',
 '12776236', '13109063', '13125211', '13155232', '13319386', '13533020', '13620856',
 '13871231', '14057406', '14552038', '14838248', '14897735', '15338067', '15342343',
 '15443490', '15664502', '15832230', '16131738', '16134034', '16224714',
 '16225862', '16343224', '16392279', '16555714', '16704494', '16813517', '16944316',
 '17139996', '17255969', '17393765', '17476309', '17519216', '17622359',
 '17692418', '17721225', '17822117', '17823166', '18050629', '18333169', '18350699',
 '18741895', '18786667', '19243203', '19565663', '19738226', '19805529', '19887122',
 '20032903', '20032938', '20080166', '20087901', '20117786', '20269132', '20362844',
 '20636344', '21018334', '21125730', '21194538', '21263001', '21353996', '21375626',
 '21615027', '22036707', '22041680', '22215460', '23626357', '24216013', '24218569',
 '24348884', '24753633', '24788074', '24841807', '25213645', '25225147', '25350604',
 '25615952', '25926281', '2598570', '26217680', '26296544', '26351762', '26454137',
 '26480881', '27027845', '27028475', '27223673', '27276234', '27344456', '27472768',
 '27680628', '27827275', '27908160', '28421185', '28482505', '28672113', '29776987',
 '29798985', '29828336', '30031036', '30199611', '30291660', '30335833', '30553858',
 '30558702', '30579881', '30683728', '30777562', '307838140', '31194976', '31368936',
 '31401282', '31852048', '33913128', '9412975', '9494361', '9966927', 'J176915214',
 'J293939240', 'J294095550', 'J-294594557', 'J298203360', 'J299615200',
 'J304611078', 'J305232806', 'J307034238', 'J308610089', 'J310445397',
 'J315789140', 'J315943867', 'J317307615', 'J400223685', 'J400319285',
 'J401244190', 'J401815685', 'J403261504', 'J403716064', 'J403831203', 'J404711724',
 'J405069651', 'J405204222', 'J405310030', 'J405860740', 'J406006343', 'J406330540',
 'J406399116', 'J407277898', 'J408374455', 'J408527120', 'J409829456', 'J410528079',
 'J412012738', 'J412402668', 'J412839969', 'J500249144', 'J500489307', 'J500543921',
 'J501075883', 'J501254834', 'J501381836', 'J-50140771-1', 'J501889368', 'J502389695',
 'J502552880', 'J502614630', 'J502991875', 'J503608331', 'J50415075-4', 'J504313343',
 'J504395650', 'J504764744', 'J504904791', 'J505140850', 'J-50546790-5', 'J505772821',
 'J506335735', 'J507228924', 'J840129004', 'V14673104', 'V20105949', 'V26358451',
 'V26683938', 'V27427963', 'V27513925', 'J500441700', '148215232',
 'E402104', 'E80397597', 'L345553', 'E277988152', 'K237544', 'L554025',
 'ANTONI ', 'L890261', 'BETZALI ', 'P278182', 'DAILUZ ', 'DARY ', 'E398107',
 'M518545', 'PK716825', 'L011243', 'I448357', 'E029602708',
 'L621271', 'M175587', 'JUAN CARLOS ', 'E82062526', 'E396604', 'E397533',
 'L627477', 'E81084272', 'P109468', 'N256287', 'P839041', 'L211048', 'L855766',
 'L454003', 'E449477', '21|615027', ' L235164', 'L650670',
 'E82359053', 'E516905', 'E419356', 'P178371', '306967532', '83434008',
 'J5022912029', 'J503655053', '25418268', 'J-50124374-3', '518545', '501581',
 '19569872', 'J406316386', '277298851', '297298851', 'J-502431128', '25255888',
 '16529085', 'J-503609052', 'V19470697', 'J501109505', 'V279424880',
 '174442127', 'V194708471', 'J296348758', '23552352', '23553352', '24861008',
 'J502719830', 'J409541860', 'J412272241', '14322496', '14322495',
 '13283143', '17882176', '29973446', 'J306473378', 'V31113467',
 'J504538736', '24883854', 'J-50575881-7', 'V24288319', 'J310706514', '118700097',
 '295376126', 'J503190043', '16135608', '298107', '24108602', '18586373',
 '12561735', 'J591970270', 'J314800841', 'V10548737', '25625528', '28421436',
 '19958920', 'V25032693', '10164684', '27525055', 'V26847910', '30312674',
 'J501900370', '31186679', '29571518', 'V30735773', '26109665', '31164331',
 '25049589', 'J413033690', '16033678', 'J296834067', 'V12657208',
 'V16305127', '16191573', '22824035', '29501208', 'V24895374', 'V18915966',
 '14039430', '26667252', '28239063', '25004156', '15152258', 'V18963834',
 'V18670194', '27767758', 'J404276521', 'J506387344',
 'J505302450', '18907171', '23446214', 'J507534731', 'J507398382', '19275626',
 '11672209', 'V22016177', 'V28349721', '28254283', '19122268', '16959485',
 'J310425604', '28186528', '21326269', '25413986',  '20233702', 'J408328747',
 'J502614117', 'J408587289', 'J297235370', 'J307780533', '18157773',
 'V30660759', '22064633', 'J502737839', 'V30234932', 'J311328840',
 'J500838280', 'J406316385', 'J413270188', '28691639', '16028052', '26416598',
 '27604125', '25577546', 'V27460468', '20841737', 'V17223552', '27622337',
 '19096088', '17169759', '24221380', 'V11503955', 'J506640651', '11705847',
 'V21305237', '20095562', '20005993', 'V10504889',
 'V25658361', '19144846', 'V31032525', '17425808', 'V31277361', '20752393',
 '23303394', '20878740', 'V29793516', '24239785', 'V14194419', '10673519',
 '22204731', '10423613', 'V27368190', 'V20304031', '25905291', '26029592',
 'V10288459', 'J296937222', 'J504135704', '15796649', '25665719',
 '12396797',  'V30440906', '12337564', '26492614', '24103247', 'V20774509',
 '10545442', '14032980', 'V19470847', 'J409240339', 'J275038276', 'V27171011',
 'J408319454', '13931622', '15860764', 'V27879044', '24277915', 'J500368062',
 '18241713', 'V15394370', 'J501039321', 'V23899802', '25846475', 'J411681628',
 '17334680', '23677487', '14108954', 'J410348364', '24607869', '17396721',
 'V24905054', 'J298283360', '27599133', 'V14215648', '21011782', '20415057',
 'J506649683', 'J500525990', '17745038', 'J501300747', 'J502308555', 
 'J308818178', 'J507602621', 'J506018535', '19091842', 'J404604243',
 '28335238', 'V19402459', '12244577', 'V13158834', '18880857', '15632029',
 'V23917440', '31113467', '20911376', '17686872', 'V12668910', 
 '15983285', '12458173', 'V28434409', 'J302524466', '21193173',
 '398107', '7259997', '16273256', '24447187', '305131376',
 'J5009521928', '27108400', 'V22524902', '15354930',
 '30461107', '12668224', '19475294', 'V15777535', '17928463',
 '24283684', 'V25444847', 'V171647122', 'V27479614', '18067818', 
 '918363', '5890771', 'V114253584', 'V27321612', '15843354', 
 'V28278745', 'J502402691', 'J413143453', 'V10548737', 'V18726437',
 '18086110', '7019390', '22030424', '15357033', '6301130', '30563418-9',
 '14678693', 'J411229091', 'J500832362', '18162358',
 '14281580', 'J317396677', '18553393', '20114266', '11972786', '16850277',
 '27739297', '24063996', '19242969', 'J310577749', '25715229',
 'V17034460', 'J508140621', 'J-407993496', 'V250083862', 'V12065512',
 'V237299830', 'V260264237', '18728298', '5219363', '12680918',
 'V16135608', 'J508170440', 'V31227824', 'V28323746', 'V13873661',
 'J507132994', 'J507447308', '19773550', 'V30451863', '101715180',
 'J316244030', 'J315024586', 'V14508161', '24900138', 'V19035139',
 '14576081', '19815288', 'V-17572687', 'V103357639', '17442189',
 'J504614734', '15201958', '22888093', '22888083', '22888093 ',
 'V22027683', '29409555', 'V159098938', '25266856', ' 25266856',
 'V197210580','9489486','J407335189','25366768','15646585','J315814889',
 '27428929','15231656','J400559812','27150660','24932507','J505088017',
 '17851336','25679547','21459836','V18573440','J412952854','V100534343',
 'V12561735','24842664','J407936166',
 ' ', '.', '..', '...', '\\'
 )
)
-- Consulta de toda la BD de clientes con los clientes
SELECT
a.code,
a.status,
a.province,
a.country,
a.phone,
a.description,
a.address,
a.created_at,
a.created_by,
a.created_in,
a.case_client,
CASE
 WHEN n.status_client IS NULL AND a.case_client IS NULL THEN a.status
 WHEN n.status_client IS NULL AND a.case_client IS NOT NULL THEN 'ELIMINADO'
 ELSE a.status
END AS status_new
FROM cluster_almayor_clients a
LEFT JOIN no_trash_clients n
ON a.code = n.code
;
""")
chunk_size = 5000
output_file_client = r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL MAYOR\almayor_clients.parquet'
parquet_writer = None

with engine_2.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_clients, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_client, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Clientes al mayor exportados")

# %%
# Facturas al mayor
tiempo_inicio = time.time()
query_general_sales = text("""
WITH facturas AS (
SELECT
emission_date AS fecha,
register_hour AS hora,
total_net_details AS venta_neta,
client_code AS rif,
seller AS vendedor,
document_no AS factura,
correlative,
RANK() OVER(PARTITION BY client_code ORDER BY emission_date DESC, register_hour DESC) AS "ultima_factura"
-- Con éste RANK nos permite identificar el rowid = 1 como la última venta realizada del cliente
FROM public.sales_operation
WHERE 
 user_code = 'ALMAYOR'
 AND client_name <> 'ANULADO'
 AND operation_type = 'BILL'
 AND emission_date BETWEEN '2023-10-31' AND CURRENT_DATE - INTERVAL '1'
),
full_dates AS (
 SELECT generate_series('2023-10-31'::date, DATE(NOW()), '1 day'::interval)::date AS fecha
),
tax_dates AS (
SELECT
 register_date,
 register_hour,
 sales_aliquot
FROM coin_history
WHERE
 main_code = '02'
 AND register_date >= '2023-10-31'
),
full_taxes AS (
SELECT
 f.fecha AS fecha_tasa,
 t.register_date,
 t.register_hour AS hora_tasa,
 t.sales_aliquot AS tasa,
 COUNT(t.sales_aliquot) OVER (ORDER BY f.fecha, t.register_hour) AS grupo
FROM full_dates f
LEFT JOIN tax_dates t
ON f.fecha = t.register_date
),
date_coin_full AS (
SELECT
 fecha_tasa,
 hora_tasa,
 COALESCE(
  tasa,
  FIRST_VALUE(tasa) OVER (PARTITION BY grupo ORDER BY fecha_tasa, hora_tasa)
 ) AS tasa_completa
FROM full_taxes
WHERE fecha_tasa BETWEEN '2023-10-31' AND CURRENT_DATE - INTERVAL '1'
),
facturas_validadas AS (
SELECT
 f.correlative,
 f.rif,
 f.vendedor,
 f.factura,
 f.venta_neta,
 f.fecha,
 dc.fecha_tasa,
 f.hora,
 dc.hora_tasa,
 dc.tasa_completa,
 CASE
  WHEN dc.hora_tasa IS NULL THEN 0
  WHEN f.hora > dc.hora_tasa THEN 1
  ELSE 0
 END AS tasa_validada,
 CASE
  WHEN dc.hora_tasa IS NULL THEN NULL
  WHEN f.hora > dc.hora_tasa THEN tasa_completa
  ELSE NULL
 END AS tasa_corregida,
 f.ultima_factura
FROM facturas f
INNER JOIN date_coin_full dc
ON f.fecha = dc.fecha_tasa
),
facturas_secuenciadas AS (
SELECT
 correlative,
 fecha,
 hora,
 tasa_corregida,
 ROW_NUMBER() OVER (PARTITION BY correlative ORDER BY tasa_validada DESC, fecha ASC, hora ASC) AS vn,
 COUNT(tasa_corregida) OVER (ORDER BY fecha, hora) AS gp,
 rif,
 vendedor,
 factura,
 venta_neta,
 ultima_factura
FROM facturas_validadas
),
facturas_identificadas AS (
SELECT
*
FROM facturas_secuenciadas
WHERE vn = 1
)
SELECT 
fecha,
hora,
rif,
vendedor,
factura,
COALESCE(
  tasa_corregida,
  FIRST_VALUE(tasa_corregida) OVER (PARTITION BY gp ORDER BY fecha, hora),
  37.2
) AS tasa_autocompletada,
ultima_factura
FROM facturas_identificadas
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL MAYOR\almayor_general_sales_correccion.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_general_sales, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Facturas al mayor exportadas")
tiempo_final = time.time()
tiempo_ejecucion = tiempo_final - tiempo_inicio
print(f"Tiempo total de ejecución: {tiempo_ejecucion:.2f} segundos")

# %%
# Facturas detalladas por producto al mayor
tiempo_inicio = time.time()
query_detail_sales = text("""
WITH general_sales AS (
SELECT
emission_date,
register_hour,
client_code,
document_no,
correlative
FROM public.sales_operation
WHERE 
 user_code = 'ALMAYOR'
 AND client_name <> 'ANULADO'
 AND operation_type = 'BILL'
 AND emission_date BETWEEN '2023-10-31' AND CURRENT_DATE - INTERVAL '1'
),
details AS (
SELECT
emission_date AS fecha,
register_hour AS hora,
client_code AS rif,
document_no AS factura,
code_product AS producto,
amount AS cantidad,
total_net AS monto
FROM public.sales_operation_details d
INNER JOIN general_sales g
ON d.main_correlative = g.correlative
)
SELECT
factura,
producto,
SUM(cantidad) AS cantidad,
SUM(monto) AS monto
FROM details
GROUP BY factura, producto
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL MAYOR\almayor_detail_sales_correccion.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_detail_sales, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Facturas detalladas al mayor exportadas")
tiempo_final = time.time()
tiempo_ejecucion = tiempo_final - tiempo_inicio
print(f"Tiempo total de ejecución: {tiempo_ejecucion:.2f} segundos")

# %%
# Definición de clientes al detal y al mayor
tiempo_inicio = time.time()
query_total_clients = text("""
-- Este CTE es una definicion del posterior
WITH datescluster_almayor_clients AS (
SELECT
c.code,
c.status,
c.client_group,
c.province,
c.phone,
c.description,
c.address,
c.created_at,
c.created_by,
c.created_in,
ROW_NUMBER() OVER(PARTITION BY c.code ORDER BY s.emission_date ASC, s.register_hour ASC) AS "rowid",
EXTRACT(YEAR FROM emission_date) AS year_emission,
EXTRACT(MONTH FROM emission_date) AS month_emission,
EXTRACT(YEAR FROM NOW()) AS year_now,
EXTRACT(MONTH FROM NOW()) AS month_now
FROM public.clients c
INNER JOIN public.sales_operation s
ON c.code = s.client_code
WHERE
s.user_code = 'ALMAYOR'
AND s.client_name <> 'ANULADO'
AND s.operation_type = 'BILL'
),
-- CTE que define y entrega la segmentacion de los clientes entre recurrentes, nuevos del año y nuevos en los ultimos 2 meses (aprox 2.5k clientes)
cluster_almayor_clients AS (
SELECT
d.code,
d.status,
d.client_group,
d.province,
d.phone,
d.description,
d.address,
d.created_at,
d.created_by,
d.created_in,
CASE
 WHEN d.code = '00' THEN 'GENERICO'
 WHEN d.year_emission < d.year_now THEN 'RECURRENTES'
 -- "month_now-2" refleja el lapso de 2 meses atrás a la fecha actual
 WHEN d.year_emission = d.year_now AND (d.month_now-2) <= d.month_emission THEN 'NUEVOS A 2 MESES'
 ELSE 'NUEVOS AL AÑO'
END AS case_client
FROM datescluster_almayor_clients d
WHERE rowid = 1
),
-- CTE que entrega la lista de clientes al mayor no duplicados y no gestionables (aprox 1.3k clientes)
no_trash_clients AS (
SELECT
code,
CAST('Cliente no basura' AS VARCHAR(55)) AS status_client
FROM cluster_almayor_clients
WHERE code NOT IN (
 '84587877', 'E-84587877', 'V199250759', '24883911', '8819029', 'V212472618',
 'HASSAN CITY MUNDO', '12717075', '11059190', '5000036779', '13041794', '179897624',
 '17989762', '27377859', 'E461883', '27979975', '25583193', '18474495',
 '184744950', 'JOSE NAVARRETE', 'JOSE NAVAREYTE', '6948077', '26040898',
 '17243990', 'J-294107796', '14100381', '19470697', 'J504412562', '27275280',
 '17857501', '18573440', '16995746', '9494368', 'J41237909-7', '27879044', 
 '17556636', '248929384', '10379262', '14571708', '18637343', 
 '20558701', '18214910', 'J22316353-6', 'J-412747606', '26012291',
 '25317642', '12941806', '1121855004', '31344121', '23687338', '27472787',
 '27309008', 'P309898', '29583193', '15685562', '19565106', '17106204',
 '27136110', 'J413197111', 'J500837674', '0011650353', '17024553',
 '182553561', '20522218', '26838287', 'CITY CELL GSM',
 'J-309950541', 'J40974590', 'J412786059', 'J-412786059', 'J-500211228',
 'JORRGE MORA', 'JORGE MORA', 'TODOCELL', '407031228', '98012908331',
 '17757892', '429470', 'J503898119', '28708035', '19941729', '-J40703122-8',
 '27519497', 'V-14346553', '31416375-0', 'J411942596', '27941720', 'J297733337',
 '305822840', '264544444', '13496441', '21001044', '28024146', '84610888', 
 '27373717', '20753333', 'E96033008897', '448357', '12898731', '16939574', 
 'GERLINA DIGITEL', 'LUIS TUCUPITA', 'JEAN HABIBI', 'MIGUEL SOSA', 'NELTAGE',
 'GILBERTO', 'SALIM', 'WILLI ', 'JOSE METROCENTER', 'DANIEL GONZALES', 'EDIBEL',
 'ROLFER RUIZ', 'BLACK TECH', 'MIGUEL', 'LUIS FLORES', 'ISABEL', 'FIDEL GARCIA',
 'SHADY', 'KARIM ESTABA', 'ISAIAS', 'LILLIAM ', 'HECYELI', 'DANIELA  URBINA',
 'FRANCYS GOCHOS', 'FELIPE RADIO', 'MARGARITA', 'SHAFIK CHARCHAR', 'MARI CARMEN',
 'PCELL', 'JOSE MANUEL', 'MAQUINAS FISCSLEA', 'JOSE LLANERO', 'EDGAR GOMEZ',
 'DAVID ', 'DANIEL GONLAEZ', '0120', 'CARLOS SALINAS', 'SALINA', 'RAUL',
 'JULIO', 'BIT MERCADO', 'TECHNOLOGY', 'WILLY', 'VICTOR ', 'JOSE CABELLO',
 'BITMERCADO DIGITAL', 'GUSTAVO GARCIA', 'FELIPE', '1', '01', 'GILBERTO ', 
 'FELIPE HERNANDEZ', 'TALAL EL VISTAZO', 'CELUYMAS', 'ALEJANDRO',
 'DEIVYS', 'CHINO ', 'SHARIS ASAF', 'WILMER', 'SAUL MARQUEZ', 'ANAMILETH',
 'FELIX GONZALEZ', 'GOCHOS', 'MIGUEL VARGAS', 'DARY', 'LILLIAM',
 'CLIENTE BARINAS', 'ANTHONI', 'AL MAYOR', 'MARTIN LEDEZMA',
 'JOHAN ZAMBRANO', 'TYL CELULARES', 'COMPUGRAPHI', 'AMER ABDUL',
 'ISAMAR', 'SABRINA', 'ZOL', '3429', 'MARCO HAPPY PHONE', 'CARLOS PADRON',
 'REFIGERACION ', 'V19530953', 'V18834223', 'V25934937', 'V16659276', 'V20874867',
 '24302364', 'V21071357', '27068256', '31978825', 'V27858239', 'V15795106',
 'J314850520', 'J411090727', 'J404794344', 'V28331830', 'V26838287', 'V22502862',
 'J506955547', 'J506856395', 'J504227463', 'V12044804', '21207852', 'J200001178',
 'V30964722', 'V25740802', 'J298990023', 'J502771077', 'J317523849', 'V31024020',
 'V12607697', 'V30806369', 'V18827324', 'V26128170', 'V28595519', 'V27239854',
 '14393669', '24656062', 'J310141432', 'V16354731', 'V10040207', '20786813',
 'V16054354', 'V29875806', 'V32777701', 'V17075167', 'V26888750', 'V28231382',
 'V26717255', 'J410002875', 'V26700028', 'J411078050', 'J299339652', 'J506513595',
 '27975952', '19625820', 'V26529754', '18616761', 'V23691821', 
 'V23607704', 'V15648751', ' 25566789', '26369997', 'J400869501', 'V080665853',
 'E473634', '13385046', 'R005259', 'L934926', 'V79491744', 'P564520', 'E85000632',
 '26919619', 'V8747970', '27406100', 'V30810086', '19008932', 'V138047993',
 '19088843', 'V176172777', 'V201234898', 'V175003335', 'P839031', 'V135872942',
 'V178585866', 'R485271', 'V171613015', 'V26012291', 'V27693035', 'V296795891',
 '17268497', 'L369198', 'J505293591', 'V15587538', '28518643', '19505967',
 '29925089-9', '223163536', 'V27529171', '21505974', '17907504', 'P01269530',
 'J090270000', '504160695', 'J408984865', '133636720', '17371845', 'J412793330',
 'A00774858', 'J503501928', '18639188', '178315648', 'J411697826', '413220660',
 '19958427', '502140069', '0J504758817', 'V191914615', 'J40401568980', '17691521-4',
 'J003258458', '1252488', '27460468', '25846833', 'V17303797', '27363491',
 '17073309', '84569847', '18204489', '20096422', '25367246', '20717124',
 'V24905920', '27107853', '28164818', '30188122', '24459089', 'V24459089',
 'V17840043', '30300266', 'V30815339', 'J406977349', 'V4835504', '27789444',
 'V27646342', 'J-400340756', 'J504926124', '11681227', 'V20616127', '31101811',
 '19228275', '19360291', '254545569', '26482246', '501356408', 'J-29459455-7',
 'J-304820038', 'J-307980486', 'J-30798048-6', 'J-313678295', 'J31546666-0',
 'J-315814889', 'J40034075-6', 'J40473769', 'J-410560037', 'J-50064113-3',
 'J-501356408', 'J50150936-0', 'J-502651411', '27000289', '18745139',
 '29615892', '27819019', '27268275', 'M571832', '29948893', 'V28554461', '28465092',
 'M152704', '19527235', 'M263615', 'V267494416', '473634', '25656247', '27309394',
 '29665857', '19740591', 'L544025', '043266299', '34174054', '22279438', '25286352',
 '23916461', '8468666', '19087122', '19729842', 'J41285716', '14166186',
 '18255356', '12160525', '19607353', '31960824', '32067021', 'V242068110', 
 '21057142','199161130', '19916130', 'V239871778', '29702183', '25130703',
 '24705985', '24931613', '28745306', '22283370', '18328622', '13111439', 'M705774',
 '26741745', 'V214140256', '30157871', '8509642', '18167399', '19759755', '30471395',
 'V14679172', '505216570', '6366732', '16701176', '19829628', 'L926934', '27561806',
 '25260788', '10281031', '26738426', '28058541', '473389', '6929178', '13308277',
 '18474950', '30510817', 'E473389', '18912651', 'J412874080', '18924508', '24501294',
 '14183735', 'L318357', 'J502431462', 'J408478277', 'J296802394', '17871674', 
 'M311026', '27309325', '12607697', '88032529484', '14746742', '20531884', '26440486',
 '20799580', '24073867', '20615445', '17609616', '17108050', 'E445356', '26620255',
 '29948014', '30155867', '20330769', '17504457', 'V076203483', '16012110', 'P407242',
 '18756137', '25696753', '14552036', '25658361', 'V26444516', 'V25813800', 
 '27297101', 'V208042803', '25504442', 'V26942692', '17106606', '30063446', 
 'J506111616', '14872037', '16095518', 'E446025', '17078676', 'E 397533', '31998095',
 '18018072', '17587128', '18959761', '20866516', '20886516', '25223481', '13986555',
 '19361240', '22888629', '18394206', '24900643', '10039354', 'V280632771',
 '18326715', '184171803', '14949587', '17622875', '450948', '20781751', '84404875',
 '26176087', '313095680', '16531316', '29893428', 'R040230', 'E411399', '13114595',
 '6448327', 'K4090007', '18586347', '28423033', 'J002453281', 'J500381980',
 'E428469', '12563438', '31506840', '15757938', '19455257', 'L235164', '22909137',
 '14194731', '20362894', '26061872', '15023744', '25417213', '19954425', '10237554',
 '29960417', '84558211','MUNDO MOVIL', '502617256', '25524432',
 'V18978038', 'V27918677', '15962833', '24806372', '84498242', 'E84498242',
 'J303077978', '26818426', '401838090', 'J40948768', 'J50064113-3', 'J500636750',
 '26161979', 'V31960824', 'V17045690', '17211114', '22778495',
 'J504395544', 'J306842675', '26454444', '22561766', '25454569', '26482946',
 '30111566', '17584476', '11166808', 'J501852596', 'J403074461', '25839812',
 '17105917', 'J504615510', '26397667', '13376244', '19223101',
 'J505662392', 'J505645730', '19818450', '19152114', '16682084', '106972105',
 '23616721', '30563418', '29533543', 'J402648960', '19228277', '17599812',
 '24795636', '27051927', 'J500445989', '20789378', 'J505434993',
 'J404204300', 'J506312107', '31263062', '20365422', '21251630',
 '15269332', '24435639', 'V22398928', '10539192', 'V25646118', '17605414',
 '19899789', '19740731', '23607176', '13326021', 'V23749010', '29549150',
 '12790006', '25252035', '18018073', '15152662', 'V030786234',
 '18236975', '32296618', '18586437', '27243396', 'J411536393', '16531317',
 '21011773', '19865354', '24578026', '20716136', '10036573', '20430101',
 '23951260', '16450184', 'V14566916', 'V27558741', 'J410110340', 'J30381261-9',
 '25361162', '19163156', '19500873', '22316353', '37023541', '23729983',
 '26430769', '0025350604', '158520441', '184661585',
 '20233708', '26497362', '29288320', '25566789', '309950541', '297235450',
 '31360909', '400648505', '401568990', '404204300', '412501550', '412786059',
 '500132905', '502466452', '502552880', '503565063', 'J-294298834',
 'J2958663458', 'J313203203092', 'J31572738-2', 'J-400729734', 'J41276970',
 'J40699595-6', 'J-412874080', 'J503655063', 'J-50412585-7', 'P:1031798',
 'V17935226', '012065512', '10381743',
 '10500573', '11161842', '11407130', '11817065', '12163578', '12187555', '12721229',
 '12776236', '13109063', '13125211', '13155232', '13319386', '13533020', '13620856',
 '13871231', '14057406', '14552038', '14838248', '14897735', '15338067', '15342343',
 '15443490', '15664502', '15832230', '16131738', '16134034', '16224714',
 '16225862', '16343224', '16392279', '16555714', '16704494', '16813517', '16944316',
 '17139996', '17255969', '17393765', '17476309', '17519216', '17622359',
 '17692418', '17721225', '17822117', '17823166', '18050629', '18333169', '18350699',
 '18741895', '18786667', '19243203', '19565663', '19738226', '19805529', '19887122',
 '20032903', '20032938', '20080166', '20087901', '20117786', '20269132', '20362844',
 '20636344', '21018334', '21125730', '21194538', '21263001', '21353996', '21375626',
 '21615027', '22036707', '22041680', '22215460', '23626357', '24216013', '24218569',
 '24348884', '24753633', '24788074', '24841807', '25213645', '25225147', '25350604',
 '25615952', '25926281', '2598570', '26217680', '26296544', '26351762', '26454137',
 '26480881', '27027845', '27028475', '27223673', '27276234', '27344456', '27472768',
 '27680628', '27827275', '27908160', '28421185', '28482505', '28672113', '29776987',
 '29798985', '29828336', '30031036', '30199611', '30291660', '30335833', '30553858',
 '30558702', '30579881', '30683728', '30777562', '307838140', '31194976', '31368936',
 '31401282', '31852048', '33913128', '9412975', '9494361', '9966927', 'J176915214',
 'J293939240', 'J294095550', 'J-294594557', 'J298203360', 'J299615200',
 'J304611078', 'J305232806', 'J307034238', 'J308610089', 'J310445397',
 'J315789140', 'J315943867', 'J317307615', 'J400223685', 'J400319285',
 'J401244190', 'J401815685', 'J403261504', 'J403716064', 'J403831203', 'J404711724',
 'J405069651', 'J405204222', 'J405310030', 'J405860740', 'J406006343', 'J406330540',
 'J406399116', 'J407277898', 'J408374455', 'J408527120', 'J409829456', 'J410528079',
 'J412012738', 'J412402668', 'J412839969', 'J500249144', 'J500489307', 'J500543921',
 'J501075883', 'J501254834', 'J501381836', 'J-50140771-1', 'J501889368', 'J502389695',
 'J502552880', 'J502614630', 'J502991875', 'J503608331', 'J50415075-4', 'J504313343',
 'J504395650', 'J504764744', 'J504904791', 'J505140850', 'J-50546790-5', 'J505772821',
 'J506335735', 'J507228924', 'J840129004', 'V14673104', 'V20105949', 'V26358451',
 'V26683938', 'V27427963', 'V27513925', 'J500441700', '148215232',
 'E402104', 'E80397597', 'L345553', 'E277988152', 'K237544', 'L554025',
 'ANTONI ', 'L890261', 'BETZALI ', 'P278182', 'DAILUZ ', 'DARY ', 'E398107',
 'M518545', 'PK716825', 'L011243', 'I448357', 'E029602708',
 'L621271', 'M175587', 'JUAN CARLOS ', 'E82062526', 'E396604', 'E397533',
 'L627477', 'E81084272', 'P109468', 'N256287', 'P839041', 'L211048', 'L855766',
 'L454003', 'E449477', '21|615027', ' L235164', 'L650670',
 'E82359053', 'E516905', 'E419356', 'P178371', '306967532', '83434008',
 'J5022912029', 'J503655053', '25418268', 'J-50124374-3', '518545', '501581',
 '19569872', 'J406316386', '277298851', '297298851', 'J-502431128', '25255888',
 '16529085', 'J-503609052', 'V19470697', 'J501109505', 'V279424880',
 '174442127', 'V194708471', 'J296348758', '23552352', '23553352', '24861008',
 'J502719830', 'J409541860', 'J412272241', '14322496', '14322495',
 '13283143', '17882176', '29973446', 'J306473378', 'V31113467',
 'J504538736', '24883854', 'J-50575881-7', 'V24288319', 'J310706514', '118700097',
 '295376126', 'J503190043', '16135608', '298107', '24108602', '18586373',
 '12561735', 'J591970270', 'J314800841', 'V10548737', '25625528', '28421436',
 '19958920', 'V25032693', '10164684', '27525055', 'V26847910', '30312674',
 'J501900370', '31186679', '29571518', 'V30735773', '26109665', '31164331',
 '25049589', 'J413033690', '16033678', 'J296834067', 'V12657208',
 'V16305127', '16191573', '22824035', '29501208', 'V24895374', 'V18915966',
 '14039430', '26667252', '28239063', '25004156', '15152258', 'V18963834',
 'V18670194', '27767758', 'J404276521', 'J506387344',
 'J505302450', '18907171', '23446214', 'J507534731', 'J507398382', '19275626',
 '11672209', 'V22016177', 'V28349721', '28254283', '19122268', '16959485',
 'J310425604', '28186528', '21326269', '25413986',  '20233702', 'J408328747',
 'J502614117', 'J408587289', 'J297235370', 'J307780533', '18157773',
 'V30660759', '22064633', 'J502737839', 'V30234932', 'J311328840',
 'J500838280', 'J406316385', 'J413270188', '28691639', '16028052', '26416598',
 '27604125', '25577546', 'V27460468', '20841737', 'V17223552', '27622337',
 '19096088', '17169759', '24221380', 'V11503955', 'J506640651', '11705847',
 'V21305237', '20095562', '20005993', 'V10504889',
 'V25658361', '19144846', 'V31032525', '17425808', 'V31277361', '20752393',
 '23303394', '20878740', 'V29793516', '24239785', 'V14194419', '10673519',
 '22204731', '10423613', 'V27368190', 'V20304031', '25905291', '26029592',
 'V10288459', 'J296937222', 'J504135704', '15796649', '25665719',
 '12396797',  'V30440906', '12337564', '26492614', '24103247', 'V20774509',
 '10545442', '14032980', 'V19470847', 'J409240339', 'J275038276', 'V27171011',
 'J408319454', '13931622', '15860764', 'V27879044', '24277915', 'J500368062',
 '18241713', 'V15394370', 'J501039321', 'V23899802', '25846475', 'J411681628',
 '17334680', '23677487', '14108954', 'J410348364', '24607869', '17396721',
 'V24905054', 'J298283360', '27599133', 'V14215648', '21011782', '20415057',
 'J506649683', 'J500525990', '17745038', 'J501300747', 'J502308555', 
 'J308818178', 'J507602621', 'J506018535', '19091842', 'J404604243',
 '28335238', 'V19402459', '12244577', 'V13158834', '18880857', '15632029',
 'V23917440', '31113467', '20911376', '17686872', 'V12668910', 
 '15983285', '12458173', 'V28434409', 'J302524466', '21193173',
 '398107', '7259997', '16273256', '24447187', '305131376',
 'J5009521928', '27108400', 'V22524902', '15354930',
 '30461107', '12668224', '19475294', 'V15777535', '17928463',
 '24283684', 'V25444847', 'V171647122', 'V27479614', '18067818', 
 '918363', '5890771', 'V114253584', 'V27321612', '15843354', 
 'V28278745', 'J502402691', 'J413143453', 'V10548737', 'V18726437',
 '18086110', '7019390', '22030424', '15357033', '6301130', '30563418-9',
 '14678693', 'J411229091', 'J500832362', '18162358',
 '14281580', 'J317396677', '18553393', '20114266', '11972786', '16850277',
 '27739297', '24063996', '19242969', 'J310577749', '25715229',
 'V17034460', 'J508140621', 'J-407993496', 'V250083862', 'V12065512',
 'V237299830', 'V260264237', '18728298', '5219363', '12680918',
 'V16135608', 'J508170440', 'V31227824', 'V28323746', 'V13873661',
 'J507132994', 'J507447308', '19773550', 'V30451863', '101715180',
 'J316244030', 'J315024586', 'V14508161', '24900138', 'V19035139',
 '14576081', '19815288', 'V-17572687', 'V103357639', '17442189',
 'J504614734', '15201958', '22888093', '22888083', '22888093 ',
 'V22027683', '29409555', 'V159098938', '25266856', ' 25266856',
 'V197210580','9489486','J407335189','25366768','15646585','J315814889',
 '27428929','15231656','J400559812','27150660','24932507','J505088017',
 '17851336','25679547','21459836','V18573440','J412952854','V100534343',
 'V12561735','24842664','J407936166',
 ' ', '.', '..', '...', '\\'
 )
),
total_clients AS (
SELECT
c1.code,
c1.status,
c1.client_group,
c1.province,
c1.country,
c1.phone,
c1.description,
c1.address,
c1.created_at,
c1.created_by,
c1.created_in
FROM public.clients c1
)
-- Consulta de toda la BD de clientes con los clientes
SELECT
t.code,
t.status,
t.province,
t.country,
t.phone,
t.description,
t.address,
t.created_at,
t.created_by,
t.created_in,
a.case_client,
n.status_client,
CASE
 WHEN n.status_client IS NULL AND a.case_client IS NULL THEN 'AL DETAL'
 ELSE 'AL MAYOR'
END AS group_sale,
CASE
 WHEN n.status_client IS NULL AND a.case_client IS NULL THEN t.status
 WHEN n.status_client IS NULL AND a.case_client IS NOT NULL THEN 'ELIMINADO'
 ELSE t.status
END AS status_new,
t.client_group
FROM total_clients t
LEFT JOIN cluster_almayor_clients a
ON t.code = a.code
LEFT JOIN no_trash_clients n
ON t.code = n.code
;
""")
chunk_size = 5000
output_file_client = r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL DETAL y AL MAYOR\all_clients.parquet'
parquet_writer = None

with engine_2.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_total_clients, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        chunk['status_client'] = chunk['status_client'].astype(str)
        chunk['case_client'] = chunk['case_client'].astype(str)
        chunk['created_at'] = pd.to_datetime(chunk['created_at'], unit='s').astype('datetime64[us]')
        chunk['created_by'] = chunk['created_by'].astype(str)
        chunk['created_in'] = chunk['created_in'].astype(str)
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_client, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Clientes al detal y al mayor exportados")
tiempo_final = time.time()
tiempo_ejecucion = tiempo_final - tiempo_inicio
print(f"Tiempo total de ejecución: {tiempo_ejecucion:.2f} segundos")

# %%
# Facturas al detal y al mayor
tiempo_inicio = time.time()
query_general_sales = text("""
WITH facturas AS (
SELECT
emission_date AS fecha,
register_hour AS hora,
total_net_details AS venta_neta,
client_code AS rif,
seller AS vendedor,
user_code AS usuario,
document_no AS factura,
store AS tienda,
correlative,
RANK() OVER(PARTITION BY client_code ORDER BY emission_date DESC, register_hour DESC) AS "ultima_factura"
-- Con éste RANK nos permite identificar el rowid = 1 como la última venta realizada del cliente
FROM public.sales_operation
WHERE 
 user_code IN (
  'AB06', 'AB71', 'AB77', 'AB77AC', 'B214', 'B407', 'L111', 'L160', 'L160AA', 'L210L', 'L210M',
  'L210Y', 'L227N', 'L227O', 'L229', 'L230', 'L231', 'L246', 'L250', 'L251', 'L337Q', 'L337R',
  'L337Z', 'L249', 'DELIVERY', 'ALMAYOR'
  )
 AND client_name <> 'ANULADO'
 AND operation_type = 'BILL'
 AND emission_date BETWEEN '2024-01-01' AND CURRENT_DATE - INTERVAL '1 day'
),
full_dates AS (
 SELECT generate_series('2024-01-01'::date, DATE(NOW()), '1 day'::interval)::date AS fecha
),
tax_dates AS (
SELECT
 register_date,
 register_hour,
 sales_aliquot
FROM coin_history
WHERE
 main_code = '02'
 AND register_date >= '2024-01-01'
),
full_taxes AS (
SELECT
 f.fecha AS fecha_tasa,
 t.register_date,
 t.register_hour AS hora_tasa,
 t.sales_aliquot AS tasa,
 COUNT(t.sales_aliquot) OVER (ORDER BY f.fecha, t.register_hour) AS grupo
FROM full_dates f
LEFT JOIN tax_dates t
ON f.fecha = t.register_date
),
date_coin_full AS (
SELECT
 fecha_tasa,
 hora_tasa,
 COALESCE(
  tasa,
  FIRST_VALUE(tasa) OVER (PARTITION BY grupo ORDER BY fecha_tasa, hora_tasa)
 ) AS tasa_completa
FROM full_taxes
WHERE fecha_tasa BETWEEN '2024-01-01' AND CURRENT_DATE - INTERVAL '1 day'
),
facturas_validadas AS (
SELECT
 f.correlative,
 f.rif,
 f.vendedor,
 f.usuario,
 f.factura,
 f.venta_neta,
 f.tienda,
 f.fecha,
 dc.fecha_tasa,
 f.hora,
 dc.hora_tasa,
 dc.tasa_completa,
 CASE
  WHEN dc.hora_tasa IS NULL THEN 0
  WHEN f.hora > dc.hora_tasa THEN 1
  ELSE 0
 END AS tasa_validada,
 CASE
  WHEN dc.hora_tasa IS NULL THEN NULL
  WHEN f.hora > dc.hora_tasa THEN tasa_completa
  ELSE NULL
 END AS tasa_corregida,
 f.ultima_factura
FROM facturas f
INNER JOIN date_coin_full dc
ON f.fecha = dc.fecha_tasa
),
facturas_secuenciadas AS (
SELECT
 correlative,
 fecha,
 hora,
 tasa_corregida,
 ROW_NUMBER() OVER (PARTITION BY correlative ORDER BY tasa_validada DESC, fecha ASC, hora ASC) AS vn,
 COUNT(tasa_corregida) OVER (ORDER BY fecha, hora) AS gp,
 rif,
 vendedor,
 usuario,
 factura,
 venta_neta,
 tienda,
 ultima_factura
FROM facturas_validadas
),
facturas_identificadas AS (
SELECT
*
FROM facturas_secuenciadas
WHERE vn = 1
)
SELECT 
fecha,
hora,
rif,
vendedor,
usuario,
factura,
tienda,
COALESCE(
  tasa_corregida,
  FIRST_VALUE(tasa_corregida) OVER (PARTITION BY gp ORDER BY fecha, hora),
  39.2
) AS tasa_autocompletada
FROM facturas_identificadas
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL DETAL y AL MAYOR\general_sales_correccion.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_general_sales, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Facturas al detal y al mayor exportadas")
tiempo_final = time.time()
tiempo_ejecucion = tiempo_final - tiempo_inicio
print(f"Tiempo total de ejecución: {tiempo_ejecucion:.2f} segundos")

# %%
# Facturas detalladas por producto al detal y al mayor
tiempo_inicio = time.time()
query_detail_sales_both = text("""
WITH general_sales AS (
SELECT
emission_date,
register_hour,
user_code,
client_code,
document_no,
correlative
FROM public.sales_operation
WHERE 
 user_code IN (
   'AB06', 'AB71', 'AB77', 'AB77AC', 'B214', 'B407', 'L111', 'L160', 'L160AA', 'L210L', 'L210M',
   'L210Y', 'L227N', 'L227O', 'L229', 'L230', 'L231', 'L246', 'L250', 'L251', 'L337Q', 'L337R',
   'L337Z', 'L249', 'DELIVERY', 'ALMAYOR'
   )
 AND client_name <> 'ANULADO'
 AND operation_type = 'BILL'
 AND emission_date BETWEEN '2024-01-01' AND CURRENT_DATE - INTERVAL '1 day'
),
details AS (
SELECT
emission_date AS fecha,
register_hour AS hora,
user_code AS usuario,
client_code AS rif,
document_no AS factura,
code_product AS producto,
amount AS cantidad,
total_net AS monto
FROM public.sales_operation_details d
INNER JOIN general_sales g
ON d.main_correlative = g.correlative
)
SELECT
usuario,
factura,
producto,
SUM(cantidad) AS cantidad,
SUM(monto) AS monto
FROM details
GROUP BY usuario, factura, producto
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL DETAL y AL MAYOR\details_sales_correccion.parquet'
parquet_writer = None

with engine_2.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_detail_sales_both, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        #print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Facturas detalladas al detal y al mayor exportadas")
tiempo_final = time.time()
tiempo_ejecucion = tiempo_final - tiempo_inicio
print(f"Tiempo total de ejecución: {tiempo_ejecucion:.2f} segundos")

# %%
# ETL Culminado
print('Procesamiento terminado')


