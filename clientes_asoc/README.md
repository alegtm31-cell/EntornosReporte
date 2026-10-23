# 📦 Clientes Asociados y Despacho de Productos

Módulo de control de inventario, pedidos y logística de envíos para la red de clientes asociados comerciales.

---

## 🎯 Componentes

1. **Dashboard Power BI (`haular/Envio de productos.pbix`)**:
   * Visualización del pipeline de despacho y entregas por cliente.
   * Monitoreo de tiempos de ciclo entre facturación y recepción física de mercancía.
   * Cumplimiento de pedidos y volumen de bultos transportados.
2. **Script de Procesamiento (`productos_solicitados.py`)**:
   * Cruza las órdenes de compra con la disponibilidad de inventario y genera tablas de seguimiento para las distintas rutas de distribución.
