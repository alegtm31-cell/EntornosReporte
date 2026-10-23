-- ============================================================================
-- CONSULTA: CLIENTES AL MAYOR INACTIVOS
-- Base de datos: PostgreSQL
-- Definicion de inactivo: sin compras en los ultimos 60 dias (2 meses)
-- Incluye: cliente, telefono cliente, ultima compra, dias sin comprar,
--          vendedor responsable y su telefono, provincia
-- NOTA: Se captura el ultimo vendedor que le facturo al cliente,
--       sin importar si pertenece al grupo asignado o no.
-- ============================================================================

WITH ultima_compra AS (
    -- Ultima fecha de compra de cada cliente al mayor (sin facturas anuladas)
    SELECT
        client_code                 AS rif,
        MAX(emission_date)          AS ultima_compra
    FROM public.sales_operation
    WHERE user_code      = 'ALMAYOR'
      AND operation_type = 'BILL'
      AND client_name   <> 'ANULADO'
    GROUP BY client_code
),
ultimo_vendedor AS (
    -- Ultimo vendedor (cualquiera) que le facturo al cliente al mayor
    -- Sin filtrar por grupo, para que no quede NULL
    SELECT DISTINCT ON (s.client_code)
        s.client_code               AS rif,
        sel.code                    AS seller_code,
        TRIM(sel.description)       AS vendedor
    FROM public.sales_operation s
    JOIN public.sellers sel ON sel.code = s.seller
    WHERE s.user_code      = 'ALMAYOR'
      AND s.operation_type = 'BILL'
      AND s.client_name   <> 'ANULADO'
    ORDER BY s.client_code, s.emission_date DESC, s.register_hour DESC
)
SELECT
    uc.rif                                                          AS "RIF / Codigo",
    COALESCE(NULLIF(TRIM(c.description), ''), uc.rif)               AS "Cliente",
    COALESCE(NULLIF(TRIM(c.phone), ''), 'SIN TELEFONO')             AS "Telefono Cliente",
    uc.ultima_compra                                                AS "Ultima Compra",
    (CURRENT_DATE - uc.ultima_compra::date)                         AS "Dias Sin Comprar",
    COALESCE(uv.vendedor, 'SIN VENDEDOR ASIGNADO')                  AS "Vendedor",
    COALESCE(NULLIF(TRIM(p.description), ''), 'NO REGISTRADO')      AS "Provincia"
FROM ultima_compra uc
LEFT JOIN public.clients   c  ON c.code       = uc.rif
LEFT JOIN ultimo_vendedor  uv ON uv.rif       = uc.rif
LEFT JOIN public.provinces p  ON p.code       = c.province
WHERE uc.ultima_compra < CURRENT_DATE - INTERVAL '60 days'
ORDER BY uc.ultima_compra ASC;

