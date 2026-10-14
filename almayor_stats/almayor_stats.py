# %%
# Librerias
print('Leyendo librerias')
import pandas as pd
import numpy as np
import polars as pl
import fastparquet as fp
import duckdb
import pyarrow as pa
import xlsxwriter
print('Librerias leidas')

# %%
# Tablas 
print('Leyendo tablas')
paises = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\countries.parquet')
estados = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\provinces.parquet')
productos = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\products.parquet')
categorias = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\department.parquet')
categorias_padre = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\father_department.parquet')
clientes = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL MAYOR\almayor_clients.parquet')
vendedores = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL MAYOR\almayor_sellers.parquet')
ventas = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL MAYOR\almayor_detail_sales_correccion.parquet')
facturas = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL MAYOR\almayor_general_sales_correccion.parquet')
print('Tablas leidas correctamente')

# %%
# Verificaciones
duckdb.sql(
"""
SELECT
*
FROM categorias
LIMIT 3
;
"""
).pl()

# %%
# Transformaciones ################## BD Clientes
print('Transformando la BD de clientes al mayor')
bd_clientes = duckdb.sql(
"""
WITH limpiando_clientes AS (
SELECT
f.rif,
c.description AS cliente,
c.phone AS telefono,
v.description AS vendedor,
c.address AS direccion,
e.description AS estado,
CASE
 WHEN p.description = 'LOCAL' THEN 'VENEZUELA'
 ELSE p.description
END AS pais,
c.case_client AS tipo,
CASE
 WHEN c.status_new = '01' THEN 'ACTIVO'
 WHEN c.status_new = '02' THEN 'INACTIVO'
 ELSE 'ELIMINADO'
END estatus,
f.factura,
ROW_NUMBER() OVER(PARTITION BY rif) AS unicidad
FROM facturas f
INNER JOIN clientes c
ON f.rif = c.code
INNER JOIN vendedores v
ON f.vendedor = v.code
INNER JOIN estados e
ON c.province = e.code
INNER JOIN paises p
ON c.country = p.code
),
primeras_operaciones AS (
SELECT
f.rif,
v.description AS vendedor,
f.fecha,
f.hora,
ROW_NUMBER() OVER(PARTITION BY f.rif ORDER BY f.fecha, f.hora) AS primera_operacion
FROM facturas f
INNER JOIN vendedores v
ON f.vendedor = v.code
),
fifo_selected AS(
SELECT
rif,
vendedor,
fecha
FROM primeras_operaciones
WHERE
primera_operacion = 1
),
lilo_selected AS (
SELECT
f.rif,
v.description AS vendedor,
f.fecha
FROM facturas f
INNER JOIN vendedores v
ON f.vendedor = v.code
WHERE
f.ultima_factura = 1
),
compras AS (
SELECT
fa.rif,
COUNT(DISTINCT(fa.factura)) AS facturas,
SUM(TRUNC((ve.monto / fa.tasa_autocompletada)::NUMERIC,2)) AS ingresos
FROM facturas fa
INNER JOIN ventas ve
ON fa.factura = ve.factura
GROUP BY rif
)
SELECT
lc.rif,
lc.cliente,
lc.telefono,
lc.direccion,
lc.estado,
lc.pais,
lc.tipo,
lc.estatus,
fs.vendedor AS primer_vendedor,
fs.fecha AS primera_factura,
ls.vendedor AS ultimo_vendedor,
ls.fecha AS ultima_factura,
cp.facturas,
cp.ingresos
FROM limpiando_clientes lc
INNER JOIN fifo_selected fs
ON lc.rif = fs.rif
INNER JOIN lilo_selected ls
ON lc.rif = ls.rif
INNER JOIN compras cp
ON lc.rif = cp.rif
WHERE
lc.unicidad = 1
;
"""
).pl()
print('Transformacion de la BD de clientes al mayor culminada')

# %%
################## Historico de facturaciones
print('Transformando las facturaciones al mayor')
facturaciones = duckdb.sql(
"""
WITH facturaciones_tasadas AS (
SELECT
f.fecha,
f.factura,
v.cantidad,
TRUNC((v.monto / f.tasa_autocompletada)::NUMERIC,2) AS monto_dolar
FROM facturas f
INNER JOIN ventas v
ON f.factura = v.factura
)
SELECT
fecha,
COUNT(DISTINCT(factura)) AS facturaciones,
SUM(cantidad) AS unidades_vendidas,
SUM(monto_dolar) AS monto_dolar
FROM facturaciones_tasadas
GROUP BY
fecha
"""
).pl()
print('Transformacion de las facturaciones al mayor culminada')

