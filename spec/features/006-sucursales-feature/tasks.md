# 006 · Sucursales — Tareas

- [ ] Crear modelo `Sucursal` en `backend/apps/sucursales/models.py` y su migración.
- [ ] Crear `SucursalSerializer` en `backend/apps/sucursales/serializers.py`.
- [ ] Crear `SucursalViewSet` con permisos diferenciados por método HTTP (lectura vs. escritura).
- [ ] Implementar soft delete (`activo=False`) sobreescribiendo el método de borrado del ViewSet.
- [ ] Registrar rutas de `Sucursal` en el router principal de la API.
- [ ] Crear componente común `frontend/src/components/common/Tabla.jsx` + `.module.css`, con columnas configurables vía props.
- [ ] Crear componente común `frontend/src/components/common/Modal.jsx` + `.module.css`.
- [ ] Crear componente común `frontend/src/components/common/BotonPrimario.jsx` + `.module.css`.
- [ ] Crear `frontend/src/api/sucursales.js` con funciones CRUD.
- [ ] Crear `frontend/src/hooks/useSucursales.js` con React Query.
- [ ] Crear `frontend/src/pages/Sucursales/Sucursales.jsx`, mostrando tabla y ocultando acciones de escritura si el rol no es admin.
- [ ] Implementar el formulario de alta/edición dentro del `Modal` reutilizable.
- [ ] Agregar la ruta `/sucursales` en `frontend/src/App.jsx`, protegida y dentro de `MainLayout`.
- [ ] Agregar el módulo "Sucursales" al diccionario "módulo → roles permitidos" definido en la feature 001.
- [ ] Escribir tests de backend: creación/edición solo por admin, rechazo de escritura por rol operador, soft delete en vez de borrado físico.
- [ ] Escribir tests de frontend: ocultamiento de botones de acción para rol operador, render correcto de la tabla.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._
