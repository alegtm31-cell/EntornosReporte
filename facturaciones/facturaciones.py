import sys
import os
import time
from datetime import datetime
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from flask import Flask, render_template_string, request, send_from_directory, abort

# ============================================================
# DETECCIÓN DE ENTORNO (PyInstaller vs Desarrollo)
# ============================================================
if getattr(sys, 'frozen', False):
    # Cuando se ejecuta como .exe compilado por PyInstaller
    CARPETA_BASE = os.path.dirname(sys.executable)
else:
    # Cuando se ejecuta como .py normal
    CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))

DIRECTORIO_SALIDA = os.path.join(CARPETA_BASE, "reportes")
os.makedirs(DIRECTORIO_SALIDA, exist_ok=True)

app = Flask(__name__)

# ============================================================
# CONEXIÓN A BASE DE DATOS
# ============================================================
drivername = "postgresql+psycopg2"
username = "postgres"          # <-- TUS CREDENCIALES REALES
host = "192.168.91.131"          # <-- TUS CREDENCIALES REALES
port = "5433"                  # <-- TUS CREDENCIALES REALES
database = "cadm_j5004625301"     # <-- TUS CREDENCIALES REALES
password = r"""Soloyo1234*-"""      # <-- TUS CREDENCIALES REALES

url_nopassword = f"{drivername}://{username}@{host}:{port}/{database}"
engine = create_engine(
    url_nopassword,
    connect_args={"password": password, "client_encoding": "latin1"}
)

# ============================================================
# FUNCIÓN ETL (Toda la lógica de facturaciones.py)
# ============================================================
def ejecutar_etl(fecha_inicio_str, fecha_fin_str):
    """
    Ejecuta todo el proceso de facturación.
    Retorna el nombre del archivo generado o lanza una excepción.
    """
    date1 = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    date2 = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()

    # --- 1. Lectura del histórico de tasas ---
    query_coin_history = text("""
        SELECT register_date, register_hour, sales_aliquot
        FROM public.coin_history
        WHERE main_code = '02';
    """)
    with engine.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT", postgresql_readonly=True)
        df_coin_history = pd.read_sql_query(query_coin_history, con=conn)

    # --- 2. Autocompletar tasas ---
    df = df_coin_history.copy()
    df['register_date'] = pd.to_datetime(df['register_date']).dt.date
    df = df.sort_values(['register_date', 'register_hour'])
    fecha_minima = df['register_date'].min()
    fecha_maxima = datetime.now().date()
    todas_fechas = pd.date_range(start=fecha_minima, end=fecha_maxima, freq='D').date
    horas_unicas = df['register_hour'].unique()
    base_fechas = pd.DataFrame({
        'FechaCompleta': np.repeat(todas_fechas, len(horas_unicas)),
        'register_hour': np.tile(horas_unicas, len(todas_fechas))
    })
    resultado = base_fechas.merge(df, left_on=['FechaCompleta', 'register_hour'],
                                   right_on=['register_date', 'register_hour'], how='left')
    resultado = resultado.drop('register_date', axis=1, errors='ignore')
    resultado = resultado.rename(columns={'FechaCompleta': 'Fecha'})
    resultado['Fecha'] = pd.to_datetime(resultado['Fecha']).dt.date
    resultado = resultado.sort_values(['Fecha', 'register_hour'])
    resultado.reset_index(drop=True, inplace=True)
    resultado['Índice'] = resultado.index + 1
    resultado['sales_aliquot'] = resultado['sales_aliquot'].ffill()
    df_conversion_tasa = resultado.sort_values(['Fecha', 'register_hour'], ascending=[False, False])

    # --- 3. Lectura de ventas ---
    query_detail_sales = text("""
        WITH details AS (
            SELECT d.line, s.document_no, s.emission_date, s.register_hour,
                   d.code_product, d.description_product, d.amount, d.price, p.minimum_price
            FROM sales_operation_details d
            INNER JOIN sales_operation s ON d.main_correlative = s.correlative
            INNER JOIN products_units p ON d.code_product = p.product_code
            WHERE s.operation_type = 'BILL'
              AND s.client_name <> 'ANULADO'
              AND s.user_code = 'ALMAYOR'
              AND s.emission_date BETWEEN :date1 AND :date2
        )
        SELECT * FROM details WHERE LEFT(document_no, 1) = 'T';
    """)
    with engine.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT", postgresql_readonly=True)
        df_detail_sales = pd.read_sql_query(query_detail_sales, con=conn,
                                             params={"date1": date1, "date2": date2})

    if df_detail_sales.empty:
        raise ValueError("No se encontraron facturas en el rango de fechas especificado.")

    # --- 4. Transformación ---
    ventas = df_detail_sales.copy()
    tasa = df_conversion_tasa.copy()
    ventas['emission_date'] = pd.to_datetime(ventas['emission_date']).dt.date
    tasa['Fecha'] = pd.to_datetime(tasa['Fecha']).dt.date
    tasa = tasa.rename(columns={'register_hour': 'hour_tasa_historico', 'Índice': 'indice_tasa_historico'})

    merged = pd.merge(ventas, tasa, left_on='emission_date', right_on='Fecha', how='left')
    merged = merged.sort_values(['emission_date', 'register_hour', 'hour_tasa_historico'])

    condiciones = [
        merged['line'] <= 535495,
        merged['hour_tasa_historico'].isna(),
        merged['register_hour'] < merged['hour_tasa_historico']
    ]
    opciones = [37.2, merged['sales_aliquot'], np.nan]
    merged['tasa_conversion_BsDollar'] = np.select(condiciones, opciones, default=merged['sales_aliquot'])
    merged['tasa_conversion_BsDollar'] = merged['tasa_conversion_BsDollar'].ffill()

    merged = merged.sort_values(['emission_date', 'register_hour', 'indice_tasa_historico'],
                                 ascending=[True, True, False])
    merged = merged.drop_duplicates(subset=['line'], keep='first')
    merged = merged.drop('sales_aliquot', axis=1)
    merged['total_net_dollar'] = (merged['price'] / merged['tasa_conversion_BsDollar']).round(2)
    merged = merged.drop(['hour_tasa_historico', 'indice_tasa_historico', 'register_hour'], axis=1)
    merged['coincidencia'] = np.where(merged['minimum_price'] == merged['total_net_dollar'],
                                       'Coincide', 'NO COINCIDE')

    columnas_finales = ['emission_date', 'document_no', 'code_product', 'description_product',
                         'minimum_price', 'total_net_dollar', 'coincidencia']
    merged = merged[columnas_finales]

    df_facturacion = merged.rename(columns={
        'emission_date': 'Fecha', 'document_no': 'Nota de entrega',
        'code_product': 'Codigo', 'description_product': 'Descripcion',
        'minimum_price': 'Precio Crystal', 'total_net_dollar': 'Precio Facturado',
        'coincidencia': 'Coincidencias'
    })

    # --- 5. Guardar archivo ---
    nombre_archivo = f"facturacion_{fecha_inicio_str}_a_{fecha_fin_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    ruta_salida = os.path.join(DIRECTORIO_SALIDA, nombre_archivo)
    df_facturacion.to_excel(ruta_salida, index=False)

    return nombre_archivo

