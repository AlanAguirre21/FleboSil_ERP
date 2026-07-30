# 012 · produccion — Plan

## Enfoque

Tres modelos: `Receta` (configuración, CRUD restringido a admin), `Produccion` (cabecera del registro operativo) y `DetalleProduccion` (líneas, snapshot de materia prima consumida — mismo patrón cabecera-detalle que Compras/Ventas, aquí aplicado a un evento de consumo en vez de una transacción comercial). La creación de `Produccion` ejecuta una transacción con múltiples `select_for_update()` antes de confirmar, igual que en Compras y Ventas.

## Implementación

1. Backend — crear modelo `Receta`: `producto_id` (FK), `materia_prima_id` (FK), `cantidad_requerida` (Decimal), `activo`.
2. Backend — crear modelo `Produccion` (cabecera): `sucursal_id` (FK), `producto_id` (FK), `cantidad_producida` (Decimal), `fecha`, `usuario_id` (FK), `costo_total` (Decimal).
3. Backend — crear modelo `DetalleProduccion` (líneas): `produccion_id` (FK), `materia_prima_id` (FK), `cantidad_consumida` (Decimal), `costo_unitario_momento` (Decimal — el `costo_promedio` de esa materia prima al momento de producir), `subtotal` (Decimal).
4. Backend — crear migraciones de los tres modelos.
5. Backend — crear `RecetaSerializer`/`RecetaViewSet`, reutilizando el permiso "solo admin escribe".
6. Backend — crear `ProduccionSerializer`/`ProduccionViewSet`, con `create` y solo lectura (sin `update`/`destroy`).
7. Backend — en el método `create()` de `Produccion`: consultar `Receta` activa del producto; si no existe, rechazar con mensaje claro. Calcular cantidad necesaria de cada materia prima.
8. Backend — dentro de `transaction.atomic()`, ordenando las materias primas por `id` antes de bloquearlas: `select_for_update()` sobre `InventarioSucursalMateriaPrima` de cada una, validar stock suficiente de todas antes de modificar cualquiera (todo o nada); si es viable, descontar cada una, crear su `MovimientoInventario` de salida, y crear el `DetalleProduccion` correspondiente con `costo_unitario_momento` tomado de `MateriaPrima.costo_promedio` en ese instante.
9. Backend — sumar los `subtotal` de todos los `DetalleProduccion` para obtener `costo_total`; crear/actualizar `InventarioSucursalProducto` sumando `cantidad_producida`; crear el `MovimientoInventario` de entrada del producto — todos con el mismo `referencia_id`.
10. Backend — registrar rutas de `Receta` y `Produccion` en el router principal.
11. Frontend — crear `frontend/src/api/produccion.js` con funciones CRUD de recetas y listado/creación de producciones.
12. Frontend — crear `frontend/src/hooks/useRecetas.js` y `useProducciones.js`, invalidando cache de `useInventario` tras confirmar una producción.
13. Frontend — crear `frontend/src/pages/Produccion/Produccion.jsx`: selector entre "Producciones registradas" y "Gestión de recetas".
14. Frontend — sección de recetas: tabla de productos con su receta, formulario para agregar/editar líneas de materia prima requerida (solo admin).
15. Frontend — sección de producciones: formulario de nueva producción, mostrando en vivo la materia prima que se va a consumir según receta vigente y si hay stock suficiente.
16. Frontend — vista de detalle de producción, mostrando el desglose de `DetalleProduccion` (materia prima consumida, cantidad, costo al momento).
17. Frontend — agregar la ruta `/produccion` en `App.jsx`.

## Decisiones

- **`DetalleProduccion` como snapshot de la receta al momento de producir, no una referencia viva a `Receta`** — mismo principio ya aplicado en `DetalleVenta`/`DetalleCompra`: el historial no debe cambiar si la configuración (receta, precios) se actualiza después.
- **Receta restringida a admin, Producción abierta a cualquier autenticado** — mismo criterio que Catálogo vs. Compras/Ventas.
- **Validación de stock "todo o nada" antes de modificar cualquier tabla** — igual que en Ventas.
- **Sin acción de cancelar en esta iteración** — documentado explícitamente como límite, dada la complejidad mayor de revertir múltiples consumos simultáneos.
- **Orden determinístico de bloqueo (`select_for_update()` por `id` ascendente)** — previene deadlocks cuando dos producciones comparten materias primas y podrían intentar bloquearlas en orden distinto.

## Riesgos

- **Deadlocks por bloqueo de múltiples filas en orden inconsistente** — mitigación: ordenar por `id` antes de iterar, ya incorporado en el paso 8.
- **Costo de materia prima desactualizado si Compras no recalcula `costo_promedio` automáticamente** — mitigación: documentado como dependencia cruzada; el `costo_unitario_momento` reflejará el valor vigente, correcto según el diseño actual, pero su precisión depende de que ese campo se mantenga actualizado por fuera de esta feature.
- **Crecimiento de la tabla `DetalleProduccion` si hay recetas con muchas materias primas y producción frecuente** — mitigación aceptable para el volumen esperado de la empresa; revisar índices sobre `produccion_id` si el historial de consultas se vuelve lento.