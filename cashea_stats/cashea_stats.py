# %%
# Importar librerias
print('Leyendo librerias')
import urllib.parse
import os
import pandas as pd
import numpy as np
import polars as pl
import fastexcel
import pyarrow as pa
import pyarrow.parquet as pq
import time
import xlsxwriter
print("Librerias leidas")

# %%
# Leyendo tablas
facturas_cashea = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\cashea_bills_correccion.parquet')
detalles_facturas = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\cashea_bills_details.parquet')
productos = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\products.parquet')
departamentos = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\department.parquet')
usuarios = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\users.parquet')
financiamientos = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\finance_cashea.parquet')
pagos = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\pays_cashea.parquet')
telefonos_vendidos_cashea = pl.read_parquet(r'C:\Users\POWERBI\Documents\Stored Data Parquet\phones_cashea.parquet')
envios_mrw = pl.read_excel(r'C:\Users\POWERBI\Documents\Cashea\2026.xlsx', sheet_name='Data') 

# %%
#bill_report.head(3)
#len(facturas_cashea)
#facturas_cashea['factura'].n_unique()
#bill_report.unique().height
#detalles_facturas.filter(pl.col('factura').is_in(['X000003194']))

# %%
# Trabajando con los join de las datas
################################################################################################################
# Trabajando con los join de la data para las facturaciones
################################################################################################################
bill_report = facturas_cashea.join(detalles_facturas, left_on='factura', right_on='factura', how='inner')
bill_report = bill_report.join(productos, left_on='producto', right_on='code', how='inner')
bill_report = bill_report.join(departamentos, left_on='department', right_on='code', how='inner')
bill_report = bill_report.with_columns(
    (pl.col('monto') / pl.col('tasa_autocompletada')).round(2)
    .alias('monto_dolar')
)
bill_report = bill_report.with_columns(
    pl.col('hora').dt.hour()
    .alias('hora_segmento')
)
bill_report = bill_report.drop(['tasa_autocompletada', 'monto', 'producto', 'department', 'status',
                                'father_department'])
bill_report_backup = bill_report
################################################################################################################
# Trabajando con los join de la data para los financiamientos
################################################################################################################
financing_report = financiamientos.join(pagos, on='factura', how='left')
financing_report = financing_report.with_columns(
    (pl.col('saldo_total') / pl.col('tasa_factura')).round(2)
    .alias('saldo_dolar')
)
financing_report = financing_report.drop(['fecha_right', 'saldo_total', 'tasa_factura'])
financing_report = financing_report.with_columns(
    pl.when(pl.col('saldo_dolar').is_null())
    .then(0)
    .otherwise(1)
    .alias('factura_pagada')
)
financing_report_backup = financing_report
################################################################################################################
# Trabajando con la data para los telefonos vendidos
################################################################################################################
phones_report = telefonos_vendidos_cashea
################################################################################################################
# Trabajando con la data para los paquetes enviados por MRW
################################################################################################################
mrw_packs_report = envios_mrw

# %%
# Cambio de nombres y filtros
bill_report = bill_report_backup.rename({
    'mark': 'marca',
    'description_right': 'categoria',
    'description': 'producto'
})
bill_report = bill_report.filter(
    ~(
    pl.col('producto').str.to_lowercase().str.starts_with('combo') |
    pl.col('producto').str.to_lowercase().str.starts_with('tarifa delivery')
    )
)
financing_report = financing_report_backup.rename({
    'monto_dolar': 'financiamiento',
    'saldo_dolar': 'monto_pagado'
})

# %%
# Verificaciones
#print(f'Numero total de filas en las facturaciones de cashea {len(envios_mrw)}')
#print(f'Facturaciones unicas de cashea {envios_mrw.unique().height}')

# %%
# Procesamiento
print('Empezando el procesamiento de los resultados')
with xlsxwriter.Workbook(r'C:\Users\POWERBI\Desktop\Entornos\cashea_stats\reports\cashea.xlsx') as workbook:
    bill_report.write_excel(workbook, worksheet='facturaciones')
    financing_report.write_excel(workbook, worksheet='financiamientos')
    phones_report.write_excel(workbook, worksheet='telefonos')
    mrw_packs_report.write_excel(workbook, worksheet='mrw')
print('Culminado el procesamiento de los resultados') 


