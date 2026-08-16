# 001 · header - spec

**Estado:** hecho.

## Qué hace

Muestra la barra horizontal superior visible en todas las pantallas internas de la aplicación (excepto Login, Recuperar contraseña y Cambiar contraseña). Incluye el logotipo de la empresa con acceso directo al Dashboard, el nombre del sistema ("Enterprise Manager"), un botón para desplegar o colapsar la barra lateral de navegación (sidebar), un ícono de notificaciones con alertas de stock mínimo (productos y materia prima), y un menú de usuario que muestra el nombre y rol de la persona con sesión activa, con acceso a "Información de Usuario" y a "Cerrar sesión". La barra lateral asociada muestra los módulos del sistema disponibles según el rol del usuario autenticado.

## Por qué

Es el punto de entrada y navegación constante de toda la aplicación — sin este componente, ninguna otra feature del roadmap puede integrarse ni probarse en un flujo real, ya que todas dependen de estar envueltas por este layout. Además, es donde vive el control de acceso visual por rol (qué módulos ve cada tipo de usuario) y la primera señal de alerta operativa (stock bajo mínimo), por lo que construirlo primero desbloquea el resto del roadmap definido.

## Criterios de aceptación

- [x] El logotipo y el texto "Enterprise Manager" son visibles en la esquina superior izquierda en toda pantalla interna, y al hacer clic redirigen al Dashboard.
- [x] El botón de despliegue de sidebar muestra u oculta la barra lateral de navegación al hacer clic.
- [x] El sidebar solo muestra los módulos que el rol del usuario autenticado tiene permitido ver — un usuario con rol operador nunca ve en el HTML renderizado las opciones de Usuarios, Caja, Contabilidad ni Configuración Fiscal, sin depender de ocultamiento visual únicamente.
- [x] El ícono de notificaciones muestra un contador visible cuando existe al menos un producto o materia prima con `stock_actual` por debajo de `stock_minimo`, en cualquier sucursal.
- [x] Al hacer clic en notificaciones, se despliega una lista con los ítems en alerta, indicando nombre del ítem y sucursal afectada.
- [x] El menú de usuario muestra el nombre y el rol del usuario autenticado, sin necesidad de recargar la página.
- [x] Desde el menú de usuario es posible acceder a "Información de Usuario" y ejecutar "Cerrar sesión", invalidando la sesión activa.
- [x] El header y el sidebar son responsive: en pantallas pequeñas (por debajo del breakpoint `md` definido en el bloque `@theme` de `index.css`), el sidebar se colapsa por defecto y se despliega solo mediante el botón correspondiente.
- [x] Si la petición de rol de usuario o de alertas de stock aún no ha resuelto, el header y sidebar muestran un estado de carga en vez de contenido vacío o incorrecto.
- [x] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

## Fuera de alcance

- No incluye selector de sucursal — decisión ya establecida: sucursal es una dimensión exclusiva de inventario, no un filtro global de la aplicación.
- No incluye buscador global de productos, clientes o ventas — queda documentado como posible mejora futura, sin entrada aún en el backlog.
- No define el contenido interno de "Información de Usuario" — esa es la feature `015 · Información de Usuario`, este spec solo cubre el punto de acceso desde el menú.
- No define la lógica de expiración/refresh del token JWT — corresponde a la feature `003 · Login` y su manejo de sesión, no al Header en sí.
