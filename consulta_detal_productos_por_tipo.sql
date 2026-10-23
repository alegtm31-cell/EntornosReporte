-- ============================================================================
-- CONSULTA 1: CANTIDAD TOTAL DE PRODUCTOS AL DETAL POR TIPO (GLOBAL)
-- Tipos: ACCESORIOS | LAPTOPS | TELEFONOS | TELEVISORES
-- Rango:  01/01/2024 -> Fecha actual
-- ============================================================================
-- Clasificacion de departamentos:
--   TELEFONOS   -> dept: 01
--   LAPTOPS     -> dept: 003
--   TELEVISORES -> dept: 043
--   ACCESORIOS  -> dept: 02, 05, 06, 11, 12, 13
-- ============================================================================

SELECT
    CASE
        WHEN p.department = '01'                                   THEN 'TELEFONOS'
        WHEN p.department = '003'                                  THEN 'LAPTOPS'
        WHEN p.department = '043'                                  THEN 'TELEVISORES'
        WHEN p.department IN ('02', '05', '06', '11', '12', '13') THEN 'ACCESORIOS'
        ELSE NULL
    END                          AS "Tipo de Producto",
    SUM(sd.amount)               AS "Total Unidades Vendidas"
FROM public.sales_operation so
JOIN public.sales_operation_details sd
    ON sd.main_correlative = so.correlative
JOIN public.products p
    ON p.code = sd.code_product
WHERE
    so.user_code     <> 'ALMAYOR'
    AND so.operation_type = 'BILL'
    AND so.client_name    <> 'ANULADO'
    AND so.emission_date BETWEEN '2024-01-01' AND CURRENT_DATE
    AND p.department IN (
        '01', '003', '043',
        '02', '05', '06', '11', '12', '13'
    )
GROUP BY
    CASE
        WHEN p.department = '01'                                   THEN 'TELEFONOS'
        WHEN p.department = '003'                                  THEN 'LAPTOPS'
        WHEN p.department = '043'                                  THEN 'TELEVISORES'
        WHEN p.department IN ('02', '05', '06', '11', '12', '13') THEN 'ACCESORIOS'
        ELSE NULL
    END
ORDER BY
    "Total Unidades Vendidas" DESC;


-- ============================================================================
-- CONSULTA 2: CANTIDAD TOTAL DE PRODUCTOS AL DETAL POR TIPO Y POR TIENDA
-- Tipos: ACCESORIOS | LAPTOPS | TELEFONOS | TELEVISORES
-- Rango:  01/01/2024 -> Fecha actual
-- Detalle: Desglosado por tienda (so.store -> public.store)
-- ============================================================================

SELECT
    TRIM(REGEXP_REPLACE(st.description, '[[:cntrl:]]', '', 'g'))
                                 AS "Tienda",
    CASE
        WHEN p.department = '01'                                   THEN 'TELEFONOS'
        WHEN p.department = '003'                                  THEN 'LAPTOPS'
        WHEN p.department = '043'                                  THEN 'TELEVISORES'
        WHEN p.department IN ('02', '05', '06', '11', '12', '13') THEN 'ACCESORIOS'
    END                          AS "Tipo de Producto",
    SUM(sd.amount)               AS "Total Unidades Vendidas"
FROM public.sales_operation so
JOIN public.sales_operation_details sd
    ON sd.main_correlative = so.correlative
JOIN public.store st
    ON so.store = st.code
JOIN public.products p
    ON p.code = sd.code_product
WHERE
    so.user_code     <> 'ALMAYOR'         -- Solo ventas AL DETAL
    AND so.operation_type = 'BILL'        -- Solo facturas
    AND so.client_name    <> 'ANULADO'    -- Excluye anuladas
    AND so.emission_date BETWEEN '2024-01-01' AND CURRENT_DATE
    AND st.description ~ '^TIENDA'        -- Solo tiendas (excluye deposito u otros)
    AND p.department IN (
        '01', '003', '043',
        '02', '05', '06', '11', '12', '13'
    )
GROUP BY
    TRIM(REGEXP_REPLACE(st.description, '[[:cntrl:]]', '', 'g')),
    CASE
        WHEN p.department = '01'                                   THEN 'TELEFONOS'
        WHEN p.department = '003'                                  THEN 'LAPTOPS'
        WHEN p.department = '043'                                  THEN 'TELEVISORES'
        WHEN p.department IN ('02', '05', '06', '11', '12', '13') THEN 'ACCESORIOS'
    END
ORDER BY
    "Tienda",
    "Total Unidades Vendidas" DESC;


-- ============================================================================
-- CONSULTA 3: CANTIDAD TOTAL DE PRODUCTOS AL DETAL POR TIPO, AÑO Y MES
-- Tipos: ACCESORIOS | LAPTOPS | TELEFONOS | TELEVISORES
-- Rango:  01/01/2024 -> Fecha actual
-- Detalle: Desglosado por año y mes (cronologico)
-- ============================================================================

SELECT
    EXTRACT(YEAR  FROM so.emission_date)::INT    AS "Año",
    EXTRACT(MONTH FROM so.emission_date)::INT    AS "Mes (Nro)",
    TO_CHAR(so.emission_date, 'TMMonth')         AS "Mes",
    CASE
        WHEN p.department = '01'                                   THEN 'TELEFONOS'
        WHEN p.department = '003'                                  THEN 'LAPTOPS'
        WHEN p.department = '043'                                  THEN 'TELEVISORES'
        WHEN p.department IN ('02', '05', '06', '11', '12', '13') THEN 'ACCESORIOS'
    END                                          AS "Tipo de Producto",
    SUM(sd.amount)                               AS "Total Unidades Vendidas"
FROM public.sales_operation so
JOIN public.sales_operation_details sd
    ON sd.main_correlative = so.correlative
JOIN public.products p
    ON p.code = sd.code_product
WHERE
    so.user_code      <> 'ALMAYOR'
    AND so.operation_type  = 'BILL'
    AND so.client_name     <> 'ANULADO'
    AND so.emission_date BETWEEN '2024-01-01' AND CURRENT_DATE
    AND p.department IN (
        '01', '003', '043',
        '02', '05', '06', '11', '12', '13'
    )
GROUP BY
    EXTRACT(YEAR  FROM so.emission_date),
    EXTRACT(MONTH FROM so.emission_date),
    TO_CHAR(so.emission_date, 'TMMonth'),
    CASE
        WHEN p.department = '01'                                   THEN 'TELEFONOS'
        WHEN p.department = '003'                                  THEN 'LAPTOPS'
        WHEN p.department = '043'                                  THEN 'TELEVISORES'
        WHEN p.department IN ('02', '05', '06', '11', '12', '13') THEN 'ACCESORIOS'
    END
ORDER BY
    "Año",
    "Mes (Nro)",
    "Total Unidades Vendidas" DESC;
