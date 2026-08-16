# 010 · Compras — Tareas

- [ ] Crear modelo `Compra` (cabecera) y su migración.
- [ ] Crear modelo `DetalleCompraProducto` y su migración.
- [ ] Crear modelo `DetalleCompraMateriaPrima` y su migración.
- [ ] Crear `CompraSerializer` con validación de líneas anidadas y cálculo de `total`/`subtotal` en el backend.
- [ ] Crear `CompraViewSet` con `list`, `retrieve`, `create`.
- [ ] Implementar acción `recibir()` con `transaction.atomic()` + `select_for_update()`, creando el registro de inventario si no existe.
- [ ] Implementar acción `cancelar()`, con generación de movimiento inverso si la compra ya estaba recibida, y validación de stock suficiente antes de revertir.
- [ ] Registrar rutas de `Compra` y sus acciones personalizadas en el router.
- [ ] Crear `frontend/src/api/compras.ts` con las funciones necesarias.
- [ ] Crear `frontend/src/hooks/useCompras.ts`, invalidando cache de `useInventario` tras recibir/cancelar.
- [ ] Crear `frontend/src/pages/Compras/Compras.tsx` con lista filtrable.
- [ ] Crear `frontend/src/pages/Compras/NuevaCompra.tsx` con selector de proveedor/sucursal y líneas dinámicas.
- [ ] Crear `frontend/src/pages/Compras/DetalleCompra.tsx` con botones de acción según estado.
- [ ] Agregar la ruta `/compras` en `App.tsx` y el módulo al diccionario "módulo → roles permitidos" (sin restricción de rol).
- [ ] Escribir tests de backend: creación con múltiples líneas, cálculo correcto de total, recepción exitosa (stock + movimiento), cancelación de compra pendiente, cancelación de compra ya recibida (movimiento inverso), bloqueo de cancelación si no hay stock suficiente para revertir.
- [ ] Escribir tests de frontend: cálculo de total en vivo al agregar/quitar líneas, botones de acción según estado, invalidación de cache de inventario tras recibir.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._