# ============================================================
# INTERFAZ WEB (Flask)
# ============================================================
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Generación de Facturación</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 30px; border-radius: 8px;
                     box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
        h2 { color: #333; text-align: center; }
        label { font-weight: bold; color: #555; }
        input[type="date"] { width: 100%; padding: 10px; margin: 8px 0 20px 0;
                             border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; background: #007bff; color: white; padding: 12px;
                 border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #0056b3; }
        .success { color: #155724; background: #d4edda; border: 1px solid #c3e6cb;
                   padding: 15px; border-radius: 4px; margin-top: 20px; text-align: center; }
        .error { color: #721c24; background: #f8d7da; border: 1px solid #f5c6cb;
                 padding: 15px; border-radius: 4px; margin-top: 20px; white-space: pre-wrap; }
        .download-btn { display: inline-block; margin-top: 15px; background: #28a745;
                        color: white; padding: 10px 20px; text-decoration: none;
                        border-radius: 4px; font-weight: bold; }
        .download-btn:hover { background: #218838; }
    </style>
</head>
<body>
  <div class="container">
    <h2>📊 Generación de Facturaciones</h2>
    <form method="POST" action="/ejecutar">
      <label>Fecha de inicio:</label>
      <input type="date" name="inicio" required>
      <label>Fecha de fin:</label>
      <input type="date" name="fin" required>
      <button type="submit">⚡ Ejecutar Procesamiento</button>
    </form>
    {% if mensaje %}
      <div class="success">
        {{ mensaje }}<br>
        <a href="/descargar/{{ nombre_archivo }}" class="download-btn">⬇️ Descargar Excel</a>
      </div>
    {% endif %}
    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}
  </div>
</body>
</html>
'''

IP_PERMITIDAS = ['192.168.89.189', '192.168.89.79']
@app.before_request
def restringir_ip():
    ip_cliente = request.remote_addr
    if ip_cliente not in IP_PERMITIDAS:
        abort(403)

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/ejecutar', methods=['POST'])
def ejecutar():
    inicio = request.form['inicio']
    fin = request.form['fin']
    try:
        # Llamamos DIRECTAMENTE a la función (sin subprocess)
        nombre_archivo = ejecutar_etl(inicio, fin)
        mensaje = f"✅ ¡Proceso completado!\nRango: {inicio} a {fin}"
        return render_template_string(HTML, mensaje=mensaje, nombre_archivo=nombre_archivo)
    except ValueError as ve:
        return render_template_string(HTML, error=f"⚠️ {str(ve)}")
    except Exception as e:
        return render_template_string(HTML, error=f"❌ Error:\n{str(e)}")

@app.route('/descargar/<filename>')
def descargar_archivo(filename):
    return send_from_directory(DIRECTORIO_SALIDA, filename, as_attachment=True)

# ============================================================
# PUNTO DE ENTRADA
# ============================================================
if __name__ == '__main__':
    print("=" * 50)
    print("  SERVIDOR DE FACTURACIÓN INICIADO")
    print("  Abre tu navegador en: http://192.168.89.79:8080")
    print("=" * 50)
    import webbrowser
    webbrowser.open("http://192.168.89.79:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)

