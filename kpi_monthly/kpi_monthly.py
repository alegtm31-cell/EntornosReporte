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
productos = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\products.parquet')
categorias = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\department.parquet')
categorias_padre = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\father_department.parquet')
existencias = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\stores_stocks.parquet')
ventas = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL DETAL y AL MAYOR\details_sales_correccion.parquet')
facturas = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\AL DETAL y AL MAYOR\general_sales_correccion.parquet')
print('Tablas leidas correctamente')

# %%
# Verificación
#duckdb.sql(""" SELECT * FROM existencias LIMIT 3 """)

# %%
# Transformaciones ################## Historico de ventas
print('Transformando el historico de las ventas al mayor y al detal')
historico_ventas = duckdb.sql(
"""
WITH facturaciones_con_montos AS (
SELECT
fa.fecha,
CASE
 WHEN fa.usuario = 'ALMAYOR' THEN 'AL MAYOR'
 ELSE 'AL DETAL'
END AS usuario,
CASE
 WHEN UPPER(LEFT(p.description,8)) = 'TELEFONO' THEN 'TELEFONOS'
 WHEN p.department IN ('02', '03', '031', '05', '06', '08', '09', '10', '11', '12') THEN 'ACCESORIOS'
 ELSE 'OTROS'
END AS tipo_producto,
CASE
 WHEN UPPER(p.mark) = '1-HORA' THEN '1 HORA'
 WHEN UPPER(p.mark) = 'GO-PRO' THEN 'GO PRO'
 WHEN UPPER(p.mark) = 'X-BYTE' THEN 'X BYTE'
 ELSE UPPER(p.mark)
END AS marca,
c.description AS categoria,
ve.cantidad AS unidades,
TRUNC((ve.monto / fa.tasa_autocompletada)::NUMERIC,2) AS ingreso
FROM facturas fa
INNER JOIN ventas ve
ON fa.factura = ve.factura
INNER JOIN productos p
ON ve.producto = p.code
INNER JOIN categorias c
ON p.department = c.code
WHERE
EXTRACT(YEAR FROM fa.fecha) >= EXTRACT(YEAR FROM DATE(NOW())) - 2
)
SELECT
fecha,
usuario,
SUM(unidades) AS unidades,
SUM(ingreso) AS ingreso
FROM facturaciones_con_montos
GROUP BY
fecha,
usuario
;
"""
).pl()
print('Transformacion de las estadisticas del historico de las ventas al mayor y al detal')

# %%
# Ventas por segmentos
print('Transformando la comparativa de las ventas al mayor y al detal por segmentos')
segmentos = duckdb.sql(
"""
WITH facturaciones_con_montos AS (
SELECT
fa.fecha,
EXTRACT(YEAR FROM fa.fecha) AS año,
--año
EXTRACT(MONTH FROM fa.fecha) AS mes,
CASE
 WHEN fa.usuario = 'ALMAYOR' THEN 'AL MAYOR'
 ELSE 'AL DETAL'
END AS usuario,
CASE
 WHEN UPPER(LEFT(p.description,8)) = 'TELEFONO' THEN 'TELEFONOS'
 WHEN p.department IN ('02', '03', '031', '05', '06', '08', '09', '10', '11', '12') THEN 'ACCESORIOS'
 ELSE 'OTROS'
END AS tipo_producto,
CASE
 WHEN UPPER(p.mark) = '1-HORA' THEN '1 HORA'
 WHEN UPPER(p.mark) = 'GO-PRO' THEN 'GO PRO'
 WHEN UPPER(p.mark) = 'X-BYTE' THEN 'X BYTE'
 ELSE UPPER(p.mark)
END AS marca,
c.description AS categoria,
ve.cantidad AS unidades,
TRUNC((ve.monto / fa.tasa_autocompletada)::NUMERIC,2) AS ingreso
FROM facturas fa
INNER JOIN ventas ve
ON fa.factura = ve.factura
INNER JOIN productos p
ON ve.producto = p.code
INNER JOIN categorias c
ON p.department = c.code
WHERE
EXTRACT(YEAR FROM fa.fecha) >= EXTRACT(YEAR FROM DATE(NOW())) - 2
)
SELECT
año,
mes,
usuario,
tipo_producto,
categoria,
marca,
SUM(unidades) AS unidades,
SUM(ingreso) AS ingreso
FROM facturaciones_con_montos
GROUP BY
año,
mes,
usuario,
tipo_producto,
categoria,
marca
;
"""
).pl()
print('Transformacion de las estadisticas de la comparativa de las ventas al mayor y al detal por segmentos')

