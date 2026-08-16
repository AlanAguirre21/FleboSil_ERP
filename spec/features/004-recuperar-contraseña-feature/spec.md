# 004 · Recuperar contraseña

**Estado:** hecho.

## Qué hace

Permite a un usuario iniciar el proceso de recuperación de su contraseña ingresando su correo electrónico. El sistema envía un correo con un código de 6 dígitos generado aleatoriamente, válido por tiempo limitado. Si el usuario ingresa el código correcto, se le redirige a "Cambiar contraseña". Se muestra retroalimentación clara sobre si el correo fue enviado, y se permite reenviar un nuevo código si el primero expiró o no llegó.

## Por qué

Es el mecanismo de autoservicio para que un usuario recupere acceso sin depender de que el administrador le reinicie la contraseña manualmente — reduce fricción operativa, especialmente relevante en un equipo pequeño donde el admin no siempre está disponible de inmediato.

## Criterios de aceptación

- [x] El formulario solicita únicamente el correo electrónico.
- [x] Si el correo existe en el sistema, se envía un código de 6 dígitos y se muestra un mensaje confirmando el envío.
- [x] Si el correo no existe, se muestra el mismo mensaje de confirmación genérico que si sí existiera — para no revelar qué correos están registrados en el sistema.
- [x] El código enviado tiene una vigencia limitada (ej. 10-15 minutos), pasada la cual deja de ser válido.
- [x] Si el código ingresado es incorrecto, se muestra un mensaje de error sin bloquear permanentemente al usuario.
- [x] Existe una opción para reenviar un nuevo código, invalidando cualquier código anterior emitido para ese mismo correo.
- [x] Al ingresar el código correcto y vigente, el usuario es redirigido a "Cambiar contraseña" con el contexto (correo) ya validado.
- [x] El proceso aplica un límite de solicitudes por correo en un periodo de tiempo, para evitar abuso del envío de correos (spam hacia el propio usuario o hacia terceros si se usa un correo ajeno).
- [x] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

## Fuera de alcance

- No incluye el formulario de cambio de contraseña en sí — corresponde a la feature `005 · Cambiar contraseña`.
- No incluye recuperación por SMS ni otro
