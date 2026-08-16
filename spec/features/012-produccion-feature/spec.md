# 012 · Producción

**Estado:** propuesta

## Qué hace

Permite definir la receta de cada producto (qué materia prima y cuánta se necesita para producir una unidad), y registrar producciones que, al confirmarse, consumen automáticamente la materia prima correspondiente del inventario de la sucursal y generan el stock de producto terminado. Cada producción guarda una copia congelada de las cantidades de materia prima realmente consumidas, independiente de cambios futuros en la receta. Incluye una lista de producciones registradas, filtrable por fecha, sucursal y producto, y una vista de gestión de recetas (crear, editar, consultar).

## Por qué

Cierra el ciclo de inventario para empresas que fabrican sus propios productos en vez de solo revenderlos: sin esta feature, la materia prima comprada (`010 · Compras`) nunca se convierte en producto vendible dentro del sistema. Depende de que Catálogo e Inventario ya existan, y es la última pieza operativa antes de Caja, que ya puede recibir movimientos reales desde Ventas.

## Criterios de aceptación

- [ ] Un usuario con rol admin puede crear, editar y desactivar una receta: seleccionar un producto y asociarle una o varias materias primas con la cantidad requerida por unidad producida.
- [ ] Un usuario con rol operador puede consultar las recetas existentes en modo lectura, sin botones de creación ni edición.
- [ ] Cualquier usuario autenticado puede registrar una nueva producción: seleccionar producto, sucursal, y cantidad a producir.
- [ ] Antes de confirmar una producción, el sistema calcula la materia prima total requerida (según la receta vigente) para la cantidad solicitada, y valida que hay stock suficiente de cada materia prima en la sucursal seleccionada.
- [ ] Si no hay stock suficiente de alguna materia prima, la producción se rechaza por completo con un mensaje claro indicando qué materia prima falta y cuánta hace falta — nunca se permite una producción parcial.
- [ ] Al confirmar una producción, en una sola transacción: se descuenta cada materia prima consumida del inventario de la sucursal, se registran los movimientos de tipo `salida` correspondientes (motivo `produccion_consumo`), se guarda un `DetalleProduccion` por cada materia prima consumida (con la cantidad exacta usada y su costo al momento), se aumenta el stock del producto terminado en la misma sucursal, y se registra el movimiento de tipo `entrada` correspondiente (motivo `produccion_entrada`) — todos con el mismo `referencia_id` apuntando a este lote de producción.
- [ ] El costo total de la producción se calcula sumando `cantidad_consumida × costo_promedio` de cada materia prima usada al momento de producir, y se guarda tanto el detalle por materia prima (`DetalleProduccion`) como el total (`Produccion.costo_total`).
- [ ] Si la receta de un producto se edita después de una producción ya registrada, el historial de esa producción no cambia — sigue reflejando exactamente lo que se consumió en ese momento, vía `DetalleProduccion`.
- [ ] Si cualquier paso de la transacción falla, ningún cambio parcial queda guardado.
- [ ] Un producto sin receta activa no puede producirse — el sistema bloquea el intento con un mensaje indicando que falta configurar la receta.
- [ ] La lista de producciones registradas es filtrable por fecha, sucursal y producto; su vista de detalle muestra el desglose de materia prima consumida vía `DetalleProduccion`.
- [ ] No existe forma de editar ni eliminar un registro de producción ya confirmado — solo consulta.
- [ ] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

## Fuera de alcance

- No incluye actualización automática de `costo_produccion` en el modelo `Producto` a partir del costo calculado aquí.
- No incluye producción con múltiples productos en un mismo lote.
- No incluye reversión ni cancelación de una producción ya confirmada.