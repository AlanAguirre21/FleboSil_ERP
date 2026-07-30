# 013 · caja — Plan

## Enfoque

Modelo `MovimientosCaja` de tipo INSERT-only, expuesto mediante un ViewSet que solo permite `list`, `retrieve` y `create` — nunca `update` ni `destroy`, reforzado a nivel de framework (no solo por permisos). Los movimientos automáticos de tipo `venta` ya se generan desde `011 · Ventas`; esta feature construye la interfaz de consulta y la acción de registrar movimientos manuales, exclusiva de admin.

## Implementación

1. Backend — crear modelo `MovimientosCaja` en `backend/apps/caja/models.py`: `tipo_movimiento` (ingreso/retiro), `monto` (Decimal), `motivo`, `referencia_id` (nullable, entero simple), `descripcion`, `usuario_id` (FK), `fecha`, `saldo_resultante` (Decimal).
2. Backend — crear migración del modelo (si `011 · Ventas` ya la generó parcialmente al implementar el movimiento automático de ingreso, verificar y completar en vez de duplicar).
3. Backend — crear `MovimientoCajaSerializer`, de solo lectura para el listado, y con validación específica para la creación manual (monto positivo, tipo válido, descripción obligatoria en movimientos manuales).
4. Backend — crear `MovimientoCajaViewSet` como subclase de `mixins.ListModelMixin`, `mixins.RetrieveModelMixin`, `mixins.CreateModelMixin` (sin `UpdateModelMixin` ni `DestroyModelMixin`) — refuerza a nivel de framework que edición/eliminación no existen como rutas.
5. Backend — en el método `create()`: si `tipo_movimiento = retiro`, dentro de `transaction.atomic()` con `select_for_update()` sobre el último registro (para evitar condición de carrera con otro movimiento simultáneo), calcular el saldo resultante propuesto; si sería negativo, rechazar con error claro antes de guardar.
6. Backend — calcular `saldo_resultante` como `saldo_anterior + monto` (si ingreso) o `saldo_anterior - monto` (si retiro), y guardarlo en el registro nuevo.
7. Backend — restringir el permiso de esta vista completa (incluida lectura) a rol admin únicamente, distinto del criterio abierto usado en Ventas/Compras.
8. Backend — registrar rutas de `MovimientosCaja` en el router principal.
9. Frontend — crear `frontend/src/api/caja.js` con funciones de listado (con filtros) y creación de movimiento manual.
10. Frontend — crear `frontend/src/hooks/useMovimientosCaja.js` con React Query.
11. Frontend — crear `frontend/src/pages/Caja/Caja.jsx`: saldo actual destacado en la parte superior, tabla de movimientos filtrable por fecha/tipo/motivo, botón "Registrar ingreso/retiro" que abre un formulario en `Modal`.
12. Frontend — el formulario de movimiento manual muestra error si el backend rechaza el retiro por saldo insuficiente, sin permitir reintentar con el mismo monto sin corregirlo.
13. Frontend — ocultar/bloquear el módulo completo de Caja en el sidebar y en el enrutador si `rol !== 'admin'` (ya definido como patrón desde `001 · Header`).
14. Frontend — agregar la ruta `/caja` en `App.jsx`, protegida exclusivamente para admin.

## Decisiones

- **`MovimientoCajaViewSet` sin `UpdateModelMixin` ni `DestroyModelMixin`, en vez de bloquear solo por permisos** — refuerza a nivel de framework (no solo de lógica de autorización) que estas rutas HTTP ni siquiera existen, consistente con el mismo criterio ya aplicado al diseño de `MovimientosInventario` como tabla de auditoría.
- **Validación de saldo negativo con `select_for_update()` sobre el último movimiento** — sin este bloqueo, dos retiros simultáneos podrían leer el mismo saldo "seguro" antes de que ninguno se aplique, permitiendo que ambos pasen la validación y dejen el saldo real en negativo; se aplica el mismo estándar de concurrencia ya usado en Ventas/Compras/Producción.
- **Caja restringida a admin en su totalidad (lectura y escritura), a diferencia de Ventas/Compras/Producción/Inventario que son de consulta abierta** — consistente con la spec general del proyecto, que ya define Caja como visible únicamente para rol admin.
- **`saldo_resultante` guardado en cada fila, no recalculado en cada consulta** — mismo patrón ya justificado en el diseño de datos original: consulta instantánea del saldo actual, y permite detectar inconsistencias si algún saldo posterior no cuadra.

## Riesgos

- **Bloqueo estricto de saldo negativo podría impedir un retiro legítimo si el admin sabe que hay efectivo físico disponible pero el sistema no refleja todos los ingresos aún capturados** — mitigación: este es un riesgo operativo aceptado por la decisión ya tomada; se documenta como comportamiento intencional, no como bug, y el admin deberá registrar cualquier ingreso pendiente antes de intentar el retiro.
- **Condición de carrera entre un movimiento automático de venta y un retiro manual simultáneo, si ambos leen el saldo antes de que el otro se confirme** — mitigación: el `select_for_update()` sobre el último movimiento cubre este caso siempre que ambas rutas de creación (automática desde Ventas, manual desde Caja) pasen por la misma lógica de bloqueo, no una lógica duplicada; verificar que ambas reutilicen una única función/servicio de creación de movimiento, no dos implementaciones distintas.
- **Migración duplicada del modelo `MovimientosCaja` si ya se creó parcialmente en `011 · Ventas`** — mitigación: verificar el estado real de la migración antes de generar una nueva, para no crear conflictos de migración en Django.