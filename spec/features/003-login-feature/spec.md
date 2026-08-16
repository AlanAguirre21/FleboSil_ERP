# 003 · Login

**Estado:** hecho.

## Qué hace

Permite el ingreso de un usuario al sistema mediante correo electrónico y contraseña. Valida las credenciales contra la base de datos (contraseña verificada por hash, nunca en texto plano), y en caso de éxito emite un token de sesión (JWT) que se usa para autenticar las siguientes peticiones a la API. Ofrece un enlace a "Recuperar contraseña" para quien no recuerde su contraseña. No incluye opción de autorregistro — las cuentas se crean únicamente por un administrador desde el módulo Personas → Usuarios.

## Por qué

Es el punto de entrada obligatorio a toda la aplicación — ningún otro módulo es accesible sin una sesión válida. Además, es donde se establece la identidad y el rol del usuario que el resto del sistema (Header, Sidebar, y cada endpoint del backend) usa para decidir qué mostrar y qué permitir, por lo que debe construirse antes que cualquier pantalla protegida.

## Criterios de aceptación

- [x] El formulario solicita correo electrónico y contraseña, ambos obligatorios.
- [x] Si las credenciales son correctas, el usuario es redirigido al Dashboard y recibe un token JWT válido almacenado de forma seguraS en el cliente.
- [x] Si las credenciales son incorrectas, se muestra un mensaje de error genérico ("correo o contraseña incorrectos"), sin indicar cuál de los dos campos falló — para no dar pistas útiles a un intento de acceso no autorizado.
- [x] Si el usuario está marcado como `activo = false`, el acceso se rechaza con un mensaje claro, aunque la contraseña sea correcta.
- [x] Existe un enlace visible a "Recuperar contraseña".
- [x] No existe ningún enlace ni formulario de autorregistro en esta pantalla.
- [x] Las contraseñas nunca se transmiten ni se almacenan en texto plano — se validan mediante hash tanto en el envío (HTTPS) como en el almacenamiento (hashing de Django).
- [x] Tras múltiples intentos fallidos consecutivos (a definir, ej. 5), el sistema aplica una restricción temporal antes de permitir un nuevo intento, para mitigar ataques de fuerza bruta.
- [x] El formulario es responsive y utilizable correctamente en pantallas pequeñas.
- [x] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

## Fuera de alcance

- No incluye creación de cuentas (autorregistro) — corresponde exclusivamente al módulo `012 · Personas`, sección Usuarios.
- No incluye la lógica de "Recuperar contraseña" ni "Cambiar contraseña" — son las features `004` y `005` respectivamente.
- No incluye autenticación de dos factores (2FA) — quedó documentada como idea en el backlog, no incluida en esta iteración.
- No define el layout del Header/Sidebar — el Login no usa `MainLayout`, tiene diseño particular propio, según lo establecido en la spec general.
