# 007 · Catálogo — Tareas

- [x] Crear modelo `Categoria` en `backend/apps/catalogo/models.py` (con campo `tipo`) y su migración.
- [x] Crear modelo `Producto` con `sku` único y campos monetarios como `Decimal`.
- [x] Crear modelo `MateriaPrima`, con FK requerida a `Categoria`. *(`proveedor_principal_id` no se declara en esta feature — ver nota en `plan.md`; queda para que `008 · Personas` la agregue con `AddField` una vez exista `Proveedor`)*
- [x] Aplicar migración `0002` (renombra `activo_*`→`activo` y `precio_unitario`→`precio_venta`, agrega `Categoria.tipo` y `MateriaPrima.categoria` con backfill de datos existentes).
- [x] Crear serializers y ViewSets de los tres modelos, reutilizando la clase de permisos de `006 · Sucursales`.
- [x] Implementar validación de unicidad de `sku` en el serializer de `Producto`.
- [x] Implementar soft delete en los tres ViewSets.
- [x] Registrar rutas de `Categoria`, `Producto` y `MateriaPrima` en el router principal.
- [x] Crear `frontend/src/api/catalogo.ts` con funciones CRUD de los tres tipos.
- [x] Crear `frontend/src/hooks/useCategorias.ts`, `useProductos.ts`, `useMateriaPrima.ts`.
- [x] Crear `frontend/src/pages/Catalogo/Catalogo.tsx` con selector de pestañas.
- [x] Implementar formularios de alta/edición por tipo dentro del `Modal` reutilizable.
- [x] Implementar filtrado de categorías por `tipo` en los formularios de Producto y MateriaPrima.
- [x] Ocultar botones de escritura para rol operador.
- [x] Agregar la ruta `/catalogo` en `App.tsx`.
- [x] Agregar el módulo "Catálogo" al diccionario "módulo → roles permitidos". *(ya existía en `core/modules.py` desde antes de esta feature)*
- [x] Escribir tests de backend: unicidad de SKU, rechazo de escritura para operador, soft delete, validación de tipo de categoría contra tipo de ítem.
- [x] Escribir tests de frontend: cambio entre pestañas, ocultamiento de botones para operador, filtrado correcto de categorías en el formulario.
- [x] Validar contra los criterios de aceptación de `spec.md`.
- [x] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Reactivación (categorías, productos, materia prima)

- [x] Agregar acción `reactivar` a `CategoriaViewSet`, `ProductoViewSet` y `MateriaPrimaViewSet`, sin historial ni revalidación de unicidad.
- [x] Escribir tests de backend: reactivar exitoso (admin), reactivar un registro ya activo (400), operador no puede reactivar (403), por cada una de las tres entidades.
- [x] Agregar `reactivarCategoria`/`reactivarProducto`/`reactivarMateriaPrima` a `frontend/src/api/catalogo.ts`.
- [x] Agregar `useReactivarCategoria`/`useReactivarProducto`/`useReactivarMateriaPrima` a los hooks correspondientes.
- [x] Agregar botón "Reactivar" (solo en filas inactivas) y modal de confirmación por pestaña en `Catalogo.tsx`.
- [x] Escribir tests de frontend: botón "Reactivar" visible solo para admin y solo en filas inactivas; confirmar reactivación llama al hook con el id correcto.
- [x] Validar contra los nuevos criterios de aceptación de `spec.md` ("Reactivación de categorías, productos y materia prima").

## Mantenimiento (checklist recurrente)

_Pasos a repetir si se agrega un nuevo tipo de catálogo en el futuro (ej. servicios)._

- [ ] Evaluar si el nuevo tipo encaja como pestaña adicional en `Catalogo.tsx` o requiere su propia feature/módulo.