# 004 · Recuperar contraseña — Tareas

- [x] Crear modelo `CodigoRecuperacion` en `backend/apps/usuarios/models.py` y su migración correspondiente.
- [x] Crear endpoint `POST /api/auth/recuperar/`, con mensaje de respuesta idéntico exista o no el correo.
- [x] Configurar el envío de correo (SMTP) en `config/settings/production.py`, con SPF/DKIM verificados en el dominio.
- [x] Crear endpoint `POST /api/auth/verificar-codigo/`, validando vigencia y coincidencia del código.
- [x] Implementar throttling por correo destino en ambos endpoints.
- [x] Crear `frontend/src/pages/RecuperarContrasena/RecuperarContrasena.tsx` con los dos pasos (correo, código).
- [x] Crear `frontend/src/pages/RecuperarContrasena/RecuperarContrasena.module.css`, diseño particular sin `MainLayout`.
- [x] Extender `frontend/src/api/auth.ts` con `solicitarRecuperacion()` y `verificarCodigo()`.
- [x] Implementar opción de reenviar código, invalidando el anterior.
- [x] Implementar redirección a `/cambiar-contrasena` tras verificación exitosa, pasando el correo validado por estado de navegación.
- [x] Escribir tests de backend: correo existente, correo inexistente (misma respuesta), código correcto, código expirado, código incorrecto, throttling activado.
- [x] Escribir tests de frontend: render de ambos pasos, manejo de reenvío, redirección tras éxito.
- [x] Validar contra los criterios de aceptación de `spec.md`.
- [x] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Verificar que el proveedor SMTP configurado sigue activo y con SPF/DKIM correctamente firmados.
- [ ] Revisar logs de intentos de envío fallidos periódicamente.
