# 004 · recuperar-contraseña — Plan

## Enfoque

Backend: modelo temporal para almacenar el código de verificación asociado a un usuario, con expiración controlada por timestamp, y envío del correo mediante el servicio SMTP configurado (ya contemplado en la arquitectura general). Frontend: pantalla independiente (sin `MainLayout`, mismo criterio que Login), en dos pasos visuales — solicitud de correo, y verificación de código — dentro del mismo componente o en dos rutas encadenadas.

## Implementación

1. Backend — crear modelo `CodigoRecuperacion` en `backend/apps/usuarios/models.py`: `usuario_id` (FK), `codigo` (6 dígitos), `expira_en` (datetime), `usado` (booleano).
2. Backend — crear endpoint `POST /api/auth/recuperar/` que recibe el correo, genera el código, lo guarda con expiración, y dispara el envío de correo (Django `send_mail` o backend SMTP configurado). Responde siempre con el mismo mensaje, exista o no el correo.
3. Backend — crear endpoint `POST /api/auth/verificar-codigo/` que recibe correo + código, valida vigencia y coincidencia, y de ser correcto emite un token temporal de un solo uso (o marca el código como validado) para habilitar el cambio de contraseña.
4. Backend — implementar throttling sobre ambos endpoints (limitar solicitudes por correo/IP en un periodo).
5. Frontend — crear `frontend/src/pages/RecuperarContrasena/RecuperarContrasena.jsx`: paso 1 (input de correo + botón enviar), paso 2 (input de 6 dígitos + botón verificar + opción de reenviar).
6. Frontend — crear `frontend/src/api/auth.js` (extendiendo el ya creado en Login) con las funciones `solicitarRecuperacion()` y `verificarCodigo()`.
7. Frontend — al verificar código correctamente, redirigir a `/cambiar-contrasena` pasando el correo validado (vía estado de navegación de React Router, no en la URL visible).

## Decisiones

- **Mensaje de confirmación idéntico exista o no el correo** — mismo principio de seguridad aplicado en Login: no revelar qué correos están registrados, para no facilitar enumeración de usuarios válidos del sistema.
- **Código de un solo uso con expiración corta, en vez de enlace de recuperación con token largo** — se prefiere el código de 6 dígitos porque ya está definido así en la spec general (UX más simple para el usuario, sin depender de que el cliente de correo renderice bien un enlace).
- **Throttling por correo y no solo por IP** — un atacante podría rotar IPs fácilmente; limitar por correo destino previene que se spamee la bandeja de un usuario específico independientemente del origen del ataque.
- **Verificación de código como paso separado del cambio de contraseña real** — mantiene la separación de responsabilidades ya definida en la spec original (features 004 y 005 distintas), en vez de fusionar ambos flujos en una sola pantalla.

## Riesgos

- **El correo de recuperación podría no llegar (filtros de spam, configuración SMTP incorrecta) sin que el usuario tenga forma de saberlo, dado el mensaje genérico** — mitigación: asegurar configuración correcta de SPF/DKIM en el dominio de envío desde el inicio, y loggear en el backend (no expuesto al usuario) cada intento de envío para diagnóstico del administrador.
- **Código interceptado si el correo del usuario está comprometido** — mitigación aceptada como riesgo residual estándar de este mecanismo; se mitiga parcialmente con la expiración corta del código.
- **Abuso del endpoint de recuperación para saturar el servicio de correo (costos o límites del proveedor SMTP)** — mitigación: el throttling ya definido en el paso 4 de implementación.