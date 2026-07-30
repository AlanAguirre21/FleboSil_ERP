# 015 · Información de Usuario — Tareas

- [ ] Extender o crear la vista `/api/usuarios/me/` para soportar `PATCH`, además del `GET` ya usado desde `001`.
- [ ] Crear `UsuarioPropioSerializer`, exponiendo solo `nombre_usuario` y `email` como editables.
- [ ] Forzar en la vista que el `usuario_id` editado sea siempre `request.user.id`.
- [ ] Implementar validación de unicidad de `nombre_usuario`/`email` excluyendo al propio usuario.
- [ ] Crear `frontend/src/pages/InformacionUsuario/InformacionUsuario.jsx`, precargando datos desde `useUsuarioActual`.
- [ ] Crear el formulario de edición con rol mostrado como texto no editable.
- [ ] Integrar el `Modal` de confirmación "¿Estás seguro?" antes de guardar.
- [ ] Extender `frontend/src/api/` con `actualizarMiInformacion()`.
- [ ] Invalidar la cache de `useUsuarioActual` tras actualización exitosa.
- [ ] Agregar la ruta `/mi-informacion` en `App.jsx`, enlazada desde el menú de usuario del Header.
- [ ] Escribir tests de backend: edición exitosa de nombre/email, rechazo de intento de modificar rol/activo vía payload manipulado, rechazo de edición de otro usuario, validación de unicidad excluyendo al propio usuario.
- [ ] Escribir tests de frontend: apertura del modal de confirmación, cancelación sin guardar cambios, actualización del Header tras confirmar.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Pasos a repetir si se agrega un nuevo campo editable al modelo `Usuario`._

- [ ] Evaluar si el nuevo campo debe ser editable por el propio usuario aquí, por el admin en `008`, o por ambos, y actualizar el serializer correspondiente.
