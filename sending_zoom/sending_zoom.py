# %%
# Leyendo librerias
print('Leyendo librerias')
import pandas as pd
import numpy as np
import openpyxl
import os
from pathlib import Path

# %%
# Carpetas definidas de lectura
print('Comenzando procesos')
carpeta_almayor = Path(r'C:\Users\POWERBI\Documents\Zoom\450432')
carpeta_aldetal = Path(r'C:\Users\POWERBI\Documents\Zoom\452371')


# %%
# Procesos de lectura
##################### AL MAYOR #####################
almayor_files = list(carpeta_almayor.glob('*.xlsx'))
almayor_df = []
for am_file in almayor_files:
    am_df = pd.read_excel(am_file, skiprows=1)
    am_df = am_df.iloc[:, 1:]
    almayor_df.append(am_df)
almayor_tabla = pd.concat(almayor_df, ignore_index=True)

##################### AL DETAL #####################
aldetal_files = list(carpeta_aldetal.glob('*.xlsx'))
aldetal_df = []
for ad_file in aldetal_files:
    ad_df = pd.read_excel(ad_file, skiprows=1)
    ad_df = ad_df.iloc[:, 1:]
    aldetal_df.append(ad_df)
aldetal_tabla = pd.concat(aldetal_df, ignore_index=True)

##################### PAQUETES DECLARADOS #####################
files_sended = pd.read_excel(r'C:\Users\POWERBI\Documents\Zoom\envios_declarados.xlsx')

# %%
# Procesamiento de datos
almayor_tabla['Paquetes registrados Al mayor'] = almayor_tabla.groupby(['Fecha', 'Ciudad Destino'])['Piezas'].transform('sum')
aldetal_tabla['Paquetes registrados Al detal'] = aldetal_tabla.groupby(['Fecha', 'Ciudad Destino'])['Piezas'].transform('sum')
almayor_tabla = almayor_tabla.iloc[:, [0,1,12,13]]
aldetal_tabla = aldetal_tabla.iloc[:, [0,1,12,13]]
almayor_tabla['Tipo'] = 'Al mayor'
aldetal_tabla['Tipo'] = 'Al detal'

# %%
# Verificacion de informacion
print('Identificando incoherencias')
print(f'AL MAYOR: Filas: {len(almayor_tabla)}, Guias unicas: {almayor_tabla['Guía'].nunique()}')
print(f'AL DETAL: Filas: {len(aldetal_tabla)}, Guias unicas: {aldetal_tabla['Guía'].nunique()}')

# %%
# Union de tablas
tabla = pd.concat([almayor_tabla, aldetal_tabla], ignore_index=True)
tabla['Fecha'] = pd.to_datetime(tabla['Fecha'], dayfirst=True)
tabla_full = pd.merge(
    tabla,
    files_sended,
    on=['Fecha', 'Tipo'],
    how='outer'
)
tabla_full_df = tabla_full.groupby(['Fecha', 'Tipo']).agg({
    'Piezas': 'sum',
    'Enviados': 'mean'
}).reset_index()

# %%
# Guardado de archivos a libros de excel
print('Guardando libros')
with pd.ExcelWriter(r'C:\Users\POWERBI\Desktop\Entornos\sending_zoom\reports\kpi_zoom.xlsx', engine='openpyxl') as writer:
    tabla.to_excel(writer, sheet_name='guias', index=False)
    tabla_full_df.to_excel(writer, sheet_name='envios & registros', index=False)

print('Proceso terminado')
