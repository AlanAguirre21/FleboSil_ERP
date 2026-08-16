# 006 · Sucursales — Tareas

- [x] Crear modelo `Sucursal` en `backend/apps/sucursales/models.py` y su migración.
- [x] Crear `SucursalSerializer` en `backend/apps/sucursales/serializers.py`.
- [x] Crear `SucursalViewSet` con permisos diferenciados por método HTTP (lectura vs. escritura).
- [x] Implementar soft delete (`activo=False`) sobreescribiendo el método de borrado del ViewSet.
- [x] Registrar rutas de `Sucursal` en el router principal de la API. *(el router de `apps/sucursales/urls.py` estaba construido pero nunca se incluyó en `config/urls.py` — `/api/sucursales/` devolvía 404 pese a esta tarea estar marcada como hecha; corregido durante la migración a TypeScript al verificar el CRUD en vivo)*
- [x] Crear componente común `frontend/src/components/common/Tabla.tsx` + `.module.css`, con columnas configurables vía props.
- [x] Crear componente común `frontend/src/components/common/Modal.tsx` + `.module.css`.
- [x] Crear componente común `frontend/src/components/common/BotonPrimario.tsx` + `.module.css`.
- [x] Crear `frontend/src/api/sucursales.ts` con funciones CRUD.
- [x] Crear `frontend/src/hooks/useSucursales.ts` con React Query.
- [x] Crear `frontend/src/pages/Sucursales/Sucursales.tsx`, mostrando tabla y ocultando acciones de escritura si el rol no es admin.
- [x] Implementar el formulario de alta/edición dentro del `Modal` reutilizable.
- [x] Agregar la ruta `/sucursales` en `frontend/src/App.tsx`, protegida y dentro de `MainLayout`.
- [x] Agregar el módulo "Sucursales" al diccionario "módulo → roles permitidos" definido en la feature 001.
- [x] Escribir tests de backend: creación/edición solo por admin, rechazo de escritura por rol operador, soft delete en vez de borrado físico.
- [x] Escribir tests de frontend: ocultamiento de botones de acción para rol operador, render correcto de la tabla.
- [x] Validar contra los criterios de aceptación (versión original) de `spec.md`.
- [x] Mover la feature a "Hecho" en `../../constitution/roadmap.md`. *(revertido a "Siguiente" al agregar la extensión de reactivación — ver abajo)*

## Extensión: reactivación, nombre duplicado, historial

- [x] Crear modelo `HistorialEstadoSucursal` en `backend/apps/sucursales/models.py` y su migración.
- [x] Crear función de validación compartida `validar_nombre_disponible(nombre, ubicacion, excluir_pk=None)` en `apps/sucursales/validators.py`.
- [x] Invocar la validación desde `SucursalSerializer.validate()`, cubriendo creación y edición/renombrado.
- [x] Modificar `perform_destroy()` para crear el `HistorialEstadoSucursal` correspondiente (`estado_anterior=True`, `estado_nuevo=False`) dentro de la misma transacción. *(idempotente: desactivar una sucursal ya inactiva no crea un historial falso)*
- [x] Crear la acción `POST /api/sucursales/{id}/reactivar/` (solo admin), con validación de nombre duplicado + `activo=True` + `HistorialEstadoSucursal` (`estado_anterior=False`, `estado_nuevo=True`), todo dentro de `transaction.atomic()`.
- [x] Usar `select_for_update()` sobre las filas candidatas durante la validación de nombre duplicado, para evitar condiciones de carrera entre registros/reactivaciones simultáneas.
- [x] Extender `frontend/src/api/sucursales.ts` con `reactivarSucursal(id)`.
- [x] Extender `frontend/src/hooks/useSucursales.ts` con `useReactivarSucursal()`.
- [x] Agregar el botón "Reactivar" (con modal de confirmación) en `Sucursales.tsx` para sucursales inactivas, visible solo para admin.
- [x] Verificar que los errores de nombre duplicado (clave `nombre_sucursal`) se muestren correctamente en el formulario existente, sin necesitar un nuevo camino de error en el frontend.
- [x] Escribir tests de backend: reactivación exitosa; rechazo de reactivación por rol operador; rechazo de reactivación de una sucursal ya activa; rechazo de creación/reactivación por nombre duplicado con una sucursal activa (sin importar ubicación); aceptación de nombre duplicado cuando la ubicación difiere y el original está inactivo; rechazo cuando la ubicación coincide aunque el original esté inactivo (incluyendo el caso de dos ubicaciones vacías); la misma validación aplicada al renombrar una sucursal existente; creación de `HistorialEstadoSucursal` en cada cambio de estado (ambos sentidos); idempotencia de `perform_destroy` sin duplicar historial. *(20/20 tests pasan, suite completa del backend 45/45, `ruff` limpio)*
- [x] Escribir tests de frontend: botón "Reactivar" visible solo para admin y solo en filas inactivas, confirmación antes de reactivar con el nombre correcto, llamada al hook al confirmar, mensaje de error de nombre duplicado mostrado en el formulario. *(31/31 tests pasan, `tsc`/lint/build limpios)*
- [x] Validar contra los criterios de aceptación actualizados de `spec.md` — verificado en vivo contra el backend real: reactivación exitosa (Sucursal Sur), rechazo de nombre duplicado activo ("Matriz"), aceptación de nombre duplicado con ubicación distinta y original inactivo ("Sucursal Norte"), registro correcto en `HistorialEstadoSucursal`, sin errores de consola.
- [x] Mover la feature de nuevo a "Hecho" en `../../constitution/roadmap.md`. *(el bloqueo de `MovimientoInventario` y la denormalización en CFDI quedan fuera de esta entrada — ver sección "Pendiente" abajo, son código de features que aún no existen)*

## Pendiente (no bloquea el resto de la extensión)

- [ ] Cuando se escriban los `plan.md` de `009 · Inventario`, `010 · Compras`, `011 · Ventas` y `012 · Producción`, cross-referenciar ahí la obligación de validar `sucursal.activo` antes de crear cualquier `MovimientoInventario` (documentada en el `plan.md` de esta feature).

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._
