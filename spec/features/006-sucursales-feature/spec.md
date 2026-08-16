# 006 · Sucursales

**Estado:** hecho para el alcance propio de esta feature — reactivación, validación de nombre duplicado e `HistorialEstadoSucursal` implementados y verificados. Dos criterios quedan sin marcar a propósito: el bloqueo de `MovimientoInventario` y la denormalización en CFDI viven en el código de `009`/`010`/`011`/`012` y `017` respectivamente, features que todavía no existen — ver `Fuera de alcance`.

## Qué hace

Permite gestionar el catálogo de sucursales de la empresa: alta, edición, desactivación, reactivación y consulta. Un usuario con rol admin puede crear, editar, desactivar y reactivar sucursales; un usuario con rol operador solo puede consultarlas en modo lectura. Cada sucursal representa una ubicación física con su propio inventario — no tiene relación con ganancias, caja ni personal, que son globales a la empresa. Cada cambio de estado (activo ⇄ inactivo) queda registrado de forma permanente en un historial de auditoría.

## Por qué

Es la base sobre la que se construye todo el módulo de inventario (`009`), compras (`010`) y ventas (`011`): ninguna de esas features puede registrar movimientos de stock sin que exista al menos una sucursal previamente definida en el sistema. Por eso va primero en el roadmap, inmediatamente después del bloque de autenticación.

La reactivación y la reutilización de nombres se agregan porque, en la operación real de la empresa, una sucursal puede cerrar temporalmente y volver a abrir después (o un admin puede desactivar una por error) — sin estas capacidades, cada cierre habría sido permanente y cada reapertura habría requerido un nombre distinto o dejar un `nombre_sucursal` "quemado" para siempre.

## Criterios de aceptación

### Ya implementado

- [x] Un usuario con rol admin puede crear una nueva sucursal indicando nombre, dirección y teléfono.
- [x] Un usuario con rol admin puede editar los datos de una sucursal existente.
- [x] Un usuario con rol admin puede desactivar una sucursal (`activo = false`), sin eliminarla físicamente de la base de datos.
- [x] Una sucursal desactivada no aparece como opción seleccionable en los formularios de Ventas, Compras, Producción ni Inventario, pero sí sigue visible en el historial de movimientos ya registrados con ella.
- [x] Un usuario con rol operador puede ver la lista de sucursales, pero no ve botones de crear, editar ni desactivar.
- [x] El backend rechaza cualquier intento de crear/editar/desactivar sucursales desde un usuario con rol operador, incluso si la petición se hace directo a la API sin pasar por la interfaz.
- [x] No es posible eliminar físicamente (`DELETE` real) una sucursal que ya tiene movimientos de inventario asociados — solo desactivar.
- [x] La lista de sucursales es consultable desde el módulo correspondiente sin necesidad de filtros adicionales (volumen esperado bajo, 2-3 sucursales inicialmente).
- [x] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

### Reactivación de sucursales

- [x] Un usuario con rol admin puede reactivar una sucursal previamente desactivada, estableciendo `activo = true`.
- [x] Al reactivar una sucursal, su inventario (`InventarioSucursalProducto`/`InventarioSucursalMateriaPrima`, feature `009`) vuelve a estar disponible de inmediato para nuevos movimientos — estas tablas no tienen un campo `activo` propio; su disponibilidad depende exclusivamente de `Sucursal.activo`, por lo que no hay ningún registro adicional que actualizar ni validar al reactivar.
- [x] Los empleados y los movimientos de caja (`MovimientosCaja`, feature `013`) nunca se ven afectados por la activación o desactivación de una sucursal, bajo ninguna circunstancia — son entidades globales a la empresa (ver `constitution/mission.md`) y este flujo no debe tocarlos ni leerlos.
- [x] El backend rechaza cualquier intento de reactivar una sucursal desde un usuario con rol operador, incluso llamando directo a la API.

### Validación de nombre duplicado

- [x] Registrar una sucursal (crear o reactivar) con el mismo `nombre_sucursal` que una sucursal ya existente se permite únicamente si **ambas** condiciones se cumplen: (a) ninguna sucursal existente con ese mismo nombre tiene la misma `ubicacion_sucursal` que la que se está registrando (dos ubicaciones vacías cuentan como coincidencia), y (b) todas las sucursales existentes con ese nombre tienen `activo = false`.
- [x] Si existe al menos una sucursal **activa** con el mismo `nombre_sucursal`, el registro (creación o reactivación) se rechaza sin importar la ubicación.
- [x] La comparación de `nombre_sucursal` y `ubicacion_sucursal` es exacta (sensible a mayúsculas/minúsculas, sin normalizar espacios).
- [x] Esta misma validación aplica al editar el `nombre_sucursal` de una sucursal existente (esté activa o inactiva) — no es posible renombrarla hacia una colisión con una sucursal activa ya existente.
- [x] La validación se implementa a nivel de serializer/servicio, no como restricción de base de datos — `nombre_sucursal` no tiene (ni debe tener) un `unique_together`/`unique` a nivel de modelo, dado que puede repetirse legítimamente entre sucursales inactivas.