# %%
# Top unidades vendidas
print('Transformando las ventas al mayor y al detal por productos mayormente vendidos')
top_unidades = duckdb.sql(
"""
WITH facturaciones_con_montos AS (
SELECT
EXTRACT(YEAR FROM fa.fecha) AS año,
--año
EXTRACT(MONTH FROM fa.fecha) AS mes,
CASE
 WHEN fa.usuario = 'ALMAYOR' THEN 'AL MAYOR'
 ELSE 'AL DETAL'
END AS usuario,
CASE
 WHEN UPPER(LEFT(p.description,8)) = 'TELEFONO' THEN 'TELEFONOS'
 WHEN p.department IN ('02', '03', '031', '05', '06', '08', '09', '10', '11', '12') THEN 'ACCESORIOS'
 ELSE 'OTROS'
END AS tipo_producto,
CASE
 WHEN UPPER(p.mark) = '1-HORA' THEN '1 HORA'
 WHEN UPPER(p.mark) = 'GO-PRO' THEN 'GO PRO'
 WHEN UPPER(p.mark) = 'X-BYTE' THEN 'X BYTE'
 ELSE UPPER(p.mark)
END AS marca,
c.description AS categoria,
p.description AS producto,
ve.cantidad AS unidades,
TRUNC((ve.monto / fa.tasa_autocompletada)::NUMERIC,2) AS ingreso
FROM facturas fa
INNER JOIN ventas ve
ON fa.factura = ve.factura
INNER JOIN productos p
ON ve.producto = p.code
INNER JOIN categorias c
ON p.department = c.code
WHERE
EXTRACT(YEAR FROM fa.fecha) >= EXTRACT(YEAR FROM DATE(NOW())) - 2
),
agrupacion AS (
SELECT
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
SUM(unidades) AS unidades_vendidas,
SUM(ingreso) AS ingreso
FROM facturaciones_con_montos
GROUP BY
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto
),
filtrado AS (
SELECT
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
unidades_vendidas,
ingreso,
DENSE_RANK() OVER(PARTITION BY año, mes, usuario, tipo_producto, marca, categoria ORDER BY unidades_vendidas DESC) AS ranking
FROM agrupacion
)
SELECT
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
unidades_vendidas,
ingreso,
ranking
FROM filtrado
WHERE
ranking <= 10
AND marca NOT IN ('', '-')
AND categoria <> 'GENERICO'
AND año = EXTRACT(YEAR FROM DATE(NOW()))
;
"""
).pl()
print('Transformacion de las estadisticas de las ventas al mayor y al detal por productos mayormente vendidos')

# %%
# Top montos facturados
print('Transformando las ventas al mayor y al detal por productos con mayor facturacion')
top_ingresos = duckdb.sql(
"""
WITH facturaciones_con_montos AS (
SELECT
EXTRACT(YEAR FROM fa.fecha) AS año,
--año
EXTRACT(MONTH FROM fa.fecha) AS mes,
CASE
 WHEN fa.usuario = 'ALMAYOR' THEN 'AL MAYOR'
 ELSE 'AL DETAL'
END AS usuario,
CASE
 WHEN UPPER(LEFT(p.description,8)) = 'TELEFONO' THEN 'TELEFONOS'
 WHEN p.department IN ('02', '03', '031', '05', '06', '08', '09', '10', '11', '12') THEN 'ACCESORIOS'
 ELSE 'OTROS'
END AS tipo_producto,
CASE
 WHEN UPPER(p.mark) = '1-HORA' THEN '1 HORA'
 WHEN UPPER(p.mark) = 'GO-PRO' THEN 'GO PRO'
 WHEN UPPER(p.mark) = 'X-BYTE' THEN 'X BYTE'
 ELSE UPPER(p.mark)
END AS marca,
c.description AS categoria,
p.description AS producto,
ve.cantidad AS unidades,
TRUNC((ve.monto / fa.tasa_autocompletada)::NUMERIC,2) AS ingreso
FROM facturas fa
INNER JOIN ventas ve
ON fa.factura = ve.factura
INNER JOIN productos p
ON ve.producto = p.code
INNER JOIN categorias c
ON p.department = c.code
WHERE
EXTRACT(YEAR FROM fa.fecha) >= EXTRACT(YEAR FROM DATE(NOW())) - 2
),
agrupacion AS (
SELECT
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
SUM(unidades) AS unidades_vendidas,
SUM(ingreso) AS ingreso
FROM facturaciones_con_montos
GROUP BY
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto
),
filtrado AS (
SELECT
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
unidades_vendidas,
ingreso,
DENSE_RANK() OVER(PARTITION BY año, mes, usuario, tipo_producto, marca, categoria ORDER BY ingreso DESC) AS ranking
FROM agrupacion
)
SELECT
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
unidades_vendidas,
ingreso,
ranking
FROM filtrado
WHERE
ranking <= 10
AND marca NOT IN ('', '-')
AND categoria <> 'GENERICO'
AND año = EXTRACT(YEAR FROM DATE(NOW()))
;
"""
).pl()
print('Transformacion de las estadisticas de las ventas al mayor y al detal con mayor facturacion')

