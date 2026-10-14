@echo off
echo ========================================
echo EJECUTANDO SCRIPTS CON UV
echo ========================================

echo.
echo Ejecutando los productos solicitados por Jorge Salazar...
cd C:\Users\POWERBI\Desktop\Entornos\clientes_asoc
uv run python productos_solicitados.py
if errorlevel 1 (
    echo ❌ Error en Script
    pause
    exit /b 1
)
echo Productos solicitados por Jorge Salazar procesado

echo.
echo Ejecutando los productos solicitados por Hector Aular...
cd C:\Users\POWERBI\Desktop\Entornos\clientes_asoc
uv run python productos_solicitados.py
if errorlevel 1 (
    echo ❌ Error en Script
    pause
    exit /b 1
)
echo Productos solicitados por Hector Aular procesado

echo.
echo ========================================
echo TODOS LOS ENTORNOS VIRTUALES (UV) COMPLETADOS
echo ========================================
pause