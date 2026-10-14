@echo off
echo ========================================
echo EJECUTANDO SCRIPTS CON UV
echo ========================================

echo.
echo Ejecutando la extraccion y transformacion de la base de datos...
cd C:\Users\POWERBI\Desktop\Entornos\etl_db
uv run python etl_db.py
if errorlevel 1 (
    echo ❌ Error en Script
    pause
    exit /b 1
)
echo ETL de la base de datos procesado

echo.
echo Ejecutando las transformaciones para las estadisticas de cashea...
cd C:\Users\POWERBI\Desktop\Entornos\cashea_stats
uv run python cashea_stats.py
if errorlevel 1 (
    echo ❌ Error en Script
    pause
    exit /b 1
)
echo Fuentes de las estadisticas de Cashea procesadas

echo.
echo Ejecutando las transformaciones para las estadisticas de Zoom...
cd C:\Users\POWERBI\Desktop\Entornos\sending_zoom
uv run python sending_zoom.py
if errorlevel 1 (
    echo ❌ Error en Script
    pause
    exit /b 1
)
echo Fuentes de las estadisticas de Zoom procesadas

echo.
echo Ejecutando las transformaciones para las estadisticas de las ventas al detal y al mayor...
cd C:\Users\POWERBI\Desktop\Entornos\kpi_monthly
uv run python kpi_monthly.py
if errorlevel 1 (
    echo ❌ Error en Script
    pause
    exit /b 1
)
echo Fuentes de las estadisticas de ventas al detal y al mayor procesadas

echo.
echo Ejecutando las transformaciones para las estadisticas al mayor...
cd C:\Users\POWERBI\Desktop\Entornos\almayor_stats
uv run python almayor_stats.py
if errorlevel 1 (
    echo ❌ Error en Script
    pause
    exit /b 1
)
echo Fuentes de las estadisticas de ventas al detal y al mayor procesadas

echo.
echo ========================================
echo TODOS LOS ENTORNOS VIRTUALES (UV) COMPLETADOS
echo ========================================
pause