# %%
# Bottom unidades vendidas
print('Transformando las ventas al mayor y al detal por productos con menores unidades vendidas')
bottom_unidades = duckdb.sql(
"""
WITH facturaciones_con_montos AS (
SELECT
EXTRACT(YEAR FROM fa.fecha) AS año,
--año
EXTRACT(MONTH FROM fa.fecha) AS mes,
CASE
 WHEN fa.usuario = 'ALMAYOR' THEN 'AL MAYOR'
 ELSE 'AL DETAL'
END AS usuario,
CASE
 WHEN UPPER(LEFT(p.description,8)) = 'TELEFONO' THEN 'TELEFONOS'
 WHEN p.department IN ('02', '03', '031', '05', '06', '08', '09', '10', '11', '12') THEN 'ACCESORIOS'
 ELSE 'OTROS'
END AS tipo_producto,
CASE
 WHEN UPPER(p.mark) = '1-HORA' THEN '1 HORA'
 WHEN UPPER(p.mark) = 'GO-PRO' THEN 'GO PRO'
 WHEN UPPER(p.mark) = 'X-BYTE' THEN 'X BYTE'
 ELSE UPPER(p.mark)
END AS marca,
c.description AS categoria,
p.description AS producto,
ve.cantidad AS unidades,
TRUNC((ve.monto / fa.tasa_autocompletada)::NUMERIC,2) AS ingreso
FROM facturas fa
INNER JOIN ventas ve
ON fa.factura = ve.factura
INNER JOIN productos p
ON ve.producto = p.code
INNER JOIN categorias c
ON p.department = c.code
WHERE
EXTRACT(YEAR FROM fa.fecha) >= EXTRACT(YEAR FROM DATE(NOW())) - 2
),
agrupacion AS (
SELECT
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
SUM(unidades) AS unidades_vendidas,
SUM(ingreso) AS ingreso
FROM facturaciones_con_montos
GROUP BY
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto
),
filtrado AS (
SELECT
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
unidades_vendidas,
ingreso,
DENSE_RANK() OVER(PARTITION BY año, mes, usuario, tipo_producto, marca, categoria ORDER BY unidades_vendidas) AS ranking
FROM agrupacion
)
SELECT
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
unidades_vendidas,
ingreso,
ranking
FROM filtrado
WHERE
ranking <= 10
AND marca NOT IN ('', '-')
AND categoria <> 'GENERICO'
AND año = EXTRACT(YEAR FROM DATE(NOW()))
;
"""
).pl()
print('Transformacion de las estadisticas de las ventas al mayor y al detal por productos con menores ventas')

# %%
# Bottom montos facturados
print('Transformando las ventas al mayor y al detal por productos con menor facturacion')
bottom_ingresos = duckdb.sql(
"""
WITH facturaciones_con_montos AS (
SELECT
EXTRACT(YEAR FROM fa.fecha) AS año,
--año
EXTRACT(MONTH FROM fa.fecha) AS mes,
CASE
 WHEN fa.usuario = 'ALMAYOR' THEN 'AL MAYOR'
 ELSE 'AL DETAL'
END AS usuario,
CASE
 WHEN UPPER(LEFT(p.description,8)) = 'TELEFONO' THEN 'TELEFONOS'
 WHEN p.department IN ('02', '03', '031', '05', '06', '08', '09', '10', '11', '12') THEN 'ACCESORIOS'
 ELSE 'OTROS'
END AS tipo_producto,
CASE
 WHEN UPPER(p.mark) = '1-HORA' THEN '1 HORA'
 WHEN UPPER(p.mark) = 'GO-PRO' THEN 'GO PRO'
 WHEN UPPER(p.mark) = 'X-BYTE' THEN 'X BYTE'
 ELSE UPPER(p.mark)
END AS marca,
c.description AS categoria,
p.description AS producto,
ve.cantidad AS unidades,
TRUNC((ve.monto / fa.tasa_autocompletada)::NUMERIC,2) AS ingreso
FROM facturas fa
INNER JOIN ventas ve
ON fa.factura = ve.factura
INNER JOIN productos p
ON ve.producto = p.code
INNER JOIN categorias c
ON p.department = c.code
WHERE
EXTRACT(YEAR FROM fa.fecha) >= EXTRACT(YEAR FROM DATE(NOW())) - 2
),
agrupacion AS (
SELECT
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
SUM(unidades) AS unidades_vendidas,
SUM(ingreso) AS ingreso
FROM facturaciones_con_montos
GROUP BY
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto
),
filtrado AS (
SELECT
año,
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
unidades_vendidas,
ingreso,
DENSE_RANK() OVER(PARTITION BY año, mes, usuario, tipo_producto, marca, categoria ORDER BY ingreso) AS ranking
FROM agrupacion
)
SELECT
mes,
usuario,
tipo_producto,
marca,
categoria,
producto,
unidades_vendidas,
ingreso,
ranking
FROM filtrado
WHERE
ranking <= 10
AND marca NOT IN ('', '-')
AND categoria <> 'GENERICO'
AND año = EXTRACT(YEAR FROM DATE(NOW()))
;
"""
).pl()
print('Transformacion de las estadisticas de las ventas al mayor y al detal con menor facturacion')

