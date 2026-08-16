# 015 · Información de Usuario

**Estado:** propuesta

## Qué hace

Permite a un usuario autenticado consultar y editar su propia información básica (nombre de usuario, email, teléfono si aplica), con un modal de confirmación final ("¿Estás seguro?") antes de guardar los cambios. No permite cambiar la contraseña desde aquí — ese flujo sigue exclusivamente a través de `004 · Recuperar contraseña` / `005 · Cambiar contraseña`. No permite cambiar el propio rol ni el estado `activo`.

## Por qué

Cierra la necesidad básica de autogestión de cuenta sin depender del admin para correcciones simples (ej. un usuario que se equivocó al capturar su correo, o quiere actualizarlo). Se separa deliberadamente del CRUD administrativo de Usuarios (`008 · Personas`), que gestiona cuentas de terceros, mientras que esta feature gestiona exclusivamente la propia cuenta del usuario autenticado.

## Criterios de aceptación

- [ ] Un usuario autenticado puede acceder a esta pantalla desde el menú de usuario en el Header, como ya se definió en `001`.
- [ ] Se muestran los datos actuales del usuario: nombre de usuario, email, y su rol (rol de solo lectura, no editable desde aquí).
- [ ] El usuario puede modificar nombre de usuario y email desde un formulario de edición.
- [ ] Al intentar guardar cambios, se muestra un modal de confirmación con el texto "¿Estás seguro?" antes de aplicar la actualización.
- [ ] Si el usuario cancela en el modal de confirmación, los cambios no se guardan y el formulario permanece editable con los valores modificados (no se pierden ni se revierten automáticamente).
- [ ] Si el usuario confirma, los cambios se guardan y se muestra una confirmación visual de éxito.
- [ ] Un usuario no puede editar aquí su propio rol, su estado `activo`, ni su contraseña — ninguno de estos campos aparece como editable en este formulario.
- [ ] El backend rechaza cualquier intento de modificar `rol` o `activo` a través de este endpoint específico, incluso si se envían esos campos manipulando la petición directamente.
- [ ] Un usuario solo puede editar su propia información — el backend valida que el `usuario_id` de la petición coincida con el usuario autenticado del token, nunca permite editar la información de otro usuario desde este endpoint.
- [ ] Si el nuevo email o nombre de usuario ya está en uso por otro usuario del sistema, se rechaza con un mensaje claro antes de guardar.
- [ ] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

## Fuera de alcance

- No incluye cambio de contraseña — corresponde exclusivamente a `004`/`005`.
- No incluye edición de rol o estado de otros usuarios — corresponde a `008 · Personas`, exclusivo de admin.
- No incluye historial de cambios de esta información (auditoría de ediciones de perfil) — no contemplado como necesidad actual del proyecto.