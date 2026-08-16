# 011 · Ventas

**Estado:** propuesta

## Qué hace

Permite registrar una venta seleccionando cliente (opcional), sucursal, y agregando una o varias líneas de producto con cantidad. Al confirmar la venta, el sistema valida stock suficiente en la sucursal seleccionada, descuenta el stock de inmediato, registra el movimiento de inventario correspondiente, y genera automáticamente un movimiento de ingreso en Caja. Permite imprimir o exportar a PDF el ticket de la venta. Admite una fecha de entrega opcional, con estados pendiente/entregada/cancelada independientes del descuento de stock (que ya ocurrió al registrar).

## Por qué

Es el flujo más transitado del sistema — el corazón operativo diario de la empresa. Depende de que Catálogo, Personas e Inventario ya existan, y es el disparador que por primera vez genera movimientos automáticos en Caja, cerrando el ciclo completo: venta → descuento de stock → ingreso de efectivo.

## Criterios de aceptación

- [ ] Un usuario autenticado puede registrar una venta seleccionando cliente (o "sin cliente"), sucursal, y agregando una o más líneas de producto con cantidad.
- [ ] Antes de confirmar cada línea, el sistema valida que hay stock suficiente del producto en la sucursal seleccionada; si no lo hay, la línea se rechaza con un mensaje claro indicando el stock disponible.
- [ ] El total de la venta se calcula automáticamente como la suma de los subtotales de sus líneas, en vivo mientras se agregan o quitan productos.
- [ ] Al confirmar la venta, en una sola transacción: se descuenta el stock del producto en la sucursal, se registra un movimiento de tipo `salida` en `MovimientosInventario` (motivo `venta`), y se registra un movimiento de tipo `ingreso` en `MovimientosCaja` (motivo `venta`, con referencia a la venta).
- [ ] Si cualquier paso de esa transacción falla, ningún cambio parcial queda guardado (ni stock descontado sin movimiento de caja, ni viceversa).
- [ ] El precio unitario de cada línea se congela en `DetalleVenta` al momento de la venta — no cambia si el `precio_venta` del producto se actualiza después.
- [ ] La venta admite una fecha de entrega opcional; si se especifica, el estado inicial es `pendiente`, de lo contrario `entregada` de inmediato (venta de mostrador).
- [ ] Una venta `pendiente` puede marcarse como `entregada` (registrando `fecha_entrega_real`) sin que esto genere ningún nuevo movimiento de stock o caja — ambos ya ocurrieron al registrar la venta.
- [ ] Cancelar una venta, en cualquier estado, revierte el stock descontado (movimiento de entrada inverso) y revierte el ingreso de caja (movimiento de retiro inverso), ambos dentro de la misma transacción atómica, sin editar los movimientos originales.
- [ ] La lista de ventas es filtrable por fecha, sucursal, estado, cliente y producto.
- [ ] La vista de detalle de una venta permite imprimir el ticket y exportarlo a PDF.
- [ ] Cualquier usuario autenticado puede registrar y consultar ventas, sin restricción de rol.
- [ ] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

## Fuera de alcance

- No incluye la generación de factura fiscal (CFDI) — corresponde a `017 · Facturación`, que se dispara desde el botón "Generar factura" ya contemplado en la spec general, consumiendo los datos de esta venta.
- No incluye descuentos, promociones ni precios especiales por cliente — el precio unitario es siempre el `precio_venta` vigente del producto al momento de la venta.
- No incluye impresión térmica directa (ESC/POS) — solo PDF, según lo ya documentado en backlog como posible mejora futura.