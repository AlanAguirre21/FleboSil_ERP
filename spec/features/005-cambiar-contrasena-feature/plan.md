# 005 · cambiar-contraseña — Plan

## Enfoque

Backend: endpoint que recibe el correo ya validado (mediante el token/marca de verificación emitido en la feature 004), la nueva contraseña, y su confirmación; aplica las validaciones de Django (`validate_password`) antes de guardar el hash. Frontend: pantalla independiente (sin `MainLayout`), que solo se renderiza si existe el estado de navegación con el correo validado; de lo contrario redirige a Recuperar contraseña.

## Implementación

1. Backend — en el endpoint `verificar-codigo` de la feature 004, emitir un token de un solo uso de corta duración (ej. JWT efímero o registro `usado=False` temporal en `CodigoRecuperacion`) que se exige como prueba en este paso.
2. Backend — crear endpoint `POST /api/auth/cambiar-contrasena/` que recibe ese token + nueva contraseña + confirmación, valida con `django.contrib.auth.password_validation.validate_password`, guarda el hash, marca el `CodigoRecuperacion` como `usado=True` definitivamente, y emite el JWT de sesión normal (login automático).
3. Frontend — crear `frontend/src/pages/CambiarContrasena/CambiarContrasena.jsx`, leyendo el estado de navegación (correo/token) pasado desde la feature 004; si no existe, redirige a `/recuperar-contrasena`.
4. Frontend — crear `frontend/src/pages/CambiarContrasena/CambiarContrasena.module.css`, diseño particular sin `MainLayout`.
5. Frontend — extender `frontend/src/api/auth.js` con `cambiarContrasena()`.
6. Frontend — al recibir respuesta exitosa, usar `AuthContext.login()` (o equivalente) para guardar el JWT recibido y redirigir directo al Dashboard, sin pasar de nuevo por Login.

## Decisiones

- **El token de verificación de la feature 004 se reutiliza como prueba de identidad aquí, en vez de pedir el código de 6 dígitos de nuevo** — evita fricción innecesaria; el usuario ya demostró su identidad en el paso anterior, no debe repetirlo.
- **Validación de contraseña con las herramientas nativas de Django (`validate_password`)** — se descarta escribir reglas de validación propias, ya que Django ya cubre longitud mínima, similitud con datos del usuario, contraseñas comunes, etc., de forma probada.
- **Login automático tras el cambio exitoso** — se descarta redirigir a la pantalla de Login pidiendo que el usuario vuelva a escribir sus credenciales, priorizando menor fricción sobre una validación adicional que no aporta seguridad real (el usuario ya demostró identidad dos veces: código + nueva contraseña).
- **Invalidación permanente del código de recuperación tras el cambio, sin esperar su expiración natural** — cierra la ventana de uso indebido si alguien más obtuviera el mismo código por error o filtración.

## Riesgos

- **Acceso directo a la URL de esta pantalla sin haber pasado por la verificación de código, si el estado de navegación se maneja de forma insegura** — mitigación: validar también en el backend que el token de verificación es legítimo y no expirado, nunca confiar solo en que el frontend controló la navegación correctamente.
- **Confirmación de contraseña que no coincide, detectada solo después de enviar al backend, generando mala experiencia** — mitigación: validar la coincidencia en el frontend antes de enviar la petición, además de la validación de backend como respaldo.
- **Reutilización accidental del token de verificación si no se invalida atómicamente junto con el guardado de la nueva contraseña** — mitigación: envolver el guardado de contraseña + invalidación del código en una misma transacción (`transaction.atomic()`), consistente con el patrón ya establecido en el tech-stack para operaciones que deben ser todo-o-nada.