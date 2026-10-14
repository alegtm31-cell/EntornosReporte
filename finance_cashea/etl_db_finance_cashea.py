# %%
# Importar librerias
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
# Query para los financiamientos de cashea
query_finance_cashea = text("""
WITH pay_cashea AS (
SELECT
 w.main_correlative,
 s.document_no,
 w.amount,
 w.amount_local,
 w.emission_date
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
)
SELECT
 *
FROM pay_cashea
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Desktop\Entornos\finance_cashea\data\financiamientos.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_finance_cashea, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Financiamientos exportados")

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
 w.amount_local
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
)
SELECT
*
FROM pay_customer
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Desktop\Entornos\finance_cashea\data\pays_cashea.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_pays, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Pagos por cashea exportados")

# %%
# Calendario
query_calendar = text("""
SELECT
DISTINCT(emission_date)
FROM sales_operation
WHERE emission_date BETWEEN '2026-04-01' AND (CURRENT_DATE - INTERVAL '1 day')
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Desktop\Entornos\finance_cashea\data\calendario.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_calendar, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Calendario exportado")

# %%
# Facturas de cashea asociadas a tiendas
query_stores_cashea = text("""
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
stores_cashea AS (
SELECT 
 s.document_no,
 u.description
FROM users u
INNER JOIN sales_operation s
ON u.code = s.user_code
INNER JOIN way_to_pay w
ON s.correlative = w.correlative_related
INNER JOIN way_to_pay_details wd
ON w.correlative = wd.main_correlative
),
selected_stores AS (
SELECT
 p.document_no,
 s.description,
 ROW_NUMBER() OVER(PARTITION BY p.document_no) AS rowid
FROM pay_cashea p
INNER JOIN stores_cashea s
ON p.document_no = s.document_no
)
SELECT
 document_no,
 description
FROM selected_stores
WHERE
 rowid = 1
;                    
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Desktop\Entornos\finance_cashea\data\stores.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_stores_cashea, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Tiendas y facturas exportados")

# %%
# Ventas asociadas a cashea
query_sales = text("""
WITH first_stage AS (
SELECT
 sd.line,
 s.document_no,
 s.emission_date,
 s.register_hour,
 sd.description_product,
 sd.mark,
 sd.total_net,
 CASE
  WHEN LEFT(UPPER(sd.description_product), 8) = 'TELEFONO' THEN 'TELEFONOS'
  WHEN d.father_department = '12' THEN 'ACCESORIOS'
  ELSE 'OTROS'
 END AS case_products
FROM sales_operation_details sd
INNER JOIN sales_operation s
ON sd.main_correlative = s.correlative
INNER JOIN way_to_pay w
ON s.correlative = correlative_related
INNER JOIN way_to_pay_details wd
ON w.correlative = wd.main_correlative
INNER JOIN products p
ON sd.code_product = p.code
INNER JOIN department d
ON p.department = d.code
WHERE
 wd.type_operation = 'TRANSFER'
 AND wd.coin_code = '06'
 AND wd.emission_date BETWEEN '2026-04-01' AND (CURRENT_DATE - INTERVAL '1 day')
 AND sd.total_net > 0
)
SELECT *
FROM first_stage
;                    
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Desktop\Entornos\finance_cashea\data\sales.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_sales, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Ventas exportadas")


# %%
# Ventas asociadas a los telefonos por cashea
query_phones_cashea = text("""
WITH cashea_phones AS (
SELECT
 so.document_no,
 so.emission_date,
 sd.code_product,
 sd.amount
FROM sales_operation so
INNER JOIN sales_operation_details sd
ON so.correlative = sd.main_correlative
WHERE
 so.emission_date BETWEEN '2026-04-01' AND (CURRENT_DATE - INTERVAL '1 day')
)
SELECT
 *
FROM cashea_phones
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Desktop\Entornos\finance_cashea\data\phones_cashea.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_phones_cashea, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Telefonos vendidos exportados")


# %%
# Ventas asociadas a los telefonos por cashea
query_productos_cashea = text("""
SELECT
code,
description,
mark
FROM products
;
""")
chunk_size = 5000
output_file_seller = r'C:\Users\POWERBI\Desktop\Entornos\finance_cashea\data\productos_cashea.parquet'
parquet_writer = None

with engine.connect() as conn:
    conn = conn.execution_options(
        isolation_level="AUTOCOMMIT",
        postgresql_readonly=True
    )
    chunks = pd.read_sql_query(query_productos_cashea, con=conn, chunksize=chunk_size)
    for i, chunk in enumerate(chunks):
        print(f"Procesando bloque {i + 1}...")
        table = pa.Table.from_pandas(chunk)
        if parquet_writer is None:
            parquet_writer = pq.ParquetWriter(output_file_seller, table.schema, compression='snappy')
        parquet_writer.write_table(table)
if parquet_writer:
    parquet_writer.close()
print("Detalles de telefonos exportados")


# %%
# ETL Culminado
print('Procesamiento terminado')
