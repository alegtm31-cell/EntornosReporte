# %%
# Librerias importadas
print('Leyendo librerias')
import pandas as pd
import numpy as np
import pyexcel as pe
import csv
from pathlib import Path
from datetime import date, datetime
from time import time
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

# %%
# Lectura de datos
print('Procesando datos')
sales = pd.read_parquet('C:/Users/POWERBI/Documents/Stored Data Parquet/AL MAYOR/almayor_detail_sales.parquet')
sales['emission_date'] = pd.to_datetime(sales['emission_date'], dayfirst=True).dt.date
sellers = pd.read_parquet('C:/Users/POWERBI/Documents/Stored Data Parquet/AL MAYOR/almayor_sellers.parquet')
clients = pd.read_parquet('C:/Users/POWERBI/Documents/Stored Data Parquet/AL MAYOR/almayor_clients.parquet')
provinces = pd.read_parquet('C:/Users/POWERBI/Documents/Stored Data Parquet/provinces.parquet')

# %%
# Cruce
df_join1 = pd.merge(sales, sellers, how='left', left_on='seller', right_on='code').copy()
df_join2 = pd.merge(df_join1, clients, left_on='client_code', right_on='code', how='left').copy()
df_join3 = pd.merge(df_join2, provinces, left_on='province', right_on='code', how='left').copy()
df = df_join3.iloc[:,[0,1,2,12,18,19,24,25,27]].copy()
df = df.sort_values(by=['emission_date', 'register_hour'], ascending=[False, False]).drop_duplicates(subset=['client_code'], keep='first')
df['status_new'] = df['status_new'].str.replace('01', 'ACTIVO')
df['status_new'] = df['status_new'].str.replace('02', 'INACTIVO')
df = df.rename(columns={
    'emission_date':'Ultima compra',
    'client_code':'RIF',
    'phone':'Telefono',
    'description_y':'Cliente',
    'status_new':'Estatus',
    'description':'Estado',
    'case_client':'Tipo de cliente'
    })
vendedores_activos = ['ABRAHAM MUÑOZ', 'ALEXANDER MUJICA', 'ANDREINA PERDOMO', 'ANTHONY LARA', 'DESIREE RANGEL', 'KIRVIN RAMIREZ', 'SCARLET GONZALEZ']
df['vendedor'] = np.where(df['description_x'].isin(vendedores_activos), 'Activo', 'No activo')

# %%
# Distribución de BD a vendedores
df_abraham_m = df[df['description_x'] == 'ABRAHAM MUÑOZ'].copy()
df_abraham_m = df_abraham_m.sort_values(by=['Cliente'])
df_abraham_m = df_abraham_m.iloc[:,[2,5,4,7,6,8,0]]

df_alexander_m = df[df['description_x'] == 'ALEXANDER MUJICA'].copy()
df_alexander_m = df_alexander_m.sort_values(by=['Cliente'])
df_alexander_m = df_alexander_m.iloc[:,[2,5,4,7,6,8,0]]

df_andreina_p = df[df['description_x'] == 'ANDREINA PERDOMO'].copy()
df_andreina_p = df_andreina_p.sort_values(by=['Cliente'])
df_andreina_p = df_andreina_p.iloc[:,[2,5,4,7,6,8,0]]

df_anthony_l = df[df['description_x'] == 'ANTHONY LARA'].copy()
df_anthony_l = df_anthony_l.sort_values(by=['Cliente'])
df_anthony_l = df_anthony_l.iloc[:,[2,5,4,7,6,8,0]]

df_desiree_r = df[df['description_x'] == 'DESIREE RANGEL'].copy()
df_desiree_r = df_desiree_r.sort_values(by=['Cliente'])
df_desiree_r = df_desiree_r.iloc[:,[2,5,4,7,6,8,0]]

df_kirvin_r = df[df['description_x'] == 'KIRVIN RAMIREZ'].copy()
df_kirvin_r = df_kirvin_r.sort_values(by=['Cliente'])
df_kirvin_r = df_kirvin_r.iloc[:,[2,5,4,7,6,8,0]]

df_scarlet_g = df[df['description_x'] == 'SCARLET GONZALEZ'].copy()
df_scarlet_g = df_scarlet_g.sort_values(by=['Cliente'])
df_scarlet_g = df_scarlet_g.iloc[:,[2,5,4,7,6,8,0]]

df_genericos = df[df['vendedor'] == 'No activo'].copy()
df_genericos = df_genericos.sort_values(by=['Cliente'])
df_genericos = df_genericos.iloc[:,[2,5,4,7,6,8,0]]

df_clientes_view = df[df['vendedor'] == 'Activo']
df_clientes_view = df_clientes_view.iloc[:, [2,5,4,7,6,8,0,3]].copy()
df_clientes_view = df_clientes_view.rename(columns={
    'description_x': 'Vendedor'
})

# %%
# Asignación de BDs
print('Guardando libros')
df_abraham_m.to_excel(r'C:\Users\POWERBI\Documents\Clientes_Almayor\Abraham Muñoz.xlsx', index=False)
df_alexander_m.to_excel(r'C:\Users\POWERBI\Documents\Clientes_Almayor\Alexander Mujica.xlsx', index=False)
df_andreina_p.to_excel(r'C:\Users\POWERBI\Documents\Clientes_Almayor\Andreina Perdomo.xlsx', index=False)
df_anthony_l.to_excel(r'C:\Users\POWERBI\Documents\Clientes_Almayor\Anthony Lara.xlsx', index=False)
df_desiree_r.to_excel(r'C:\Users\POWERBI\Documents\Clientes_Almayor\Desiree Rangel.xlsx', index=False)
df_kirvin_r.to_excel(r'C:\Users\POWERBI\Documents\Clientes_Almayor\Kirvin Ramirez.xlsx', index=False)
df_scarlet_g.to_excel(r'C:\Users\POWERBI\Documents\Clientes_Almayor\Scarlet Gonzalez.xlsx', index=False)
#df_genericos.to_excel(r'C:\Users\POWERBI\Documents\Clientes_Almayor\Genericos.xlsx', index=False)
df_clientes_view.to_excel(r'C:\Users\POWERBI\Documents\Clientes_Almayor\Clientes.xlsx', index=False)
print('Libros guardados')
input()