### Bloqueo de movimientos de inventario para sucursales inactivas

*(Sin marcar a propósito — este código vive en `009 · Inventario`/`010`/`011`/`012`, que todavía no existen. `Sucursal.activo` ya es la fuente de verdad que esas features deben consultar; ver "Pendiente" en `tasks.md`.)*

- [ ] No es posible crear un nuevo `MovimientoInventario` (feature `009`) cuya sucursal asociada tenga `activo = false`; el backend rechaza el intento dentro de la misma `transaction.atomic()` de la operación que lo origina (venta, compra, producción, ajuste).
- [ ] Esta validación aplica exclusivamente al momento de creación — no es retroactiva. Los `MovimientoInventario` ya existentes de una sucursal ahora inactiva permanecen intactos y consultables indefinidamente (patrón INSERT-only ya establecido en la constitución).
- [ ] Al reactivar una sucursal, es posible volver a generar `MovimientoInventario` para ella a partir de ese momento, sin ninguna acción adicional.
- [ ] `MovimientosCaja` (feature `013`) **no** lleva ninguna validación directa de sucursal — Caja es una entidad global sin FK a `Sucursal` (ver `constitution/mission.md`: "la sucursal es una dimensión de inventario, no de negocio"; `CLAUDE.md`: "profit, cash (caja)... are global to the company, never segmented by branch"). La protección para operaciones que combinan inventario y caja en una misma transacción (ej. una venta) ocurre de forma indirecta: si el paso de inventario de esa transacción es rechazado por sucursal inactiva, toda la transacción —incluido el movimiento de caja asociado— se revierte, sin que `MovimientoCaja` necesite conocer la sucursal.

### `HistorialEstadoSucursal` (nueva entidad)

- [x] Cada cambio de `activo` en una sucursal (desactivación o reactivación) genera un registro nuevo en `HistorialEstadoSucursal`, con al menos: sucursal, estado anterior, estado nuevo, usuario que realizó el cambio y fecha/hora.
- [x] `HistorialEstadoSucursal` es **INSERT-only**, igual que `MovimientosCaja`/`MovimientosInventario` — ningún registro se edita ni se elimina; el historial completo de una sucursal queda siempre disponible para auditoría.
- [x] El registro en `HistorialEstadoSucursal` se crea dentro de la misma `transaction.atomic()` que el cambio de `activo` en `Sucursal` — si uno falla, el otro tampoco se guarda.

### Nota para features futuras (CFDI / Facturación)

*(Sin marcar a propósito — corresponde al código de `017 · Facturación`, que todavía no existe.)*

- [ ] Cualquier documento fiscal (CFDI, feature `017 · Facturación`) debe almacenar los datos de la sucursal (nombre, ubicación) de forma **desnormalizada** al momento de su emisión, nunca como una referencia viva por FK — dado que, a partir de esta feature, `nombre_sucursal` deja de ser único de forma permanente en el sistema.

## Fuera de alcance

- No incluye la relación de sucursal con inventario, ventas o compras — esas relaciones se implementan en sus respectivas features (`009`, `010`, `011`), que dependen de que esta ya exista.
- No incluye asignación de empleados o usuarios a una sucursal fija — ya se estableció que el personal es global, sin importar esta feature.
- No incluye reportes ni comparativas entre sucursales — las ganancias son globales, según lo definido en la constitución del proyecto.
- No agrega un campo `activo` a `InventarioSucursalProducto`/`InventarioSucursalMateriaPrima` — su disponibilidad depende exclusivamente de `Sucursal.activo`, sin estado propio que sincronizar ni cascada real que ejecutar.
- No agrega segmentación de Caja por sucursal ni un `sucursal_id` a `MovimientosCaja` — Caja permanece global a la empresa; el bloqueo de movimientos por sucursal inactiva aplica únicamente a `MovimientoInventario`.
- No implementa todavía la denormalización de datos de sucursal en `017 · Facturación` — solo se documenta aquí como criterio a respetar cuando esa feature se construya.
- No incluye un endpoint ni una vista para consultar `HistorialEstadoSucursal` — decisión explícita para esta iteración: por ahora es un registro de auditoría interno (se crea, pero no se expone para lectura vía API ni interfaz). Se añadiría como extensión menor (endpoint de solo lectura + tabla) si surge la necesidad real de auditarlo desde la UI.
