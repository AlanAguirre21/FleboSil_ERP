# 009 · Inventario

**Estado:** propuesta

## Qué hace

Muestra el stock actual de Productos y Materia Prima por sucursal, con selector para cambiar entre ambos tipos de inventario y selector de sucursal para filtrar la tabla. Incluye un historial de movimientos de inventario de solo lectura, filtrable por producto/materia prima, sucursal y tipo de movimiento (entrada/salida). No permite edición manual directa del stock — todo cambio de inventario ocurre como consecuencia de otra operación (compra, venta, producción), registrada en el módulo correspondiente.

## Por qué

Es el punto donde se hace visible el efecto acumulado de Compras, Ventas y Producción sobre el stock físico de la empresa — sin esta feature, no hay forma de consultar cuánto hay disponible antes de vender, ni de auditar por qué cambió una cantidad. Se construye antes que Compras/Ventas/Producción porque esos módulos necesitan poder leer y escribir sobre `InventarioSucursalProducto`/`MateriaPrima`, que aquí quedan expuestos por primera vez a través de una interfaz.

## Criterios de aceptación

- [ ] Existe un selector para alternar entre "Inventario de productos" e "Inventario de materia prima".
- [ ] Existe un selector de sucursal que filtra la tabla de stock mostrada.
- [ ] La tabla de stock muestra, por cada ítem: nombre, stock actual, stock mínimo, y un indicador visual (color de advertencia) cuando `stock_actual < stock_minimo`.
- [ ] Existe una sección de historial de movimientos, de solo lectura, sin botones de creación ni edición en ninguna parte de esta feature.
- [ ] El historial es filtrable por producto/materia prima, por sucursal y por tipo de movimiento (entrada/salida).
- [ ] Cada fila del historial muestra: fecha, ítem, sucursal, tipo de movimiento, cantidad, motivo (compra/venta/producción/ajuste), y usuario que lo generó.
- [ ] No existe ningún formulario ni botón en esta feature que permita modificar `stock_actual` directamente — el stock solo cambia como efecto de Compras, Ventas o Producción, ya construidas o por construir en features posteriores.
- [ ] Cualquier usuario autenticado puede consultar el inventario y su historial, sin restricción de rol (es información operativa de consulta diaria, no administrativa).
- [ ] Si una sucursal no tiene registros de inventario para un ítem (ej. producto nuevo aún no comprado ahí), se muestra como `stock_actual = 0`, no como error ni fila vacía.

## Fuera de alcance

- No incluye edición manual de stock — cualquier ajuste (ej. corrección por conteo físico) requiere un mecanismo de "ajuste manual" que, si se necesita, sería una feature separada y documentada explícitamente como excepción auditable, no incluida aquí.
- No incluye las operaciones que generan movimientos (Compras, Producción) — esta feature solo consume y muestra `InventarioSucursalProducto`/`MateriaPrima` y `MovimientosInventario`, que otras features poblarán.
- No incluye alertas push ni notificaciones fuera del dropdown ya construido en `001 · Header` — esta feature reutiliza esa fuente de datos, no crea un sistema de notificación nuevo.