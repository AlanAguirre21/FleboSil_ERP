# 004 · Recuperar contraseña — Tareas

- [ ] Crear modelo `CodigoRecuperacion` en `backend/apps/usuarios/models.py` y su migración correspondiente.
- [ ] Crear endpoint `POST /api/auth/recuperar/`, con mensaje de respuesta idéntico exista o no el correo.
- [ ] Configurar el envío de correo (SMTP) en `config/settings/production.py`, con SPF/DKIM verificados en el dominio.
- [ ] Crear endpoint `POST /api/auth/verificar-codigo/`, validando vigencia y coincidencia del código.
- [ ] Implementar throttling por correo destino en ambos endpoints.
- [ ] Crear `frontend/src/pages/RecuperarContrasena/RecuperarContrasena.jsx` con los dos pasos (correo, código).
- [ ] Crear `frontend/src/pages/RecuperarContrasena/RecuperarContrasena.module.css`, diseño particular sin `MainLayout`.
- [ ] Extender `frontend/src/api/auth.js` con `solicitarRecuperacion()` y `verificarCodigo()`.
- [ ] Implementar opción de reenviar código, invalidando el anterior.
- [ ] Implementar redirección a `/cambiar-contrasena` tras verificación exitosa, pasando el correo validado por estado de navegación.
- [ ] Escribir tests de backend: correo existente, correo inexistente (misma respuesta), código correcto, código expirado, código incorrecto, throttling activado.
- [ ] Escribir tests de frontend: render de ambos pasos, manejo de reenvío, redirección tras éxito.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Verificar que el proveedor SMTP configurado sigue activo y con SPF/DKIM correctamente firmados.
- [ ] Revisar logs de intentos de envío fallidos periódicamente.