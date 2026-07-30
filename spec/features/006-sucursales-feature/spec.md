# 006 · Sucursales

**Estado:** propuesta

## Qué hace

Permite gestionar el catálogo de sucursales de la empresa: alta, edición, desactivación y consulta. Un usuario con rol admin puede crear, editar y desactivar sucursales; un usuario con rol operador solo puede consultarlas en modo lectura. Cada sucursal representa una ubicación física con su propio inventario — no tiene relación con ganancias, caja ni personal, que son globales a la empresa.

## Por qué

Es la base sobre la que se construye todo el módulo de inventario (`009`), compras (`010`) y ventas (`011`): ninguna de esas features puede registrar movimientos de stock sin que exista al menos una sucursal previamente definida en el sistema. Por eso va primero en el roadmap, inmediatamente después del bloque de autenticación.

## Criterios de aceptación

- [ ] Un usuario con rol admin puede crear una nueva sucursal indicando nombre, dirección y teléfono.
- [ ] Un usuario con rol admin puede editar los datos de una sucursal existente.
- [ ] Un usuario con rol admin puede desactivar una sucursal (`activo = false`), sin eliminarla físicamente de la base de datos.
- [ ] Una sucursal desactivada no aparece como opción seleccionable en los formularios de Ventas, Compras, Producción ni Inventario, pero sí sigue visible en el historial de movimientos ya registrados con ella.
- [ ] Un usuario con rol operador puede ver la lista de sucursales, pero no ve botones de crear, editar ni desactivar.
- [ ] El backend rechaza cualquier intento de crear/editar/desactivar sucursales desde un usuario con rol operador, incluso si la petición se hace directo a la API sin pasar por la interfaz.
- [ ] No es posible eliminar físicamente (`DELETE` real) una sucursal que ya tiene movimientos de inventario asociados — solo desactivar.
- [ ] La lista de sucursales es consultable desde el módulo correspondiente sin necesidad de filtros adicionales (volumen esperado bajo, 2-3 sucursales inicialmente).

## Fuera de alcance

- No incluye la relación de sucursal con inventario, ventas o compras — esas relaciones se implementan en sus respectivas features (`009`, `010`, `011`), que dependen de que esta ya exista.
- No incluye asignación de empleados o usuarios a una sucursal fija — ya se estableció que el personal es global, sin importar esta feature.
- No incluye reportes ni comparativas entre sucursales — las ganancias son globales, según lo definido en la constitución del proyecto.