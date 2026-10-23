# 📈 Al Mayor Stats

Módulo analítico para la consolidación de estadísticas de ventas al mayor, cálculo de tickets promedio y reporte comercial ejecutivo.

## 🎯 Funcionalidades
* Lee los datasets generados por `etl_db` (`almayor_detail_sales.parquet`, `almayor_sellers.parquet`).
* Genera el informe consolidado en Excel (`reports/almayor.xlsx`) con métricas por vendedor, cliente y producto.

## 🚀 Ejecución
```bash
uv run python almayor_stats.py
```
