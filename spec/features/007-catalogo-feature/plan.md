# 007 · catalogo — Plan

## Enfoque

Tres ViewSets de DRF independientes (`CategoriaViewSet`, `ProductoViewSet`, `MateriaPrimaViewSet`), reutilizando el mismo patrón de permisos (lectura para cualquier autenticado, escritura solo admin) y soft delete ya definidos en `006 · Sucursales`. Frontend: una sola página `Catalogo.tsx` con un selector de pestañas (Productos / Materia Prima / Categorías) que reutiliza los componentes comunes `Tabla` y `Modal` construidos en la feature anterior — sin duplicar su lógica.

## Implementación

1. Backend — crear modelo `Categoria` en `backend/apps/catalogo/models.py`: `nombre`, `descripcion`, `tipo` (choices: producto/materia_prima/ambos), `activo`.
2. Backend — crear modelo `Producto`: `nombre`, `sku` (único), `descripcion`, `categoria_id` (FK), `precio_venta` (Decimal), `costo_produccion` (Decimal), `unidad_medida`, `activo`.
3. Backend — crear modelo `MateriaPrima`: `nombre`, `categoria_id` (FK), `unidad_medida`, `costo_promedio` (Decimal), `proveedor_principal_id` (FK, nullable — apunta a `Proveedores`, aún no creado; se deja como FK diferida hasta la feature `008 · Personas`), `activo`.
4. Backend — crear migraciones de los tres modelos.
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

## Decisiones

- **Tres modelos y ViewSets separados, no uno polimórfico con un campo `tipo_item`** — consistente con la decisión ya tomada para `DetalleCompra` e `InventarioSucursal`: se prioriza integridad referencial real sobre economía de código, dado que ya se estableció ese criterio como estándar del proyecto.
- **Una sola página con selector de pestañas, en vez de tres rutas separadas** — reduce la navegación necesaria para un catálogo pequeño (consistente con la escala de la empresa) y reutiliza el mismo layout de tabla/modal para los tres tipos.
- **`proveedor_principal_id` como FK nullable, aunque `Proveedores` no existe todavía** — se declara la relación desde ahora para no tener que hacer una migración posterior que altere `MateriaPrima`; Django permite crear la FK apuntando a un modelo que se define en la siguiente feature, siempre que ambas migraciones se apliquen en orden.
- **Reutilización estricta de `Tabla` y `Modal` de la feature 006, sin crear variantes nuevas** — si estos componentes no cubren un caso (ej. selector de categoría filtrado dentro del modal), se extienden con nuevas props, no se duplican.

## Riesgos

- **La FK `proveedor_principal_id` hacia un modelo `Proveedor` que no existe aún podría causar error de migración si no se ordena correctamente** — mitigación: crear el campo como nullable desde el inicio y aplicar la migración de `Producto`/`MateriaPrima` únicamente después de que `Proveedores` exista, o usar una migración de dos pasos (crear campo, luego poblar) si el orden del roadmap ya avanzó sin esa tabla.
- **El selector de categoría en los formularios de Producto/MateriaPrima podría mostrar categorías del tipo incorrecto si el filtrado por `tipo` no se implementa correctamente en el frontend** — mitigación: filtrar por `tipo` tanto en el query de `useCategorias` como validar en el backend que la categoría asignada corresponde al tipo correcto del ítem.
- **Reutilizar `Tabla`/`Modal` sin ajustar sus props para tres estructuras de datos distintas podría forzar hacks poco mantenibles** — mitigación: revisar antes de implementar si las props actuales de esos componentes (definidas en la feature 006) son suficientemente flexibles; si no, extenderlas ahí mismo antes de usarlas aquí.