# 009 · Inventario — Tareas

- [ ] Crear modelo `InventarioSucursalProducto` con `unique_together` y su migración.
- [ ] Crear modelo `InventarioSucursalMateriaPrima` con `unique_together` y su migración.
- [ ] Crear modelo `MovimientosInventario` con índices sobre `sucursal_id`, `item_id`, `fecha`, y su migración.
- [ ] Crear serializers de solo lectura para los tres modelos.
- [ ] Crear `ReadOnlyModelViewSet` de `InventarioSucursalProducto`/`MateriaPrima`, con filtro por sucursal.
- [ ] Crear `ReadOnlyModelViewSet` de `MovimientosInventario`, con filtros por ítem, sucursal y tipo de movimiento.
- [ ] Verificar si el endpoint de alertas de `001 · Header` ya cubre esta necesidad; reutilizarlo o adaptarlo, no duplicar.
- [ ] Registrar rutas de los tres recursos en el router principal.
- [ ] Crear `frontend/src/api/inventario.ts` con funciones de consulta.
- [ ] Crear hooks `useInventario.ts` y `useMovimientosInventario.ts`.
- [ ] Crear `frontend/src/pages/Inventario/Inventario.tsx` con selector de tipo, selector de sucursal y tabla de stock con indicador de alerta.
- [ ] Implementar sección de historial con filtros combinados, sin botones de acción.
- [ ] Agregar la ruta `/inventario` en `App.tsx` y el módulo al diccionario "módulo → roles permitidos" (sin restricción de rol).
- [ ] Crear management command de seed con movimientos ficticios para probar esta feature antes de que existan Compras/Ventas/Producción.
- [ ] Escribir tests de backend: filtros combinados del historial, manejo de stock en 0 sin registro previo, ausencia de endpoints de escritura (verificar que `POST`/`PUT`/`DELETE` devuelven 405).
- [ ] Escribir tests de frontend: cambio entre tipo de inventario, filtrado por sucursal, indicador visual de alerta bajo el mínimo.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._
