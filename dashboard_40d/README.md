# ⏱️ Dashboard de Clientes Inactivos (+40 Días)

Tablero web enfocado en la **retención y prevención de fuga de clientes (Churn Prevention)**, identificando específicamente a todos los clientes del canal mayorista que llevan más de 40 días consecutivos sin registrar compras en el sistema.

---

## 🎯 Objetivo y Funcionalidades

* **Detección Temprana de Churn**: Alerta sobre clientes en riesgo de abandono para activación de campañas de re-contacto comercial.
* **Filtros por Asesor de Ventas**: Permite a cada vendedor visualizar únicamente su cartera de clientes dormidos para coordinar llamadas o visitas comerciales.
* **Métricas de Impacto**:
  * Total de clientes en inactividad crítica.
  * Histórico de última compra y días exactos sin interacción comercial.
  * Monto histórico facturado y unidades previas.
* **Información de Contacto Inmediata**: Muestra el RIF, razón social, número de teléfono y estado geográfico para agilizar la gestión de reactivación.

---

## 🔌 Conexión con la Base de Datos

1. **Consulta SQL Especializada**:
   Los datos son extraídos mediante la consulta `consulta_clientes_almayor_inactivos.sql` ejecutada sobre la base de datos **PostgreSQL (Saint Enterprise)**:
   ```sql
   -- Identifica la última fecha de factura por cliente y calcula la diferencia de días con la fecha actual
   CURRENT_DATE - MAX(s.emission_date) > 40
   ```
2. **Dataset de Consumo**:
   La consulta genera el archivo `clientes_inactivos_fixed.csv`, el cual es leído automáticamente por el frontend al inicializar la aplicación.

---

## 🚀 Cómo Ejecutar

1. Abre `index.html` en tu navegador.
2. La vista cargará de forma automática el archivo `clientes_inactivos_fixed.csv` ubicado en el mismo directorio.
3. Puedes buscar clientes por nombre o RIF y ordenar por días de inactividad de mayor a menor para priorizar los casos más urgentes.
