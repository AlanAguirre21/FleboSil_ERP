# 015 · informacion-de-usuario — Plan

## Enfoque

Endpoint dedicado y distinto del `UsuarioViewSet` administrativo ya construido en `008 · Personas` — este endpoint (`/api/usuarios/me/`) solo permite que un usuario lea y edite su propio registro, con un serializer restringido que expone únicamente los campos editables por el propio usuario (nunca `rol` ni `activo`). El endpoint `/api/usuarios/me/` ya fue mencionado como fuente de datos para `useUsuarioActual` en el Header (`001`); aquí se completa con soporte de escritura (`PATCH`), que antes solo se usaba en modo lectura.

## Implementación

1. Backend — en `backend/apps/usuarios/views.py`, extender (o crear si no existe) la vista de `me/` para soportar `GET` (ya usado desde `001`) y `PATCH`.
2. Backend — crear `UsuarioPropioSerializer`, distinto del `UsuarioSerializer` administrativo de `008`, exponiendo solo `nombre_usuario`, `email` como campos editables; `rol` y `activo` se muestran de solo lectura o se excluyen del payload de escritura por completo.
3. Backend — en la vista, forzar que el `usuario_id` editado sea siempre `request.user.id`, ignorando cualquier `id` que llegue en el cuerpo de la petición — nunca confiar en un ID enviado por el cliente para esta acción.
4. Backend — validar unicidad de `nombre_usuario` y `email` excluyendo al propio usuario de la comparación (para no rechazar guardar sin cambios reales en esos campos).
5. Frontend — crear `frontend/src/pages/InformacionUsuario/InformacionUsuario.tsx`, precargando los datos desde `useUsuarioActual` (ya existente desde `001`).
6. Frontend — crear el formulario de edición con nombre de usuario y email; rol mostrado como texto no editable.
7. Frontend — al enviar el formulario, abrir el `Modal` de confirmación ("¿Estás seguro?") ya construido como componente común desde `006 · Sucursales`, antes de disparar la petición real.
8. Frontend — extender `frontend/src/api/personas.ts` (o crear `frontend/src/api/usuarioActual.ts` si se prefiere separar del CRUD administrativo) con la función `actualizarMiInformacion()`.
9. Frontend — invalidar la cache de `useUsuarioActual` tras una actualización exitosa, para que el Header refleje el nombre actualizado de inmediato.
10. Frontend — agregar la ruta `/mi-informacion` (o similar) en `App.tsx`, accesible desde el menú de usuario del Header.

## Decisiones

- **Endpoint separado (`/me/`) del `UsuarioViewSet` administrativo, en vez de reutilizar el mismo con permisos condicionales** — evita que un mismo serializer tenga que decidir dinámicamente qué campos son editables según "si el usuario edita su propia cuenta o la de alguien más"; separar los endpoints hace explícito y simple el límite de qué se puede tocar en cada caso.
- **`rol` y `activo` excluidos del serializer de escritura, no solo validados y rechazados en la vista** — si el campo ni siquiera es parte del serializer de escritura, no hay forma de que se filtre por error futuro de mantenimiento; es más seguro que confiar en una validación explícita que alguien podría olvidar mantener.
- **`usuario_id` siempre tomado de `request.user`, nunca del cuerpo de la petición** — previene que un usuario manipule la petición para editar la información de otro usuario cambiando un ID en el payload.
- **Reutilización del componente `Modal` ya existente para la confirmación** — consistente con el principio de mantenimiento centralizado ya aplicado en toda la aplicación desde `006 · Sucursales`.

## Riesgos

- **Si el serializer administrativo de `008 · Personas` y este nuevo `UsuarioPropioSerializer` divergen con el tiempo (ej. se agrega un campo nuevo a `Usuario` y solo se actualiza uno de los dos serializers)** — mitigación: documentar explícitamente en el código que ambos serializers deben revisarse juntos cada vez que se modifique el modelo `Usuario`.
- **Invalidar solo la cache de `useUsuarioActual` podría no reflejar el cambio en otras vistas que también muestran el nombre de usuario (ej. `usuario_id` en historiales de ventas/movimientos)** — mitigación: aceptable como comportamiento esperado, ya que esos historiales muestran el nombre que tenía el usuario al momento de la operación, no necesariamente el actual; documentar esto como decisión, no como bug.
- **Confirmación con modal podría sentirse innecesaria para cambios triviales (ej. corregir una letra en el email)** — mitigación: es un requisito ya explícito de la spec original del proyecto: se mantiene tal cual fue solicitado, sin reinterpretarlo.