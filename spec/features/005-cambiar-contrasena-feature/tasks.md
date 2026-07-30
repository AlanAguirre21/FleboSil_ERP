# 005 · Cambiar contraseña — Tareas

- [ ] Modificar el endpoint `verificar-codigo` (feature 004) para emitir un token/marca de verificación de un solo uso.
- [ ] Crear endpoint `POST /api/auth/cambiar-contrasena/`, validando el token de verificación y la nueva contraseña con `validate_password`.
- [ ] Envolver el guardado de contraseña + invalidación de código en `transaction.atomic()`.
- [ ] Emitir JWT de sesión normal al completar el cambio exitosamente (login automático).
- [ ] Crear `frontend/src/pages/CambiarContrasena/CambiarContrasena.jsx`, con validación de estado de navegación previo.
- [ ] Crear `frontend/src/pages/CambiarContrasena/CambiarContrasena.module.css`, diseño particular sin `MainLayout`.
- [ ] Extender `frontend/src/api/auth.js` con `cambiarContrasena()`.
- [ ] Implementar validación de coincidencia de contraseña/confirmación en el frontend antes de enviar.
- [ ] Implementar redirección automática al Dashboard tras éxito, usando `AuthContext.login()`.
- [ ] Implementar redirección a `/recuperar-contrasena` si no existe contexto de verificación válido.
- [ ] Escribir tests de backend: token válido + contraseña válida, token inválido/expirado, contraseña que no cumple requisitos, invalidación del código tras uso.
- [ ] Escribir tests de frontend: acceso sin contexto previo (redirección), validación de coincidencia, redirección tras éxito.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._