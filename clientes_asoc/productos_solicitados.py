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
# Productos solicitados
query_jsalazar = text("""
WITH productos AS (
SELECT
code AS codigo_producto,
description AS producto,
mark AS marca,
UPPER(LEFT(description,8)) AS inicial
FROM products
WHERE
mark IN ('SAMSUNG', 'TECNO', 'BLU', 'MOTOROLA')
AND UPPER(LEFT(description,8)) = 'TELEFONO'
),
depositos AS (
SELECT
product_code AS codigo_producto,
store AS codigo_deposito,
stock AS stock_actual
FROM products_stock
),
tiendas AS (
SELECT
code AS codigo_deposito,
description AS tienda,
CASE
 WHEN UPPER(LEFT(description,3)) = 'DEP' THEN 'DEPOSITO'
 ELSE UPPER(description)
END AS resumen_tienda
FROM store
),
ventas AS (
SELECT
sd.code_product AS codigo_producto,
sd.store AS codigo_deposito,
sd.amount AS cantidad
FROM sales_operation_details sd
INNER JOIN sales_operation so
ON sd.main_correlative = so.correlative
WHERE
so.client_name <> 'ANULADO'
AND so.operation_type = 'BILL'
AND so.emission_date BETWEEN CURRENT_DATE - INTERVAL '7 day' AND CURRENT_DATE - INTERVAL '1 day'
)
SELECT
p.producto,
p.marca,
t.resumen_tienda AS tienda,
d.stock_actual,
SUM(v.cantidad) AS cantidad
FROM ventas v
INNER JOIN productos p
ON v.codigo_producto = p.codigo_producto
INNER JOIN tiendas t
ON t.codigo_deposito = v.codigo_deposito
LEFT JOIN depositos d
ON d.codigo_producto = v.codigo_producto
AND d.codigo_deposito = v.codigo_deposito
GROUP BY
p.producto,
p.marca,
t.resumen_tienda,
d.stock_actual
;
""")
output_file_seller = r'C:\Users\POWERBI\Desktop\Entornos\clientes_asoc\jsalazar\productos solicitados.csv'
with engine.connect() as conn:
    conn = conn.execution_options(
        postgresql_readonly=True
    )
    df = pd.read_sql_query(query_jsalazar, con=conn)
    df.to_csv(
        output_file_seller,
        index=False,
        encoding='utf-8'
    )
print("Productos solicitados por Jorge Salazar")

# %%
# Productos solicitados
query_haular = text("""
WITH categorias AS (
SELECT
code AS codigo_categoria,
description AS categoria
FROM department
WHERE
code = '01'
),
productos AS (
SELECT
p.code AS codigo_producto,
p.description AS producto
FROM products p
INNER JOIN categorias c
ON p.department = c.codigo_categoria
WHERE
p.mark IN ('TECNO')
),
depositos AS (
SELECT
product_code AS codigo_producto,
SUM(stock) AS stock_actual
FROM products_stock
GROUP BY
product_code
),
ventas AS (
SELECT
p.producto,
p.codigo_producto,
SUM(sd.amount) AS cantidad_vendida
FROM sales_operation_details sd
INNER JOIN sales_operation so
ON sd.main_correlative = so.correlative
INNER JOIN productos p
ON p.codigo_producto = sd.code_product
WHERE
so.client_name <> 'ANULADO'
AND so.operation_type = 'BILL'
AND so.emission_date BETWEEN '2026-09-14' AND '2026-09-27'
GROUP BY
p.codigo_producto,
p.producto
)
SELECT
v.producto,
d.stock_actual,
v.cantidad_vendida
FROM ventas v
INNER JOIN depositos d
ON v.codigo_producto = d.codigo_producto
;
""")
output_file_seller = r'C:\Users\POWERBI\Desktop\Entornos\clientes_asoc\haular\productos solicitados.csv'
with engine.connect() as conn:
    conn = conn.execution_options(
        postgresql_readonly=True
    )
    df = pd.read_sql_query(query_haular, con=conn)
    df.to_csv(
        output_file_seller,
        index=False,
        encoding='utf-8'
    )
print("Productos solicitados por Hector Aular")


