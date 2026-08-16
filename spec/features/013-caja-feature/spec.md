# 013 · Caja

**Estado:** propuesta

## Qué hace

Muestra el historial de movimientos de caja global de la empresa (sin segmentación por sucursal), incluyendo tanto los movimientos automáticos generados por Ventas (ingreso) y sus cancelaciones (retiro inverso), como los movimientos manuales de ingreso o retiro que solo un usuario con rol admin puede registrar. Cada movimiento queda permanentemente registrado — nunca se edita ni se elimina; cualquier corrección se hace con un movimiento inverso nuevo. Muestra también el saldo actual de caja, calculado a partir del último movimiento.

## Por qué

Es el reflejo financiero consolidado de toda la operación del negocio — cierra el ciclo iniciado por Ventas (`011`), que ya genera movimientos automáticos, y da al admin control directo sobre entradas/salidas de efectivo que no provienen de una venta (aportaciones de capital, pago de gastos, retiros). Es también la base de datos que alimentará el Dashboard (`014`) y, más adelante, Contabilidad (`018`).

## Criterios de aceptación

- [ ] Esta vista es visible únicamente para el rol admin — un usuario operador no ve el módulo "Caja" en el sidebar ni puede acceder a sus endpoints.
- [ ] La lista de movimientos es de solo lectura para movimientos con `motivo = venta` (generados automáticamente) — no existe botón de edición ni eliminación sobre ningún movimiento, sin excepción.
- [ ] El admin puede registrar un movimiento manual de tipo `ingreso` o `retiro`, indicando monto y descripción (motivo textual).
- [ ] Cada movimiento manual queda asociado al usuario admin que lo registró y a la fecha/hora exacta.
- [ ] El saldo actual de caja se muestra de forma destacada, calculado como el `saldo_resultante` del movimiento más reciente — no como una suma recalculada de toda la tabla en cada consulta.
- [ ] La lista de movimientos es filtrable por fecha, tipo de movimiento (ingreso/retiro) y motivo.
- [ ] Cada fila muestra: fecha, tipo, monto, motivo, descripción, usuario, y saldo resultante tras ese movimiento.
- [ ] Un movimiento de tipo `venta` incluye referencia visible/enlazable a la venta que lo generó.
- [ ] No existe ningún endpoint de `PUT`, `PATCH` ni `DELETE` sobre movimientos de caja ya existentes — el backend los rechaza incluso si se llaman directo a la API.
- [ ] Si un retiro manual dejaría el saldo de caja en negativo, el sistema bloquea la operación de forma estricta, sin excepción ni confirmación posible — el saldo de caja nunca puede quedar por debajo de cero.
- [ ] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

## Fuera de alcance

- No incluye conciliación bancaria ni vínculo con cuentas bancarias reales — es un registro manual de efectivo/transferencias, según lo ya definido en la constitución.
- No incluye movimientos de caja generados por Compras — se documenta como posible ampliación futura si se decide que las compras también afecten caja directamente.
- No incluye reportes de caja por periodo más allá del filtro de fecha ya definido — reportes agregados (día/semana/mes) corresponden al Dashboard (`014`).