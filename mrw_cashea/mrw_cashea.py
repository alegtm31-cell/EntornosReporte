# %%
# Leyendo librerias
print('Leyendo librerias')
import os
from pathlib import Path
import openpyxl
import re
import pdfplumber
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import sys
import warnings
print('Librerias leidas')

# %%
# Leyendo datos
print('Iniciando lectura de pdfs')
carpeta_pdf = 'C:/Users/POWERBI/Documents/Cashea/validando/'
resultados = []
for archivo in os.listdir(carpeta_pdf):
    if archivo.endswith('.pdf'):
        ruta_completa = os.path.join(carpeta_pdf, archivo)
        num_v = None
        todos_los_cs = []  # Lista para acumular TODOS los trackings de este PDF
        estados_destino = []
        telefonos_clientes = []
        pesos_paquetes = []
        ciudades_destino = []
        productos_entrega = []
        with pdfplumber.open(ruta_completa) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if texto:
                    # --- NUEVA REGLA 1: Buscar TODOS los CS- en la página ---
                    # re.findall nos devuelve una lista con todos los números encontrados
                    coincidencias_cs = re.findall(r'CS-(\d+)', texto)
                    todos_los_cs.extend(coincidencias_cs)
                    coincidencias_estados = re.findall(r'Estado destino\s*:\s*([^\n]+)', texto, re.IGNORECASE)
                    estados_destino.extend(coincidencias_estados)
                    coincidencias_telefonos = re.findall(r'Teléfono del Receptor\s*:\s*([^\n]+)', texto, re.IGNORECASE)
                    telefonos_clientes.extend(coincidencias_telefonos)
                    coincidencias_pesos = re.findall(r'Peso\s*:\s*([^\n]+)', texto, re.IGNORECASE)
                    pesos_paquetes.extend(coincidencias_pesos)
                    coincidencias_ciudades = re.findall(r'Ciudad destino\s*:\s*([^\n]+)', texto, re.IGNORECASE)
                    ciudades_destino.extend(coincidencias_ciudades)
                    coincidencias_productos = re.findall(r'DESCRIPCIÓN DEL CONTENIDO DEL PAQUETE\s*:\s*(.+?),\s*', texto, re.IGNORECASE | re.DOTALL)
                    productos_entrega.extend(coincidencias_productos)
                    # --- REGLA 2: Mantener la búsqueda de la "V" línea por línea ---
                    for linea in texto.split('\n'):
                        linea = linea.strip()
                        if not num_v:
                            match_v = re.search(r'V\s*(\d+)', linea)
                            if match_v:
                                num_v = match_v.group(1)
                            elif linea.isdigit() and (6 <= len(linea) <= 9):
                                num_v = linea
        # Asignamos de forma segura la primera y segunda coincidencia
        # Usamos un "if" corto para evitar errores si el PDF tiene menos de 2 trackings
        num_cs_1 = todos_los_cs[0] if len(todos_los_cs) > 0 else None
        num_cs_2 = todos_los_cs[1] if len(todos_los_cs) > 1 else None
        estado = estados_destino[0] if len(estados_destino) > 0 else None
        ciudad = ciudades_destino[0] if len(ciudades_destino) > 0 else None
        telefono = telefonos_clientes[0] if len(telefonos_clientes) > 0 else None
        peso = pesos_paquetes[0] if len(pesos_paquetes) > 0 else None
        producto = productos_entrega[0] if len(productos_entrega) > 0 else None
        # Guardamos los datos organizados en columnas distintas
        resultados.append({
            'Origen_Archivo': archivo,
            'CEDULA': num_v,
            'TRACKING': num_cs_1,
            'CS-': num_cs_2,
            'ESTADO': estado,
            'CIUDAD': ciudad,
            'TELEFONO': telefono,
            'PESO': peso,
            'PRODUCTO': producto
        })
df_final = pd.DataFrame(resultados)
df_final = df_final.iloc[:, [2,3,1,4,5,6,7,8]]
df_final['TELEFONO'] = df_final['TELEFONO'].str.replace('+58', '')
df_final['PESO'] = df_final['PESO'].str.replace(' Kg', '')
print('Lectura finalizada')

# %%
# Inciando el guardado de archivos
print("Guarda la guia de caseha:")
ruta_salida = filedialog.asksaveasfilename(
    title="Guardando la guia de cashea",
    defaultextension=".xlsx",
    filetypes=[("Libro de excel", "*.xlsx")]
)
if ruta_salida:
    df_final.to_excel(ruta_salida, index=False)
    print("Guardado sin problemas las guias de cashea")

# %%
# Lectura de multiples libros y procesamiento de datos
carpeta_excel = Path('C:/Users/POWERBI/Documents/Cashea/recibidos')
archivos_mrw = list(carpeta_excel.glob('*.xlsx'))
mrw_cashea_df = []
for mc_file in archivos_mrw:
    mc_df = pd.read_excel(mc_file)
    mc_df['FECHA'] = mc_file.name
    mrw_cashea_df.append(mc_df)
tabla_mrw_cashea = pd.concat(mrw_cashea_df, ignore_index=True)
tabla_mrw_cashea['PRODUCTO'] = tabla_mrw_cashea['PRODUCTO'].str.replace('\n', ' ')
tabla_mrw_cashea['FECHA'] = tabla_mrw_cashea['FECHA'].str.replace('.xlsx', '')
tabla_mrw_cashea.to_csv(r'C:\Users\POWERBI\Desktop\Entornos\mrw_cashea\reports\packages.csv', index=False, encoding='utf-8-sig')


