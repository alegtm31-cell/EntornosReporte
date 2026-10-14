-- Resultados, equipos por tienda
SELECT
TRIM(
 REGEXP_REPLACE(
  st.description,'[[:cntrl:]]', '', 'g'
 )
) AS tienda,
so.emission_date AS fecha,
SUM(sd.amount) AS equipos_vendidos
FROM sales_operation so
INNER JOIN sales_operation_details sd
ON so.correlative = sd.main_correlative
INNER JOIN store st
ON so.store = st.code
INNER JOIN products p
ON sd.code_product = p.code
INNER JOIN department d
ON p.department = d.code
WHERE
so.operation_type = 'BILL'
AND so.emission_date BETWEEN '2026-09-05' AND CURRENT_DATE - INTERVAL '1 day'
AND st.description ~ '^TIENDA'
AND (
    d.father_department IN ('004', '005', '006')
    OR d.code IN ('003', '004', '005', '01', '021', '04', '041', '042', '043', '044')
)
GROUP BY
so.emission_date, st.description
----------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------
-- Resultados, accesorios por tienda
SELECT
TRIM(
 REGEXP_REPLACE(
  st.description,'[[:cntrl:]]', '', 'g'
 )
) AS tienda,
so.emission_date AS fecha,
SUM(sd.amount) AS equipos_vendidos
FROM sales_operation so
INNER JOIN sales_operation_details sd
ON so.correlative = sd.main_correlative
INNER JOIN store st
ON so.store = st.code
INNER JOIN products p
ON sd.code_product = p.code
INNER JOIN department d
ON p.department = d.code
WHERE
so.operation_type = 'BILL'
AND so.emission_date BETWEEN '2026-09-05' AND CURRENT_DATE - INTERVAL '1 day'
AND st.description ~ '^TIENDA'
AND (
d.father_department IN ('02', '05', '08', '11', '12')
    OR d.code IN ('02', '03', '031', '05', '050', '06', '08', '09', '10', '11', '12')
)
GROUP BY
so.emission_date, st.description
----------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------
-- Resultados, equipos por asesor
SELECT
so.emission_date AS fecha,
TRIM(
 REGEXP_REPLACE(
    sl.description,'[[:cntrl:]]', '', 'g'
 )
) AS asesor,
TRIM(
 REGEXP_REPLACE(
    st.description,'[[:cntrl:]]', '', 'g'
 )
) AS tienda,
SUM(sd.amount) AS equipos_vendidos
FROM sales_operation so
INNER JOIN sales_operation_details sd
ON so.correlative = sd.main_correlative
INNER JOIN sellers sl
ON so.seller = sl.code
INNER JOIN products p
ON sd.code_product = p.code
INNER JOIN department d
ON p.department = d.code
INNER JOIN store st
ON so.store = st.code
WHERE
so.operation_type = 'BILL'
AND so.emission_date BETWEEN '2026-09-05' AND CURRENT_DATE - INTERVAL '1 day'
AND st.description ~ '^TIENDA'
AND (
    d.father_department IN ('004', '005', '006')
    OR d.code IN ('003', '004', '005', '01', '021', '04', '041', '042', '043', '044')
)
GROUP BY
so.emission_date, sl.description, st.description
----------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------
-- Resultados, accesorios por asesor
SELECT
so.emission_date AS fecha,
TRIM(
 REGEXP_REPLACE(
    sl.description,'[[:cntrl:]]', '', 'g'
 )
) AS asesor,
TRIM(
 REGEXP_REPLACE(
    st.description,'[[:cntrl:]]', '', 'g'
 )
) AS tienda,
SUM(sd.amount) AS equipos_vendidos
FROM sales_operation so
INNER JOIN sales_operation_details sd
ON so.correlative = sd.main_correlative
INNER JOIN sellers sl
ON so.seller = sl.code
INNER JOIN products p
ON sd.code_product = p.code
INNER JOIN department d
ON p.department = d.code
INNER JOIN store st
ON so.store = st.code
WHERE
so.operation_type = 'BILL'
AND so.emission_date BETWEEN '2026-09-05' AND CURRENT_DATE - INTERVAL '1 day'
AND st.description ~ '^TIENDA'
AND (
    d.father_department IN ('02', '05', '08', '11', '12')
    OR d.code IN ('02', '03', '031', '05', '050', '06', '08', '09', '10', '11', '12')
)
GROUP BY
so.emission_date, sl.description, st.description