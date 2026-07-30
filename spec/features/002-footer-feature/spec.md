# 002 · footer

**Estado:** propuesta

## Qué hace

Muestra una franja delgada en la parte inferior de toda pantalla interna de la aplicación (excepto Login, Recuperar contraseña y Cambiar contraseña), con la versión actual del sistema y el copyright/nombre de la empresa. No incluye enlaces de navegación, redes sociales, ni formularios — es puramente informativo y de bajo protagonismo visual.

## Por qué

Da contexto mínimo de versión útil para soporte y diagnóstico (saber qué versión corre el usuario al reportar un problema), y cumple la expectativa estándar de cierre de página sin restar espacio útil a los módulos operativos, que son el foco real de la aplicación.

## Criterios de aceptación

- [ ] El footer es visible en la parte inferior de toda pantalla interna envuelta por `MainLayout`.
- [ ] Muestra el número de versión del sistema (ej. `v1.0`), leído desde una única fuente configurable (no hardcodeado en múltiples lugares).
- [ ] Muestra el texto de copyright con el nombre de la empresa y el año actual, calculado dinámicamente (no un año fijo escrito a mano).
- [ ] El footer no interfiere con el contenido principal en pantallas pequeñas — no se superpone ni oculta contenido operativo al hacer scroll.
- [ ] El footer respeta la paleta de color definida en `variables.css` (texto discreto, bajo contraste intencional respecto al contenido principal).

## Fuera de alcance

- No incluye enlaces a políticas de privacidad, términos de servicio, ni redes sociales — no aplica a un sistema interno.
- No incluye selector de idioma ni configuración — no aplica, el sistema es monolingüe (español).
- No incluye indicador de estado de conexión/sincronización — quedó como idea descartada en discusión previa; puede evaluarse como backlog si surge la necesidad real.