# %%
# Progreso de facturacion por productos
print('Transformando las ventas al mayor y al detal por productos')
telefonos = duckdb.sql(
"""
WITH facturaciones_con_montos AS (
SELECT
fa.fecha,
EXTRACT(YEAR FROM fa.fecha) AS año,
--año
EXTRACT(MONTH FROM fa.fecha) AS mes,
CASE
 WHEN fa.usuario = 'ALMAYOR' THEN 'AL MAYOR'
 ELSE 'AL DETAL'
END AS usuario,
CASE
 WHEN UPPER(LEFT(p.description,8)) = 'TELEFONO' THEN 'TELEFONOS'
 WHEN p.department IN ('02', '03', '031', '05', '06', '08', '09', '10', '11', '12') THEN 'ACCESORIOS'
 ELSE 'OTROS'
END AS tipo_producto,
CASE
 WHEN UPPER(p.mark) = '1-HORA' THEN '1 HORA'
 WHEN UPPER(p.mark) = 'GO-PRO' THEN 'GO PRO'
 WHEN UPPER(p.mark) = 'X-BYTE' THEN 'X BYTE'
 ELSE UPPER(p.mark)
END AS marca,
c.description AS categoria,
p.description AS producto,
ve.cantidad AS unidades,
TRUNC((ve.monto / fa.tasa_autocompletada)::NUMERIC,2) AS ingreso
FROM facturas fa
INNER JOIN ventas ve
ON fa.factura = ve.factura
INNER JOIN productos p
ON ve.producto = p.code
INNER JOIN categorias c
ON p.department = c.code
WHERE
EXTRACT(YEAR FROM fa.fecha) >= EXTRACT(YEAR FROM DATE(NOW())) - 2
),
agrupacion AS (
SELECT
fecha,
usuario,
tipo_producto,
marca,
categoria,
producto,
SUM(unidades) AS unidades_vendidas,
SUM(ingreso) AS ingreso
FROM facturaciones_con_montos
GROUP BY
fecha,
usuario,
tipo_producto,
marca,
categoria,
producto
)
SELECT
fecha,
marca,
producto,
unidades_vendidas,
ingreso
FROM agrupacion
WHERE
marca NOT IN ('', '-')
AND tipo_producto = 'TELEFONOS'
AND categoria <> 'GENERICO'
AND EXTRACT(YEAR FROM fecha) = EXTRACT(YEAR FROM DATE(NOW()))
AND usuario = 'AL DETAL'
;
"""
).pl()
print('Transformacion de las estadisticas de las ventas al mayor y al detal por productos')

# %%
# Procesamiento
print('Empezando el procesamiento de los resultados al detal y al mayor')
with xlsxwriter.Workbook(r'C:\Users\POWERBI\Desktop\Entornos\kpi_monthly\kpi_reports\kpi_monthly.xlsx') as workbook:
    historico_ventas.write_excel(workbook, worksheet='historico')
    segmentos.write_excel(workbook, worksheet='segmentos')
    top_unidades.write_excel(workbook, worksheet='top_unidades')
    top_ingresos.write_excel(workbook, worksheet='top_ingresos')
    bottom_unidades.write_excel(workbook, worksheet='bottom_unidades')
    bottom_ingresos.write_excel(workbook, worksheet='bottom_ingresos')
    telefonos.write_excel(workbook, worksheet='telefonos')
print('Procesamientos terminados')


