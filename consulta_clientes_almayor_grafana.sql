-- ============================================================================
-- CONSULTA: CLIENTES AL MAYOR - PRINCIPAL (GRAFANA)
-- Base de datos: PostgreSQL
-- Variables Grafana:
--   $vendedor -> filtra por vendedor (multi-valor, Include All = "All")
--   $estado   -> filtra por provincia/estado (multi-valor, Include All = "All")
--   $__timeFilter(s.emission_date) -> rango de fechas del panel
--
-- CONFIGURACION DE VARIABLES EN GRAFANA:
--   Variable "$vendedor":
--     Query        : SELECT TRIM(description) FROM public.sellers
--                    WHERE code IN ('25625528','25411189','23225823',
--                                   '22974980','281502778','24057112',
--                                   '28386523')
--                    ORDER BY description
--     Include All  : SI  |  Custom all value: All  |  Multi-value: SI
--
--   Variable "$estado":
--     Query        : SELECT TRIM(description) FROM public.provinces
--                    WHERE description IS NOT NULL AND TRIM(description) <> ''
--                    ORDER BY description
--     Include All  : SI  |  Custom all value: All  |  Multi-value: SI
-- ============================================================================

WITH invoice_units AS (
    -- Total de unidades vendidas por factura
    SELECT 
        main_correlative,
        SUM(amount) AS total_unidades
    FROM public.sales_operation_details
    GROUP BY main_correlative
),
primera_compra_empresa AS (
    -- Primera factura historica de cada cliente en toda la empresa
    SELECT 
        client_code AS rif,
        MIN(emission_date) AS primera_compra_historica
    FROM public.sales_operation
    WHERE operation_type = 'BILL'
      AND client_name <> 'ANULADO'
      AND user_code = 'ALMAYOR'
    GROUP BY client_code
),
sales_base AS (
    -- Facturas del periodo analizado con los vendedores seleccionados
    SELECT 
        s.correlative,
        s.document_no                                                           AS factura,
        s.emission_date                                                         AS fecha,
        s.register_hour                                                         AS hora,
        s.client_code                                                           AS rif,
        s.client_name,
        s.seller                                                                AS seller_code,
        TRIM(sel.description)                                                   AS vendedor,
        s.total_net_details                                                     AS monto_bs,
        sc.sales_aliquot                                                        AS tasa_del_dia,
        ROUND((s.total_net_details / NULLIF(sc.sales_aliquot, 0))::numeric, 2) AS monto_usd,
        COALESCE(iu.total_unidades, 0)                                          AS unidades
    FROM public.sales_operation s
    JOIN public.sales_operation_coins sc 
        ON s.correlative = sc.main_correlative 
       AND sc.coin_code = '02'                    -- Tasa Dolar
    LEFT JOIN invoice_units iu 
        ON s.correlative = iu.main_correlative
    JOIN public.sellers sel 
        ON s.seller = sel.code
    WHERE s.user_code      = 'ALMAYOR'
      AND s.operation_type = 'BILL'
      AND s.client_name   <> 'ANULADO'
      AND $__timeFilter(s.emission_date)           -- << Rango de fechas Grafana
      AND sel.code IN (
          '25625528',   -- ABRAHAM MUNOZ
          '25411189',   -- ALEXANDER MUJICA
          '23225823',   -- ANDREINA PERDOMO
          '22974980',   -- ANTHONY LARA
          '281502778',  -- DESIREE RANGEL
          '24057112',   -- KIRVIN RAMIREZ
          '28386523'    -- SCARLET GONZALEZ
      )
      -- ---------------------------------------------------------------
      -- FILTRO DINAMICO: $vendedor
      -- '$vendedor' devuelve 'All' cuando se selecciona todo
      -- ---------------------------------------------------------------
      AND (
          '$vendedor' = 'All'
          OR TRIM(sel.description) IN (${vendedor:sqlstring})
      )
),
ranked_sales AS (
    -- Asigna la persona que le vendio mas recientemente dentro del periodo
    SELECT 
        sb.*,
        ROW_NUMBER() OVER (
            PARTITION BY sb.rif 
            ORDER BY sb.fecha DESC, sb.hora DESC, sb.correlative DESC
        ) AS rn_ultimo
    FROM sales_base sb
),
client_sales_summary AS (
    -- Consolidacion de unidades, montos y compras por cliente en el periodo
    SELECT 
        rif,
        COUNT(DISTINCT factura)     AS total_facturas,
        SUM(unidades)               AS cantidad_unidades_compradas,
        SUM(monto_usd)              AS monto_total_dolares,
        SUM(monto_bs)               AS monto_total_bs,
        MIN(fecha)                  AS primera_compra_periodo,
        MAX(fecha)                  AS ultima_compra
    FROM sales_base
    GROUP BY rif
),
ultimo_vendedor AS (
    -- Vendedor que le vendio por ultima vez en el periodo
    SELECT 
        rif,
        vendedor AS vendedor_que_le_vendio
    FROM ranked_sales
    WHERE rn_ultimo = 1
)
SELECT 
    css.rif                                                                     AS "RIF / Codigo",
    COALESCE(NULLIF(TRIM(c.description), ''), css.rif)                          AS "Cliente",
    COALESCE(NULLIF(TRIM(p.description), ''), 'NO REGISTRADO')                  AS "Provincia / Estado",
    uv.vendedor_que_le_vendio                                                   AS "Persona que le Vendio",
    -- Clasificacion segun historial en la empresa
    CASE 
        WHEN pce.primera_compra_historica >= date_trunc('month', $__timeFrom()::timestamp)
        THEN 'NUEVO'
        ELSE 'RECURRENTE'
    END                                                                         AS "Tipo de Cliente",
    pce.primera_compra_historica                                                AS "Primera Compra Empresa",
    css.primera_compra_periodo                                                  AS "Primera Compra Periodo",
    css.ultima_compra                                                           AS "Ultima Compra",
    css.total_facturas                                                          AS "Total Facturas",
    css.cantidad_unidades_compradas                                             AS "Cantidad Total Unidades Compradas",
    css.monto_total_dolares                                                     AS "Monto Total en Dolares ($)",
    css.monto_total_bs                                                          AS "Monto Total en Bs.",
    COALESCE(NULLIF(TRIM(c.phone), ''), 'SIN TELEFONO')                         AS "Telefono"
FROM client_sales_summary css
LEFT JOIN primera_compra_empresa pce ON pce.rif  = css.rif
LEFT JOIN public.clients         c   ON c.code   = css.rif
LEFT JOIN public.provinces       p   ON p.code   = c.province
LEFT JOIN ultimo_vendedor        uv  ON uv.rif   = css.rif
WHERE
    -- ---------------------------------------------------------------
    -- FILTRO DINAMICO: $estado (provincia)
    -- '$estado' devuelve 'All' cuando se selecciona todo
    -- ---------------------------------------------------------------
    (
        '$estado' = 'All'
        OR TRIM(p.description) IN (${estado:sqlstring})
    )
ORDER BY css.monto_total_dolares DESC;


