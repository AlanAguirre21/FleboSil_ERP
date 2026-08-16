# 005 · Cambiar contraseña — Tareas

- [x] Modificar el endpoint `verificar-codigo` (feature 004) para emitir un token/marca de verificación de un solo uso.
- [x] Crear endpoint `POST /api/auth/cambiar-contrasena/`, validando el token de verificación y la nueva contraseña con `validate_password`.
- [x] Envolver el guardado de contraseña + invalidación de código en `transaction.atomic()`.
- [x] Emitir JWT de sesión normal al completar el cambio exitosamente (login automático).
- [x] Crear `frontend/src/pages/CambiarContrasena/CambiarContrasena.tsx`, con validación de estado de navegación previo.
- [x] Crear `frontend/src/pages/CambiarContrasena/CambiarContrasena.module.css`, diseño particular sin `MainLayout`.
- [x] Extender `frontend/src/api/auth.ts` con `cambiarContrasena()`.
- [x] Implementar validación de coincidencia de contraseña/confirmación en el frontend antes de enviar.
- [x] Implementar redirección automática al Dashboard tras éxito, usando `AuthContext.login()`.
- [x] Implementar redirección a `/recuperar-contrasena` si no existe contexto de verificación válido.
- [x] Escribir tests de backend: token válido + contraseña válida, token inválido/expirado, contraseña que no cumple requisitos, invalidación del código tras uso.
- [x] Escribir tests de frontend: acceso sin contexto previo (redirección), validación de coincidencia, redirección tras éxito.
- [x] Validar contra los criterios de aceptación de `spec.md`.
- [x] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._
