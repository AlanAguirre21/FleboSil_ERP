# 007 · Catálogo

**Estado:** hecho

## Qué hace

Permite gestionar el catálogo de la empresa: Productos, Materia Prima y Categorías, mediante una única vista con selector para cambiar entre los tres tipos de catálogo. Ofrece operaciones CRUD completas (crear, ver, editar, desactivar) sobre cada uno, exclusivas para el rol admin. Los campos de stock no forman parte de esta feature — Productos y Materia Prima describen únicamente qué es el ítem (nombre, precio/costo, categoría, unidad de medida), no cuánto hay ni en qué sucursal, eso corresponde al módulo de Inventario.

## Por qué

Es prerrequisito directo de Ventas, Compras y Producción — ninguna de esas features puede funcionar sin productos y materia prima ya definidos en el sistema. Se construye después de Sucursales porque, aunque el catálogo en sí no depende de sucursal, sí es requisito previo de Inventario, que sí la necesita.

## Criterios de aceptación

- [x] Existe un selector visible para alternar entre las vistas de Productos, Materia Prima y Categorías, sin necesidad de recargar la página.
- [x] CRUD de Categorías (solo admin): crear, editar, desactivar, con campo `tipo` (producto / materia_prima / ambos) para filtrar dónde aplica cada categoría.
- [x] CRUD de Productos (solo admin): nombre, SKU, descripción, categoría (filtrada a categorías de tipo producto o ambos), precio de venta, costo de producción, unidad de medida.
- [x] CRUD de Materia Prima (solo admin): nombre, categoría (filtrada a categorías de tipo materia_prima o ambos), unidad de medida, costo promedio. *(`proveedor principal` queda fuera de esta entrega — ver nota en `plan.md`: no puede declararse una FK hacia un modelo, `Proveedor`, que `008 · Personas` todavía no crea; esa feature la agregará con un `AddField` propio)*
- [x] El SKU de un producto es único en el sistema; el backend rechaza duplicados con un mensaje claro.
- [x] Todo campo monetario (`precio_venta`, `costo_produccion`, `costo_promedio`) acepta únicamente valores numéricos no negativos, almacenados como `Decimal`.
- [x] Desactivar un producto o materia prima (`activo=false`) no lo elimina físicamente ni rompe referencias en ventas, compras o producción ya registradas — solo deja de aparecer como opción seleccionable en formularios nuevos.
- [x] Un usuario con rol operador puede consultar el catálogo en modo lectura, sin ver botones de crear, editar ni desactivar.
- [x] El backend rechaza cualquier intento de escritura (crear/editar/desactivar) desde un usuario con rol operador, incluso llamando directo a la API.
- [x] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

## Reactivación de categorías, productos y materia prima

- [x] Un usuario con rol admin puede reactivar una categoría, producto o materia prima previamente desactivados, estableciendo `activo = true`.
- [x] Reactivar una categoría/producto/materia prima que ya está activa se rechaza con un mensaje claro (`400`), sin generar ningún cambio.
- [x] El backend rechaza cualquier intento de reactivar desde un usuario con rol operador, incluso llamando directo a la API.
- [x] A diferencia de `006 · Sucursales`, esta reactivación **no** requiere un historial de auditoría (`HistorialEstado*`) ni una revalidación de unicidad de nombre al reactivar: `Producto.sku` ya es único a nivel de base de datos sin importar `activo`, y `Categoria`/`MateriaPrima` no tienen ninguna restricción de unicidad de nombre — por lo que una reactivación nunca puede colisionar con un registro activo existente, a diferencia de `Sucursal.nombre_sucursal`.

## Fuera de alcance

- No incluye campos de stock (`stock_actual`, `stock_minimo`) — pertenecen a `009 · Inventario`.
- No incluye gestión de recetas (relación producto ↔ materia prima) — corresponde a `012 · Producción`.
- No incluye carga masiva desde Excel — quedó documentada como idea en el backlog.
- No incluye `MateriaPrima.proveedor_principal` — corresponde a `008 · Personas`, que agregará el campo una vez exista el modelo `Proveedor`.