# 007 · catalogo — Plan

## Enfoque

Tres ViewSets de DRF independientes (`CategoriaViewSet`, `ProductoViewSet`, `MateriaPrimaViewSet`), reutilizando el mismo patrón de permisos (lectura para cualquier autenticado, escritura solo admin) y soft delete ya definidos en `006 · Sucursales`. Frontend: una sola página `Catalogo.tsx` con un selector de pestañas (Productos / Materia Prima / Categorías) que reutiliza los componentes comunes `Tabla` y `Modal` construidos en la feature anterior — sin duplicar su lógica.

## Implementación

1. Backend — modelo `Categoria` en `backend/apps/catalogo/models.py`: `nombre_categoria`, `descripcion_categoria`, `tipo` (choices: producto/materia_prima/ambos), `activo`. *(nombres de campo con sufijo de entidad, no `nombre`/`descripcion` a secas — consistente con el precedente de `Sucursal` en `006`, donde solo `activo` va sin sufijo)*
2. Backend — modelo `Producto`: `nombre_producto`, `sku` (único), `descripcion_producto`, `categoria` (FK), `precio_venta` (Decimal), `costo_produccion` (Decimal), `unidad_medida`, `activo`.
3. Backend — modelo `MateriaPrima`: `nombre_item`, `categoria` (FK, requerida), `unidad_medida`, `costo_promedio` (Decimal), `activo`. **Sin `proveedor_principal_id` en esta feature** — ver nota corregida en Decisiones.
4. Backend — modelos base ya existían de forma mínima (creados junto con `009`/`001` como soporte de `InventarioSucursalProducto`/`MateriaPrima`) con nombres `activo_categoria`/`activo_producto`/`activo_item`/`precio_unitario`; la migración `0002` los renombra a la convención de arriba, agrega `Categoria.tipo` y `MateriaPrima.categoria`, y hace backfill de las filas existentes antes de exigir la FK no nula.
5. Backend — crear serializers y ViewSets para `Categoria`, `Producto`, `MateriaPrima`, reutilizando la misma clase de permiso definida en `006 · Sucursales` (lectura abierta, escritura solo admin).
6. Backend — implementar validación de unicidad de `sku` a nivel de serializer, con mensaje de error claro.
7. Backend — implementar soft delete (override del método de borrado) en los tres ViewSets, igual que en Sucursales.
8. Backend — registrar rutas de los tres recursos en el router principal.
9. Frontend — crear `frontend/src/api/catalogo.ts` con funciones CRUD para los tres tipos.
10. Frontend — crear `frontend/src/hooks/useCategorias.ts`, `useProductos.ts`, `useMateriaPrima.ts` con React Query.
11. Frontend — crear `frontend/src/pages/Catalogo/Catalogo.tsx` con selector de pestañas (Productos / Materia Prima / Categorías) que renderiza la tabla correspondiente usando el componente común `Tabla`.
12. Frontend — crear los formularios de alta/edición de cada tipo dentro del `Modal` reutilizable, con campos específicos por tipo.
13. Frontend — ocultar botones de escritura si `rol !== 'admin'` (leyendo de `useUsuarioActual`).
14. Frontend — agregar la ruta `/catalogo` en `App.tsx`, protegida y dentro de `MainLayout`.
15. Backend — agregar una acción `reactivar` (`@action(detail=True, methods=['post'])`) a los tres ViewSets, análoga a `SucursalViewSet.reactivar` de `006` pero sin historial ni revalidación de unicidad (ver Decisiones): si ya está `activo`, responde `400` con mensaje claro; si no, pone `activo = True` y guarda.
16. Frontend — agregar `reactivarCategoria`/`reactivarProducto`/`reactivarMateriaPrima` a `api/catalogo.ts`, un hook `useReactivarX` por entidad, y un botón "Reactivar" + modal de confirmación por pestaña en `Catalogo.tsx`, igual que en `Sucursales.tsx`.

## Decisiones

- **Tres modelos y ViewSets separados, no uno polimórfico con un campo `tipo_item`** — consistente con la decisión ya tomada para `DetalleCompra` e `InventarioSucursal`: se prioriza integridad referencial real sobre economía de código, dado que ya se estableció ese criterio como estándar del proyecto.
- **Una sola página con selector de pestañas, en vez de tres rutas separadas** — reduce la navegación necesaria para un catálogo pequeño (consistente con la escala de la empresa) y reutiliza el mismo layout de tabla/modal para los tres tipos.
- **`proveedor_principal_id` se difiere por completo a `008 · Personas`, en vez de declararse ahora como FK nullable** — la idea original de esta sección (declarar la FK ya, apuntando a un `Proveedor` que la siguiente feature define) no es válida en Django: una migración no puede referenciar un modelo que todavía no existe en el registro de apps, sin importar el orden en que se apliquen las migraciones después. `008` agregará el campo con su propio `AddField` sobre `MateriaPrima` una vez que `Proveedor` exista.
- **Reutilización estricta de `Tabla` y `Modal` de la feature 006, sin crear variantes nuevas** — si estos componentes no cubren un caso (ej. selector de categoría filtrado dentro del modal), se extienden con nuevas props, no se duplican.

## Riesgos

- **Resuelto en la implementación**: la FK `proveedor_principal_id` no se declaró en esta feature (ver Decisiones) — el riesgo real era que Django no permite crear una FK hacia un modelo inexistente, así que la mitigación correcta fue diferir el campo por completo a `008 · Personas`, no intentar un orden de migraciones especial.
- **Backfill al agregar `MateriaPrima.categoria` como FK requerida sobre una tabla con filas existentes** — la migración `0002` la agrega como `null=True`, ejecuta un `RunPython` que asigna la categoría "General" (creándola si falta) a las filas sin categoría, y solo entonces la vuelve `null=False` vía `AlterField`.
- **El selector de categoría en los formularios de Producto/MateriaPrima podría mostrar categorías del tipo incorrecto si el filtrado por `tipo` no se implementa correctamente en el frontend** — mitigación: filtrar por `tipo` tanto en el query de `useCategorias` como validar en el backend que la categoría asignada corresponde al tipo correcto del ítem.
- **Reutilizar `Tabla`/`Modal` sin ajustar sus props para tres estructuras de datos distintas podría forzar hacks poco mantenibles** — mitigación: revisar antes de implementar si las props actuales de esos componentes (definidas en la feature 006) son suficientemente flexibles; si no, extenderlas ahí mismo antes de usarlas aquí.