# %%
################## Facturaciones por marcas
print('Transformando las facturaciones al mayor por marcas')
marcas = duckdb.sql(
"""
WITH facturaciones_marcas AS (
SELECT
f.fecha,
f.factura,
EXTRACT(YEAR FROM f.fecha) AS año,
EXTRACT(MONTH FROM f.fecha) AS mes,
CASE
 WHEN p.mark = '1-HORA' THEN '1 HORA'
 WHEN p.mark = 'X-BYTE' THEN 'X BYTE'
 ELSE p.mark
END AS marca,
CASE
 WHEN p.department IN ('02', '03', '031', '05', '050', '06', '08', '09', '10', '11', '12') THEN 'ACCESORIOS'
 WHEN UPPER(LEFT(p.description,8)) = 'TELEFONO' THEN 'TELEFONOS'
 ELSE 'OTROS'
END AS tipo_producto,
v.cantidad,
v.monto,
f.tasa_autocompletada,
TRUNC((v.monto / f.tasa_autocompletada)::NUMERIC,2) AS monto_dolar,
p.code AS producto,
p.department AS categoria
FROM ventas v
INNER JOIN facturas f
ON v.factura = f.factura
INNER JOIN productos p
ON v.producto = p.code
WHERE
p.mark NOT IN ('', '-')
)
SELECT
año,
mes,
marca,
tipo_producto,
SUM(cantidad) AS unidades_vendidas,
SUM(monto_dolar) AS ventas
FROM facturaciones_marcas
GROUP BY
año,
mes,
marca,
tipo_producto
;
"""
).pl()
print('Transformacion de las facturaciones al mayor por marcas culminada')

# %%
################## Estadisticas por vendedor
print('Transformando las ventas por los vendedores al mayor')
traza_vendedores = duckdb.sql(
"""
WITH facturaciones AS (
SELECT
f.fecha,
EXTRACT(YEAR FROM f.fecha) AS año,
EXTRACT(MONTH FROM f.fecha) AS mes,
CASE
 WHEN EXTRACT(DAY FROM f.fecha) <= 15 THEN 1
 ELSE 2
END AS n_quincena,
CASE
 WHEN EXTRACT(DAY FROM f.fecha) <= 15 THEN '1ra quincena'
 ELSE '2da quincena'
END AS quincena,
f.factura,
TRUNC((v.monto / f.tasa_autocompletada)::NUMERIC,2) AS monto_dolar,
ve.description AS vendedor,
c.code AS rif,
c.description AS cliente,
c.phone AS telefono,
e.description AS estado,
CASE
 WHEN c.status_new = '01' THEN 'ACTIVO'
 WHEN c.status_new = '02' THEN 'INACTIVO'
 ELSE 'ELIMINADO'
END estatus,
c.case_client AS tipo
FROM facturas f
INNER JOIN ventas v
ON f.factura = v.factura
INNER JOIN vendedores ve
ON f.vendedor = ve.code
INNER JOIN clientes c
ON f.rif = c.code
INNER JOIN estados e
ON c.province = e.code
WHERE
ve.status_seller = 'ACTIVOS'
)
SELECT
año,
mes,
n_quincena,
quincena,
vendedor,
rif,
cliente,
estado,
estatus,
tipo,
COUNT(DISTINCT(factura)) AS facturas,
SUM(monto_dolar) AS monto_dolar
FROM facturaciones
GROUP BY
año,
mes,
n_quincena,
quincena,
vendedor,
rif,
cliente,
estado,
estatus,
tipo
;
"""
).pl()
print('Transformacion de las ventas por los vendedores al mayor culminada')

