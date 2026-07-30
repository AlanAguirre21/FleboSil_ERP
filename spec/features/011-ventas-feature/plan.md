# 011 · ventas — Plan

## Enfoque

Mismo patrón cabecera-detalle que Compras (`Venta` + `DetalleVenta`), pero con dos diferencias estructurales clave: la validación de stock ocurre *antes* de confirmar (no después, como "recibir" en Compras), y la confirmación de una venta dispara *dos* efectos automáticos en la misma transacción (inventario y caja), no solo uno. La generación de PDF se resuelve con una librería de Python (`weasyprint`) en un endpoint dedicado que arma el documento a partir de los datos ya guardados.

## Implementación

1. Backend — crear modelo `Venta` en `backend/apps/ventas/models.py`: `cliente_id` (FK nullable), `sucursal_id` (FK), `usuario_id` (FK), `fecha`, `fecha_entrega` (nullable), `fecha_entrega_real` (nullable), `total` (Decimal), `estado` (pendiente/entregada/cancelada).
2. Backend — crear modelo `DetalleVenta`: `venta_id` (FK), `producto_id` (FK), `cantidad`, `precio_unitario` (Decimal), `subtotal` (Decimal).
3. Backend — crear migraciones de ambos modelos.
4. Backend — crear `VentaSerializer` con líneas anidadas, calculando `subtotal`/`total` en el backend, igual que en Compras.
5. Backend — crear `VentaViewSet` con `list`, `retrieve`, `create` (la creación ya incluye la validación y confirmación, a diferencia de Compras donde crear y recibir son pasos separados).
6. Backend — en el método `create()` del serializer o una acción personalizada, envolver en `transaction.atomic()`: por cada línea, `select_for_update()` sobre `InventarioSucursalProducto`, validar `stock_actual >= cantidad` (si no, abortar con error claro antes de tocar cualquier tabla), descontar stock, crear `MovimientoInventario` de salida, y al final crear un único `MovimientoCaja` de ingreso por el total de la venta.
7. Backend — implementar acción `POST /api/ventas/{id}/entregar/`: cambia `estado` a `entregada` y registra `fecha_entrega_real`, sin tocar inventario ni caja.
8. Backend — implementar acción `POST /api/ventas/{id}/cancelar/`: dentro de `transaction.atomic()`, revierte stock (movimiento de entrada inverso por cada línea) y revierte caja (movimiento de retiro inverso por el total), luego marca `estado='cancelada'`.
9. Backend — crear endpoint `GET /api/ventas/{id}/ticket/` que genera el PDF con `weasyprint`, a partir de una plantilla HTML con los datos de `Venta` + `DetalleVenta`.
10. Backend — registrar rutas de `Venta` y sus acciones en el router principal.
11. Frontend — crear `frontend/src/api/ventas.js` con funciones de listado, creación, detalle, entregar, cancelar y descarga de ticket.
12. Frontend — crear `frontend/src/hooks/useVentas.js`, invalidando cache de `useInventario` tras crear/cancelar una venta.
13. Frontend — crear `frontend/src/pages/Ventas/Ventas.jsx`: lista filtrable por fecha/sucursal/estado/cliente/producto.
14. Frontend — crear `frontend/src/pages/Ventas/NuevaVenta.jsx`: selector de cliente (o sin cliente), selector de sucursal, buscador de producto con validación de stock disponible mostrada en vivo antes de confirmar.
15. Frontend — crear `frontend/src/pages/Ventas/DetalleVenta.jsx`: líneas, total, botón "Generar factura" (deshabilitado si el cliente no tiene datos fiscales completos, según lo definido en `008`), botón "Imprimir ticket"/"Exportar PDF", y acciones de entregar/cancelar según estado.

## Decisiones

- **Validación de stock antes de confirmar, con rechazo explícito por línea** — a diferencia de Compras (que siempre "recibe" lo que se compró), Ventas no puede permitir vender lo que no existe; se prioriza bloquear sobre permitir stock negativo, como ya se estableció en el diseño de datos original.
- **Creación de la venta ya incluye la confirmación (stock + caja) en un solo paso, sin estado intermedio "por confirmar"** — decidido explícitamente: el stock se descuenta al registrar, no al entregar; esto simplifica el flujo respecto a Compras, que sí tiene un paso separado de "recibir".
- **Cancelar revierte tanto inventario como caja siempre, sin importar el estado (pendiente/entregada)** — consecuencia directa de que ambos efectos ya ocurrieron al registrar; no hay forma de cancelar "antes de que afecte inventario/caja" porque ese momento ya pasó.
- **PDF generado on-demand en un endpoint dedicado, no almacenado como archivo permanente** — evita gestión de almacenamiento de archivos innecesaria; el ticket se reconstruye desde los datos ya guardados en `Venta`/`DetalleVenta` cada vez que se solicita, garantizando que siempre refleje la información real (incluso si se cancela después, se podría regenerar con estado "cancelada" visible).

## Riesgos

- **Condición de carrera real: dos usuarios vendiendo el mismo producto en la misma sucursal simultáneamente** — mitigación: `select_for_update()` es aquí más crítico que en Compras, porque Ventas sí puede fallar por falta de stock; debe bloquear la fila de inventario durante toda la transacción para que la segunda venta espere y vea el stock ya actualizado, no una lectura obsoleta.
- **Cancelar una venta entregada podría generar stock que en la práctica ya no existe físicamente (el producto salió del local con el cliente)** — mitigación: la reversión de stock en cancelación es una decisión contable/de trazabilidad, no una garantía física; se documenta explícitamente que cancelar una venta ya entregada requiere criterio del usuario (ej. solo cancelar por error de captura, no por devolución física real, que sería un flujo distinto no cubierto aquí).
- **Generación de PDF podría ser lenta si `weasyprint` no está optimizado o el servidor tiene recursos limitados** — mitigación: probar tiempos de generación con datos reales antes de production; si es un cuello de botella, considerar generar de forma asíncrona con notificación cuando esté listo, aunque para el volumen esperado (5-10 usuarios) probablemente no sea necesario.