import psycopg2
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os
import time

def generar_reporte():
    inicio_tiempo = time.time()
    print("Iniciando conexión a la base de datos PostgreSQL...")
    conn = psycopg2.connect(
        host='192.168.91.131',
        port=5432,
        dbname='cadm_j5004625301',
        user='postgres',
        password='Soloyo1234*-',
        client_encoding='UTF8'
    )
    
    print("Extrayendo detalle de facturas al mayor con cálculo de tasa del día...")
    # Query de todas las facturas al mayor con su tasa del día y unidades
    query_facturas = """
    WITH sales_base AS (
        SELECT 
            s.correlative,
            s.document_no as factura,
            s.emission_date as fecha,
            s.register_hour as hora,
            s.client_code as rif,
            s.client_name,
            s.seller as seller_code,
            COALESCE(NULLIF(TRIM(sel.description), ''), 'GENERICO') as vendedor,
            s.total_net_details as monto_bs,
            sc.sales_aliquot as tasa_dia,
            ROUND((s.total_net_details / NULLIF(sc.sales_aliquot, 0))::numeric, 2) as monto_usd
        FROM public.sales_operation s
        JOIN public.sales_operation_coins sc 
            ON s.correlative = sc.main_correlative AND sc.coin_code = '02'
        LEFT JOIN public.sellers sel 
            ON s.seller = sel.code
        WHERE s.user_code = 'ALMAYOR' 
          AND s.operation_type = 'BILL' 
          AND s.client_name <> 'ANULADO'
    ),
    invoice_units AS (
        SELECT 
            main_correlative,
            SUM(amount) as unidades
        FROM public.sales_operation_details
        GROUP BY main_correlative
    )
    SELECT 
        sb.correlative,
        sb.factura,
        sb.fecha,
        sb.hora,
        sb.rif,
        COALESCE(NULLIF(TRIM(c.description), ''), sb.client_name, sb.rif) as cliente_nombre,
        sb.vendedor,
        COALESCE(NULLIF(TRIM(p.description), ''), 'NO REGISTRADO') as provincia,
        COALESCE(iu.unidades, 0) as unidades,
        sb.tasa_dia,
        sb.monto_bs,
        sb.monto_usd
    FROM sales_base sb
    LEFT JOIN invoice_units iu ON sb.correlative = iu.main_correlative
    LEFT JOIN public.clients c ON sb.rif = c.code
    LEFT JOIN public.provinces p ON c.province = p.code
    ORDER BY sb.fecha DESC, sb.hora DESC;
    """
    
    df_facturas = pd.read_sql_query(query_facturas, conn)
    print(f"Facturas extraídas: {len(df_facturas):,}")
    
    print("Extrayendo resumen consolidado de clientes al mayor...")
    query_clientes = """
    WITH sales_base AS (
        SELECT 
            s.correlative,
            s.document_no as factura,
            s.emission_date as fecha,
            s.register_hour as hora,
            s.client_code as rif,
            s.client_name,
            s.seller as seller_code,
            COALESCE(NULLIF(TRIM(sel.description), ''), 'GENERICO') as vendedor,
            s.total_net_details as monto_bs,
            sc.sales_aliquot as tasa_dia,
            ROUND((s.total_net_details / NULLIF(sc.sales_aliquot, 0))::numeric, 2) as monto_usd
        FROM public.sales_operation s
        JOIN public.sales_operation_coins sc 
            ON s.correlative = sc.main_correlative AND sc.coin_code = '02'
        LEFT JOIN public.sellers sel 
            ON s.seller = sel.code
        WHERE s.user_code = 'ALMAYOR' 
          AND s.operation_type = 'BILL' 
          AND s.client_name <> 'ANULADO'
    ),
    invoice_units AS (
        SELECT 
            main_correlative,
            SUM(amount) as unidades
        FROM public.sales_operation_details
        GROUP BY main_correlative
    ),
    invoices_enriched AS (
        SELECT 
            sb.*,
            COALESCE(iu.unidades, 0) as unidades
        FROM sales_base sb
        LEFT JOIN invoice_units iu ON sb.correlative = iu.main_correlative
    ),
    ranked_sales AS (
        SELECT 
            ie.*,
            ROW_NUMBER() OVER (PARTITION BY ie.rif ORDER BY ie.fecha DESC, ie.hora DESC, ie.correlative DESC) as rn_desc,
            ROW_NUMBER() OVER (PARTITION BY ie.rif ORDER BY ie.fecha ASC, ie.hora ASC, ie.correlative ASC) as rn_asc
        FROM invoices_enriched ie
    ),
    client_sales_summary AS (
        SELECT 
            rif,
            COUNT(DISTINCT factura) as total_facturas,
            SUM(unidades) as total_unidades,
            SUM(monto_bs) as total_monto_bs,
            SUM(monto_usd) as total_monto_usd,
            MIN(fecha) as primera_compra,
            MAX(fecha) as ultima_compra
        FROM invoices_enriched
        GROUP BY rif
    ),
    ultimo_vendedor AS (
        SELECT rif, vendedor as vendedor_ultima_venta
        FROM ranked_sales
        WHERE rn_desc = 1
    ),
    primer_vendedor AS (
        SELECT rif, vendedor as primer_vendedor
        FROM ranked_sales
        WHERE rn_asc = 1
    )
    SELECT 
        css.rif,
        COALESCE(NULLIF(TRIM(c.description), ''), css.rif) as cliente_nombre,
        COALESCE(NULLIF(TRIM(p.description), ''), 'NO REGISTRADO') as provincia,
        uv.vendedor_ultima_venta as persona_que_le_vendio,
        pv.primer_vendedor,
        COALESCE(NULLIF(TRIM(sel_asig.description), ''), 'SIN ASIGNAR') as vendedor_ficha_cliente,
        COALESCE(NULLIF(TRIM(c.phone), ''), 'SIN TELEFONO') as telefono,
        css.total_unidades,
        css.total_monto_usd,
        css.total_monto_bs,
        css.total_facturas,
        css.primera_compra,
        css.ultima_compra
    FROM client_sales_summary css
    LEFT JOIN public.clients c ON css.rif = c.code
    LEFT JOIN public.provinces p ON c.province = p.code
    LEFT JOIN public.sellers sel_asig ON c.seller = sel_asig.code
    LEFT JOIN ultimo_vendedor uv ON css.rif = uv.rif
    LEFT JOIN primer_vendedor pv ON css.rif = pv.rif
    ORDER BY css.total_monto_usd DESC;
    """
    df_clientes = pd.read_sql_query(query_clientes, conn)
    print(f"Clientes al mayor consolidados: {len(df_clientes):,}")
    
    print("Extrayendo resumen de cliente por vendedor...")
    query_cliente_vendedor = """
    WITH sales_base AS (
        SELECT 
            s.correlative,
            s.document_no as factura,
            s.emission_date as fecha,
            s.client_code as rif,
            s.client_name,
            COALESCE(NULLIF(TRIM(sel.description), ''), 'GENERICO') as vendedor,
            s.total_net_details as monto_bs,
            ROUND((s.total_net_details / NULLIF(sc.sales_aliquot, 0))::numeric, 2) as monto_usd
        FROM public.sales_operation s
        JOIN public.sales_operation_coins sc 
            ON s.correlative = sc.main_correlative AND sc.coin_code = '02'
        LEFT JOIN public.sellers sel 
            ON s.seller = sel.code
        WHERE s.user_code = 'ALMAYOR' 
          AND s.operation_type = 'BILL' 
          AND s.client_name <> 'ANULADO'
    ),
    invoice_units AS (
        SELECT 
            main_correlative,
            SUM(amount) as unidades
        FROM public.sales_operation_details
        GROUP BY main_correlative
    )
    SELECT 
        sb.rif,
        COALESCE(NULLIF(TRIM(c.description), ''), sb.client_name, sb.rif) as cliente_nombre,
        COALESCE(NULLIF(TRIM(p.description), ''), 'NO REGISTRADO') as provincia,
        sb.vendedor,
        COUNT(DISTINCT sb.factura) as facturas,
        SUM(COALESCE(iu.unidades, 0)) as total_unidades,
        SUM(sb.monto_usd) as total_monto_usd,
        SUM(sb.monto_bs) as total_monto_bs,
        MIN(sb.fecha) as primera_venta,
        MAX(sb.fecha) as ultima_venta
    FROM sales_base sb
    LEFT JOIN invoice_units iu ON sb.correlative = iu.main_correlative
    LEFT JOIN public.clients c ON sb.rif = c.code
    LEFT JOIN public.provinces p ON c.province = p.code
    GROUP BY sb.rif, c.description, sb.client_name, p.description, sb.vendedor
    ORDER BY total_monto_usd DESC;
    """
    df_cliente_vendedor = pd.read_sql_query(query_cliente_vendedor, conn)
    print(f"Combinaciones Cliente-Vendedor: {len(df_cliente_vendedor):,}")
    
    print("Extrayendo resumen por vendedor...")
    query_resumen_vendedor = """
    WITH sales_base AS (
        SELECT 
            s.correlative,
            s.document_no as factura,
            s.client_code as rif,
            COALESCE(NULLIF(TRIM(sel.description), ''), 'GENERICO') as vendedor,
            s.total_net_details as monto_bs,
            ROUND((s.total_net_details / NULLIF(sc.sales_aliquot, 0))::numeric, 2) as monto_usd
        FROM public.sales_operation s
        JOIN public.sales_operation_coins sc 
            ON s.correlative = sc.main_correlative AND sc.coin_code = '02'
        LEFT JOIN public.sellers sel 
            ON s.seller = sel.code
        WHERE s.user_code = 'ALMAYOR' 
          AND s.operation_type = 'BILL' 
          AND s.client_name <> 'ANULADO'
    ),
    invoice_units AS (
        SELECT 
            main_correlative,
            SUM(amount) as unidades
        FROM public.sales_operation_details
        GROUP BY main_correlative
    )
    SELECT 
        sb.vendedor,
        COUNT(DISTINCT sb.rif) as total_clientes,
        COUNT(DISTINCT sb.factura) as total_facturas,
        SUM(COALESCE(iu.unidades, 0)) as total_unidades,
        SUM(sb.monto_usd) as total_monto_usd,
        SUM(sb.monto_bs) as total_monto_bs
    FROM sales_base sb
    LEFT JOIN invoice_units iu ON sb.correlative = iu.main_correlative
    GROUP BY sb.vendedor
    ORDER BY total_monto_usd DESC;
    """
    df_vendedores = pd.read_sql_query(query_resumen_vendedor, conn)
    
    print("Extrayendo resumen por provincia...")
    query_resumen_provincia = """
    WITH sales_base AS (
        SELECT 
            s.correlative,
            s.document_no as factura,
            s.client_code as rif,
            s.total_net_details as monto_bs,
            ROUND((s.total_net_details / NULLIF(sc.sales_aliquot, 0))::numeric, 2) as monto_usd
        FROM public.sales_operation s
        JOIN public.sales_operation_coins sc 
            ON s.correlative = sc.main_correlative AND sc.coin_code = '02'
        WHERE s.user_code = 'ALMAYOR' 
          AND s.operation_type = 'BILL' 
          AND s.client_name <> 'ANULADO'
    ),
    invoice_units AS (
        SELECT 
            main_correlative,
            SUM(amount) as unidades
        FROM public.sales_operation_details
        GROUP BY main_correlative
    )
    SELECT 
        COALESCE(NULLIF(TRIM(p.description), ''), 'NO REGISTRADO') as provincia,
        COUNT(DISTINCT sb.rif) as total_clientes,
        COUNT(DISTINCT sb.factura) as total_facturas,
        SUM(COALESCE(iu.unidades, 0)) as total_unidades,
        SUM(sb.monto_usd) as total_monto_usd,
        SUM(sb.monto_bs) as total_monto_bs
    FROM sales_base sb
    LEFT JOIN invoice_units iu ON sb.correlative = iu.main_correlative
    LEFT JOIN public.clients c ON sb.rif = c.code
    LEFT JOIN public.provinces p ON c.province = p.code
    GROUP BY p.description
    ORDER BY total_monto_usd DESC;
    """
    df_provincias = pd.read_sql_query(query_resumen_provincia, conn)
    
    conn.close()
    print("Conexión con PostgreSQL cerrada con éxito.")
    
    # Exportación a CSV
    output_dir = r"c:\Users\YARBED\Desktop\Entornos\reportes_almayor"
    os.makedirs(output_dir, exist_ok=True)
    
    csv_clientes = os.path.join(output_dir, "clientes_almayor_consolidado.csv")
    csv_facturas = os.path.join(output_dir, "facturas_almayor_detalle.csv")
    
    df_clientes.to_csv(csv_clientes, index=False, encoding='utf-8-sig')
    df_facturas.to_csv(csv_facturas, index=False, encoding='utf-8-sig')
    print(f"CSVs exportados en: {output_dir}")
    
    # Generación de Excel con Openpyxl
    excel_path = os.path.join(output_dir, "Reporte_Clientes_AlMayor_Completo.xlsx")
    print(f"Generando libro Excel estilizado en: {excel_path}...")
    
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)
    
    # Styles
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    alt_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    border_thin = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )
    
    sheets_data = [
        ("Clientes Al Mayor", df_clientes, {
            "Total Unidades": "#,##0",
            "Monto Total USD ($)": "$#,##0.00",
            "Monto Total Bs.": "#,##0.00",
            "Total Facturas": "#,##0"
        }),
        ("Ventas Cliente-Vendedor", df_cliente_vendedor, {
            "Total Unidades": "#,##0",
            "Monto Total USD ($)": "$#,##0.00",
            "Monto Total Bs.": "#,##0.00",
            "Facturas": "#,##0"
        }),
        ("Resumen por Vendedor", df_vendedores, {
            "Total Clientes": "#,##0",
            "Total Facturas": "#,##0",
            "Total Unidades": "#,##0",
            "Total Ventas USD ($)": "$#,##0.00",
            "Total Ventas Bs.": "#,##0.00"
        }),
        ("Resumen por Provincia", df_provincias, {
            "Total Clientes": "#,##0",
            "Total Facturas": "#,##0",
            "Total Unidades": "#,##0",
            "Total Ventas USD ($)": "$#,##0.00",
            "Total Ventas Bs.": "#,##0.00"
        }),
        ("Detalle de Facturas", df_facturas, {
            "Unidades": "#,##0",
            "Tasa del Día (Bs/$)": "#,##0.00",
            "Monto Bs.": "#,##0.00",
            "Monto USD ($)": "$#,##0.00"
        })
    ]
    
    # Column rename mappings for friendly display
    name_maps = {
        "rif": "RIF / Código",
        "cliente_nombre": "Nombre del Cliente",
        "provincia": "Provincia / Estado",
        "persona_que_le_vendio": "Persona que le Vendió (Última Venta)",
        "primer_vendedor": "Primer Vendedor",
        "vendedor_ficha_cliente": "Vendedor Asignado (Ficha)",
        "telefono": "Teléfono",
        "total_unidades": "Total Unidades",
        "total_monto_usd": "Monto Total USD ($)",
        "total_monto_bs": "Monto Total Bs.",
        "total_facturas": "Total Facturas",
        "primera_compra": "Primera Compra",
        "ultima_compra": "Última Compra",
        "vendedor": "Vendedor",
        "facturas": "Facturas",
        "primera_venta": "Primera Venta",
        "ultima_venta": "Última Venta",
        "total_clientes": "Total Clientes",
        "correlative": "ID Operación",
        "factura": "Nro Factura",
        "fecha": "Fecha Venta",
        "hora": "Hora Registro",
        "unidades": "Unidades",
        "tasa_dia": "Tasa del Día (Bs/$)",
        "monto_bs": "Monto Bs.",
        "monto_usd": "Monto USD ($)"
    }
    
    for sheet_name, df, num_formats in sheets_data:
        ws = wb.create_sheet(title=sheet_name)
        ws.views.sheetView[0].showGridLines = True
        
        # Rename columns for headers
        headers = [name_maps.get(col, col) for col in df.columns]
        ws.append(headers)
        
        # Format header row
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = border_thin
        ws.row_dimensions[1].height = 28
        
        # Add data rows
        for row_idx, row_data in enumerate(df.itertuples(index=False), start=2):
            ws.append(list(row_data))
            is_alt = (row_idx % 2 == 0)
            for col_idx, val in enumerate(row_data, start=1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.border = border_thin
                if is_alt:
                    cell.fill = alt_fill
                
                header_name = headers[col_idx - 1]
                # Apply number formats
                if header_name in num_formats:
                    cell.number_format = num_formats[header_name]
                    cell.alignment = Alignment(horizontal="right")
                elif isinstance(val, (int, float)):
                    cell.alignment = Alignment(horizontal="right")
                elif "Fecha" in header_name or "Compra" in header_name or "Venta" in header_name:
                    cell.alignment = Alignment(horizontal="center")
                else:
                    cell.alignment = Alignment(horizontal="left")
                    
        # Auto-adjust column widths
        for col_idx, header_name in enumerate(headers, start=1):
            col_letter = get_column_letter(col_idx)
            max_len = len(header_name)
            # Sample up to 100 rows for length
            for r in range(2, min(ws.max_row + 1, 150)):
                v = ws.cell(row=r, column=col_idx).value
                if v is not None:
                    max_len = max(max_len, len(str(v)))
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)
            
    wb.save(excel_path)
    duracion = time.time() - inicio_tiempo
    print(f"[OK] Reporte generado exitosamente en {duracion:.2f} segundos!")
    print(f"Ruta Excel: {excel_path}")

if __name__ == "__main__":
    generar_reporte()
