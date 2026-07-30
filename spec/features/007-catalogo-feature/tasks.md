# 007 · Catálogo — Tareas

- [ ] Crear modelo `Categoria` en `backend/apps/catalogo/models.py` (con campo `tipo`) y su migración.
- [ ] Crear modelo `Producto` con `sku` único y campos monetarios como `Decimal`.
- [ ] Crear modelo `MateriaPrima`, con `proveedor_principal_id` como FK nullable hacia `Proveedores`.
- [ ] Aplicar migraciones en el orden correcto, validando que no fallen por la FK diferida.
- [ ] Crear serializers y ViewSets de los tres modelos, reutilizando la clase de permisos de `006 · Sucursales`.
- [ ] Implementar validación de unicidad de `sku` en el serializer de `Producto`.
- [ ] Implementar soft delete en los tres ViewSets.
- [ ] Registrar rutas de `Categoria`, `Producto` y `MateriaPrima` en el router principal.
- [ ] Crear `frontend/src/api/catalogo.js` con funciones CRUD de los tres tipos.
- [ ] Crear `frontend/src/hooks/useCategorias.js`, `useProductos.js`, `useMateriaPrima.js`.
- [ ] Crear `frontend/src/pages/Catalogo/Catalogo.jsx` con selector de pestañas.
- [ ] Implementar formularios de alta/edición por tipo dentro del `Modal` reutilizable.
- [ ] Implementar filtrado de categorías por `tipo` en los formularios de Producto y MateriaPrima.
- [ ] Ocultar botones de escritura para rol operador.
- [ ] Agregar la ruta `/catalogo` en `App.jsx`.
- [ ] Agregar el módulo "Catálogo" al diccionario "módulo → roles permitidos".
- [ ] Escribir tests de backend: unicidad de SKU, rechazo de escritura para operador, soft delete, validación de tipo de categoría contra tipo de ítem.
- [ ] Escribir tests de frontend: cambio entre pestañas, ocultamiento de botones para operador, filtrado correcto de categorías en el formulario.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Pasos a repetir si se agrega un nuevo tipo de catálogo en el futuro (ej. servicios)._

- [ ] Evaluar si el nuevo tipo encaja como pestaña adicional en `Catalogo.jsx` o requiere su propia feature/módulo.