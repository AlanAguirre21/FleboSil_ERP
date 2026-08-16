# 010 · Compras

**Estado:** propuesta

## Qué hace

Permite registrar compras de materia prima y/o productos ante un proveedor, destinadas a una sucursal específica. Cada compra tiene una cabecera (proveedor, sucursal destino, fecha, fecha de entrega, estado, total) y una o varias líneas de detalle (ítem comprado, tipo, cantidad, costo unitario). Al marcar una compra como recibida, el sistema aumenta automáticamente el stock correspondiente en `InventarioSucursalProducto`/`MateriaPrima` y genera el movimiento de entrada correspondiente en `MovimientosInventario`. Incluye una lista de compras filtrable por proveedor, fecha y estado, y una vista de detalle de cada compra registrada.

## Por qué

Es la primera vía real para que el inventario definido en la feature anterior tenga stock disponible — sin Compras, `InventarioSucursalProducto`/`MateriaPrima` permanecería siempre en cero. También es prerrequisito indirecto de Producción, que necesita materia prima ya existente en stock para poder producir.

## Criterios de aceptación

- [ ] Un usuario autenticado puede registrar una nueva compra seleccionando proveedor, sucursal destino, y agregando una o más líneas (producto o materia prima) con cantidad y costo unitario.
- [ ] El total de la compra se calcula automáticamente como la suma de los subtotales de sus líneas, y se recalcula en vivo mientras se agregan o quitan ítems.
- [ ] Una compra se crea con estado `pendiente` por defecto; puede marcarse como `recibida` o `cancelada` desde la vista de detalle.
- [ ] Al marcar una compra como `recibida`, el sistema, en una sola transacción: aumenta el stock del ítem correspondiente en la sucursal destino, y registra un movimiento de tipo `entrada` en `MovimientosInventario` con motivo `compra` y referencia a esta compra.
- [ ] Si la transacción de recepción falla en cualquier paso, ningún cambio parcial queda guardado (ni stock aumentado sin movimiento registrado, ni viceversa).
- [ ] Una compra en estado `cancelada` no genera ni revierte movimientos de inventario; si ya estaba `recibida` y se cancela después, debe generarse el movimiento inverso correspondiente (salida) para mantener la trazabilidad, nunca editar el movimiento original.
- [ ] La lista de compras es filtrable por proveedor, fecha y estado.
- [ ] La vista de detalle de una compra muestra sus líneas, el proveedor, la sucursal destino, el total y el estado actual.
- [ ] El costo unitario de cada línea se congela en `DetalleCompraProducto`/`DetalleCompraMateriaPrima` al momento de la compra — no se recalcula ni cambia si el `costo_promedio` del ítem se actualiza después.
- [ ] Cualquier usuario autenticado puede registrar y consultar compras, sin restricción de rol (es operación diaria, consistente con el criterio ya aplicado a Clientes/Proveedores).
- [ ] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

## Fuera de alcance

- No incluye actualización automática de `costo_promedio` en Materia Prima a partir del costo de compra — se documenta como posible mejora en backlog si se decide implementar costeo promedio ponderado automático.
- No incluye órdenes de compra ni cotizaciones previas a la compra en firme — el flujo actual asume registro directo de una compra ya decidida.
- No incluye pagos ni relación con Caja — el módulo de Caja (`013`) es global y no distingue compras específicas como origen de un movimiento en esta iteración; se documenta como posible ampliación futura.