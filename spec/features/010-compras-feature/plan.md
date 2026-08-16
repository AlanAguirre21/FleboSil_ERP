# 010 · compras — Plan

## Enfoque

Patrón cabecera-detalle ya definido en la arquitectura: modelo `Compra` (cabecera) + `DetalleCompraProducto`/`DetalleCompraMateriaPrima` (líneas, tablas separadas por integridad referencial). La acción de "marcar como recibida" es la operación crítica de esta feature — se implementa como un endpoint dedicado (no un simple `PATCH` de estado) que ejecuta la lógica de actualización de inventario dentro de una transacción atómica con `select_for_update()`.

## Implementación

1. Backend — crear modelo `Compra` en `backend/apps/compras/models.py`: `proveedor_id` (FK), `sucursal_id` (FK), `usuario_id` (FK), `fecha`, `fecha_entrega`, `total` (Decimal), `estado` (pendiente/recibida/cancelada).
2. Backend — crear modelo `DetalleCompraProducto`: `compra_id` (FK), `producto_id` (FK), `cantidad`, `costo_unitario` (Decimal), `subtotal` (Decimal).
3. Backend — crear modelo `DetalleCompraMateriaPrima`: misma estructura, con `materia_prima_id`.
4. Backend — crear migraciones de los tres modelos.
5. Backend — crear serializers anidados: `CompraSerializer` acepta líneas de ambos tipos en la creación, calculando `subtotal` y `total` en el backend (nunca confiar en el total enviado desde el frontend).
6. Backend — crear `CompraViewSet` con acciones estándar (`list`, `retrieve`, `create`) más una acción personalizada `POST /api/compras/{id}/recibir/`.
7. Backend — implementar la acción `recibir()`: dentro de `transaction.atomic()`, para cada línea de la compra, usar `select_for_update()` sobre el registro de `InventarioSucursalProducto`/`MateriaPrima` correspondiente (creándolo si no existe aún para esa combinación sucursal+ítem), sumar la cantidad, y crear el `MovimientoInventario` de tipo `entrada` con `referencia_id` apuntando a la compra.
8. Backend — implementar la acción `cancelar()`: si la compra estaba `pendiente`, solo cambia el estado; si ya estaba `recibida`, genera movimientos de tipo `salida` inversos por cada línea, dentro de la misma transacción atómica, antes de marcar como `cancelada`.
9. Backend — registrar rutas de `Compra` en el router principal, incluyendo las acciones personalizadas.
10. Frontend — crear `frontend/src/api/compras.ts` con funciones de listado, creación, detalle, recibir y cancelar.
11. Frontend — crear `frontend/src/hooks/useCompras.ts` con React Query, incluyendo invalidación de cache de `useInventario` al recibir/cancelar una compra (para que la feature `009` refleje el cambio sin recargar).
12. Frontend — crear `frontend/src/pages/Compras/Compras.tsx`: lista filtrable por proveedor/fecha/estado, reutilizando `Tabla`.
13. Frontend — crear `frontend/src/pages/Compras/NuevaCompra.tsx`: selector de proveedor, selector de sucursal destino, buscador de ítems (producto o materia prima) que agrega líneas dinámicamente, cálculo de total en vivo.
14. Frontend — crear `frontend/src/pages/Compras/DetalleCompra.tsx`: muestra líneas, totales, y botones de acción ("Marcar como recibida", "Cancelar") según el estado actual.
15. Frontend — agregar la ruta `/compras` en `App.tsx`, sin restricción de rol.

## Decisiones

- **Acción dedicada `recibir()` en vez de un `PATCH` genérico de estado** — cambiar el estado a "recibida" no es un cambio de campo simple, dispara efectos secundarios (stock, movimientos) que deben quedar explícitos como una operación de negocio propia, no ocultos dentro de una actualización genérica de recurso.
- **`select_for_update()` al recibir una compra** — aunque el riesgo de condición de carrera es menor en compras que en ventas (menos frecuentes, normalmente una persona a la vez), se aplica el mismo estándar ya definido en el tech-stack para toda operación que modifique stock, sin hacer excepciones por "baja probabilidad".
- **Cancelar una compra ya recibida genera movimiento inverso, nunca edita el original** — aplica el principio de trazabilidad total ya establecido; el historial debe reflejar que hubo una entrada y luego una corrección, no simular que la entrada nunca ocurrió.
- **Total calculado y validado en el backend, ignorando cualquier total enviado desde el frontend** — evita que un cliente malicioso o un bug de frontend registre una compra con un total manipulado que no corresponda a la suma real de sus líneas.
- **Sin restricción de rol para registrar compras** — mismo criterio aplicado a Clientes/Proveedores: es operación diaria, no administrativa.

## Riesgos

- **Crear el registro de `InventarioSucursalProducto`/`MateriaPrima` sobre la marcha si no existe aún para esa combinación sucursal+ítem, dentro de la misma transacción con `select_for_update()`** — riesgo de race condition si dos compras del mismo ítem/sucursal se reciben simultáneamente antes de que exista la fila; mitigación: usar `get_or_create()` con manejo explícito de la excepción de duplicado dentro de la transacción, o aplicar una restricción `unique_together` que el propio `IntegrityError` proteja como respaldo.
- **Cancelar una compra recibida podría dejar el stock en negativo si ya se consumió parte de esa materia prima en una producción posterior** — mitigación: validar antes de cancelar que hay stock suficiente para revertir; si no lo hay, bloquear la cancelación con un mensaje explícito en vez de permitir stock negativo silencioso.
- **El cálculo de total en el frontend podría desincronizarse visualmente del que el backend termina validando, si hay redondeos distintos** — mitigación: usar la misma lógica de redondeo (2 decimales, `Decimal` con `ROUND_HALF_UP`) tanto en frontend como backend, documentada explícitamente para evitar diferencias de centavos entre lo mostrado y lo guardado.