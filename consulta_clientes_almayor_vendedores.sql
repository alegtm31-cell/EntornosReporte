-- ============================================================================
-- CONSULTA 1: LISTA CONSOLIDADA DE CLIENTES AL MAYOR POR VENDEDOR ESPECÍFICO
-- Vendedores filtrados:
--   1. ABRAHAM MUÑOZ   (Código: '25625528')
--   2. ALEXANDER MUJICA (Código: '25411189')
--   3. ANDREINA PERDOMO (Código: '23225823')
--   4. ANTHONY LARA    (Código: '22974980')
--   5. DESIREE RANGEL  (Código: '281502778')
--   6. KIRVIN RAMIREZ  (Código: '24057112')
--   7. SCARLET GONZALEZ (Código: '28386523')
-- ============================================================================

WITH invoice_units AS (
    -- Suma de unidades físicas por factura para evitar productos cartesianos
    SELECT 
        main_correlative,
        SUM(amount) AS total_unidades
    FROM public.sales_operation_details
    GROUP BY main_correlative
),
sales_base AS (
    -- Facturas al mayor con la tasa del día de la venta y conversión a USD
    SELECT 
        s.correlative,
        s.document_no AS factura,
        s.emission_date AS fecha,
        s.register_hour AS hora,
        s.client_code AS rif,
        s.client_name,
        s.seller AS seller_code,
        sel.description AS vendedor,
        s.total_net_details AS monto_bs,
        sc.sales_aliquot AS tasa_del_dia,
        ROUND((s.total_net_details / NULLIF(sc.sales_aliquot, 0))::numeric, 2) AS monto_usd,
        COALESCE(iu.total_unidades, 0) AS unidades
    FROM public.sales_operation s
    JOIN public.sales_operation_coins sc 
        ON s.correlative = sc.main_correlative 
       AND sc.coin_code = '02' -- Moneda Dólar
    LEFT JOIN invoice_units iu 
        ON s.correlative = iu.main_correlative
    JOIN public.sellers sel 
        ON s.seller = sel.code
    WHERE s.user_code = 'ALMAYOR' 
      AND s.operation_type = 'BILL' 
      AND s.client_name <> 'ANULADO'
      AND sel.code IN (
          '25625528',  -- ABRAHAM MUÑOZ
          '25411189',  -- ALEXANDER MUJICA
          '23225823',  -- ANDREINA PERDOMO
          '22974980',  -- ANTHONY LARA
          '281502778', -- DESIREE RANGEL
          '24057112',  -- KIRVIN RAMIREZ
          '28386523'   -- SCARLET GONZALEZ
      )
),
ranked_sales AS (
    -- Identificar el último vendedor que le vendió dentro del grupo seleccionado
    SELECT 
        sb.*,
        ROW_NUMBER() OVER (
            PARTITION BY sb.rif 
            ORDER BY sb.fecha DESC, sb.hora DESC, sb.correlative DESC
        ) AS rn_ultimo
    FROM sales_base sb
),
client_sales_summary AS (
    -- Consolidación de unidades, montos y facturas por cliente
    SELECT 
        rif,
        COUNT(DISTINCT factura) AS total_facturas,
        SUM(unidades) AS cantidad_unidades_compradas,
        SUM(monto_usd) AS monto_total_dolares,
        SUM(monto_bs) AS monto_total_bs,
        MIN(fecha) AS primera_compra,
        MAX(fecha) AS ultima_compra
    FROM sales_base
    GROUP BY rif
),
ultimo_vendedor AS (
    SELECT 
        rif,
        vendedor AS vendedor_que_le_vendio
    FROM ranked_sales
    WHERE rn_ultimo = 1
)
SELECT 
    css.rif AS "RIF / Código",
    COALESCE(NULLIF(TRIM(c.description), ''), css.rif) AS "Cliente",
    COALESCE(NULLIF(TRIM(p.description), ''), 'NO REGISTRADO') AS "Provincia / Estado",
    uv.vendedor_que_le_vendio AS "Persona que le Vendió",
    css.cantidad_unidades_compradas AS "Cantidad Total Unidades Compradas",
    css.monto_total_dolares AS "Monto Total en Dólares ($)",
    css.monto_total_bs AS "Monto Total en Bs.",
    css.total_facturas AS "Total Facturas",
    css.primera_compra AS "Primera Compra",
    css.ultima_compra AS "Última Compra",
    c.phone AS "Teléfono"
FROM client_sales_summary css
LEFT JOIN public.clients c 
    ON css.rif = c.code
LEFT JOIN public.provinces p 
    ON c.province = p.code
LEFT JOIN ultimo_vendedor uv 
    ON css.rif = uv.rif
ORDER BY css.monto_total_dolares DESC;



-- ============================================================================
-- CONSULTA 2: DETALLE FACTURA POR FACTURA (CON TASA DEL DÍA)
-- ============================================================================
/*
WITH invoice_units AS (
    SELECT 
        main_correlative,
        SUM(amount) AS total_unidades
    FROM public.sales_operation_details
    GROUP BY main_correlative
)
SELECT 
    s.document_no AS "Nro Factura",
    s.emission_date AS "Fecha de Venta",
    s.register_hour AS "Hora",
    s.client_code AS "RIF / Código",
    COALESCE(NULLIF(TRIM(c.description), ''), s.client_name, s.client_code) AS "Cliente",
    sel.description AS "Persona que le Vendió",
    COALESCE(NULLIF(TRIM(p.description), ''), 'NO REGISTRADO') AS "Provincia / Estado",
    COALESCE(iu.total_unidades, 0) AS "Cantidad Unidades",
    sc.sales_aliquot AS "Tasa del Día (Bs/$)",
    s.total_net_details AS "Monto Factura (Bs.)",
    ROUND((s.total_net_details / NULLIF(sc.sales_aliquot, 0))::numeric, 2) AS "Monto Total en Dólares ($)"
FROM public.sales_operation s
JOIN public.sales_operation_coins sc 
    ON s.correlative = sc.main_correlative 
   AND sc.coin_code = '02'
LEFT JOIN invoice_units iu 
    ON s.correlative = iu.main_correlative
LEFT JOIN public.clients c 
    ON s.client_code = c.code
LEFT JOIN public.provinces p 
    ON c.province = p.code
JOIN public.sellers sel 
    ON s.seller = sel.code
WHERE s.user_code = 'ALMAYOR' 
  AND s.operation_type = 'BILL' 
  AND s.client_name <> 'ANULADO'
  AND sel.code IN (
      '25625528',  -- ABRAHAM MUÑOZ
      '25411189',  -- ALEXANDER MUJICA
      '23225823',  -- ANDREINA PERDOMO
      '22974980',  -- ANTHONY LARA
      '281502778', -- DESIREE RANGEL
      '24057112',  -- KIRVIN RAMIREZ
      '28386523'   -- SCARLET GONZALEZ
  )
ORDER BY s.emission_date DESC, s.register_hour DESC;
*/