# %%
################## Revision detallada por facturas
print('Transformando los clientes gestionados al mayor')
clientes_gestionados = duckdb.sql(
"""
WITH primera_operacion AS (
SELECT
EXTRACT(YEAR FROM fa.fecha) AS año,
EXTRACT(MONTH FROM fa.fecha) AS mes,
es.description AS estado,
ve.description AS vendedor,
fa.factura,
cl.code AS rif,
cl.case_client AS tipo_cliente,
CASE
 WHEN status_new = '01' THEN 'ACTIVO'
 WHEN status_new = '02' THEN 'INACTIVO'
 ELSE status_new
END AS estatus
FROM facturas fa
INNER JOIN vendedores ve
ON fa.vendedor = ve.code
INNER JOIN clientes cl
ON fa.rif = cl.code
INNER JOIN estados es
ON cl.province = es.code
WHERE
ve.status_seller = 'ACTIVOS'
)
SELECT
año,
mes,
CASE
 WHEN mes = 1 THEN 'Enero'
 WHEN mes = 2 THEN 'Febrero'
 WHEN mes = 3 THEN 'Marzo'
 WHEN mes = 4 THEN 'Abril'
 WHEN mes = 5 THEN 'Mayo'
 WHEN mes = 6 THEN 'Junio'
 WHEN mes = 7 THEN 'Julio'
 WHEN mes = 8 THEN 'Agosto'
 WHEN mes = 9 THEN 'Septiembre'
 WHEN mes = 10 THEN 'Octubre'
 WHEN mes = 11 THEN 'Noviembre'
 ELSE 'Diciembre'
END AS nombre_mes,
estado,
vendedor,
tipo_cliente,
estatus,
COUNT(DISTINCT(factura)) AS facturas,
COUNT(DISTINCT(rif)) AS clientes_gestionados
FROM primera_operacion
GROUP BY
año,
mes,
estado,
vendedor,
tipo_cliente,
estatus
;
"""
).pl()
print('Transformacion de los clientes gestionados al mayor culminada')

# %%
################## Estadisticas por quincena-periodo
print('Transformando las ventas por las quincenas al mayor')
traza_quincenas = duckdb.sql(
"""
WITH facturaciones AS (
SELECT
f.fecha,
CASE
 WHEN EXTRACT(DAY FROM f.fecha) BETWEEN 6 AND 21 THEN 1
 ELSE 2
END AS n_quincena,
CASE
 WHEN EXTRACT(DAY FROM f.fecha) BETWEEN 6 AND 21 THEN '1ra quincena'
 ELSE '2da quincena'
END AS quincena,
f.factura,
TRUNC((v.monto / f.tasa_autocompletada)::NUMERIC,2) AS monto_dolar,
ve.description AS vendedor,
c.code AS rif,
c.description AS cliente,
c.phone AS telefono,
e.description AS estado,
CASE
 WHEN c.status_new = '01' THEN 'ACTIVO'
 WHEN c.status_new = '02' THEN 'INACTIVO'
 ELSE 'ELIMINADO'
END estatus,
c.case_client AS tipo,
ca.description AS categoria
FROM facturas f
INNER JOIN ventas v
ON f.factura = v.factura
INNER JOIN vendedores ve
ON f.vendedor = ve.code
INNER JOIN clientes c
ON f.rif = c.code
INNER JOIN estados e
ON c.province = e.code
INNER JOIN productos p
ON v.producto = p.code
INNER JOIN categorias ca
ON p.department = ca.code
WHERE
ve.status_seller = 'ACTIVOS'
AND f.fecha >= '2026-07-06'
)
SELECT
fecha,
n_quincena,
quincena,
vendedor,
rif,
cliente,
estado,
estatus,
tipo,
categoria,
SUM(monto_dolar) AS monto_dolar
FROM facturaciones
GROUP BY
fecha,
n_quincena,
quincena,
vendedor,
rif,
cliente,
estado,
estatus,
tipo,
categoria
;
"""
).pl()
print('Transformacion de las ventas por las quincenas al mayor culminada')

# %%
# Procesamiento
print('Empezando el procesamiento de los resultados')
with xlsxwriter.Workbook(r'C:\Users\POWERBI\Desktop\Entornos\almayor_stats\reports\almayor.xlsx') as workbook:
    bd_clientes.write_excel(workbook, worksheet='clientes')
    facturaciones.write_excel(workbook, worksheet='facturaciones')
    marcas.write_excel(workbook, worksheet='marcas')
    traza_vendedores.write_excel(workbook, worksheet='vendedores')
    clientes_gestionados.write_excel(workbook, worksheet='gestionados')
    traza_quincenas.write_excel(workbook, worksheet='quincenas')
print('Culminado el procesamiento de los resultados')


