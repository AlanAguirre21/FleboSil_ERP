# 011 · Ventas — Tareas

- [ ] Crear modelo `Venta` (cabecera) y su migración.
- [ ] Crear modelo `DetalleVenta` y su migración.
- [ ] Crear `VentaSerializer` con líneas anidadas y cálculo de `total`/`subtotal` en el backend.
- [ ] Crear `VentaViewSet` con `list`, `retrieve`, `create`.
- [ ] Implementar la lógica de creación con `transaction.atomic()` + `select_for_update()`: validación de stock, descuento, movimiento de inventario, movimiento de caja.
- [ ] Implementar acción `entregar()`, actualizando `estado` y `fecha_entrega_real` sin tocar inventario/caja.
- [ ] Implementar acción `cancelar()`, revirtiendo stock y caja dentro de la misma transacción.
- [ ] Crear endpoint `GET /api/ventas/{id}/ticket/` generando PDF con `weasyprint`.
- [ ] Crear plantilla HTML del ticket con los datos de cabecera y líneas.
- [ ] Registrar rutas de `Venta` y sus acciones en el router.
- [ ] Crear `frontend/src/api/ventas.ts` con las funciones necesarias, incluida descarga del PDF.
- [ ] Crear `frontend/src/hooks/useVentas.ts`, invalidando cache de `useInventario` tras crear/cancelar.
- [ ] Crear `frontend/src/pages/Ventas/Ventas.tsx` con lista filtrable por los 5 criterios definidos.
- [ ] Crear `frontend/src/pages/Ventas/NuevaVenta.tsx`, mostrando stock disponible en vivo antes de confirmar cada línea.
- [ ] Crear `frontend/src/pages/Ventas/DetalleVenta.tsx` con botones de ticket/PDF, factura (placeholder hasta `017`), entregar y cancelar.
- [ ] Agregar la ruta `/ventas` en `App.tsx` y el módulo al diccionario "módulo → roles permitidos" (sin restricción de rol).
- [ ] Escribir tests de backend: creación con stock suficiente, rechazo por stock insuficiente, cálculo correcto de total, generación simultánea de movimiento de inventario y caja, entrega sin efectos secundarios, cancelación con reversión de stock y caja, condición de carrera con `select_for_update()` (test de concurrencia si es viable).
- [ ] Escribir tests de frontend: validación de stock en vivo, cálculo de total al agregar/quitar líneas, botones de acción según estado.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._