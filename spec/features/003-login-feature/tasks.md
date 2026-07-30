# 003 · Login — Tareas

- [ ] Instalar y configurar `djangorestframework-simplejwt` en `config/settings/base.py`.
- [ ] Crear endpoint `POST /api/auth/login/` en `backend/apps/usuarios/views.py`, validando `activo=True`.
- [ ] Implementar throttling sobre el endpoint de login usando clases de DRF.
- [ ] Crear `frontend/src/context/AuthContext.jsx` con `login()`, `logout()` y estado de sesión.
- [ ] Crear `frontend/src/pages/Login/Login.jsx` con el formulario y validación de campos vacíos.
- [ ] Crear `frontend/src/pages/Login/Login.module.css` con diseño particular, sin depender de `MainLayout`.
- [ ] Crear `frontend/src/api/auth.js` centralizando la llamada de login.
- [ ] Configurar interceptor de Axios en `frontend/src/api/axiosClient.js` para adjuntar el JWT automáticamente.
- [ ] Configurar rutas protegidas en `frontend/src/App.jsx`, redirigiendo a `/login` sin sesión válida.
- [ ] Agregar enlace a "Recuperar contraseña" en `Login.jsx`.
- [ ] Implementar mensaje de error genérico ante credenciales inválidas (sin distinguir campo).
- [ ] Implementar refresh automático de token antes de expiración, en el interceptor de Axios.
- [ ] Escribir tests de backend (pytest-django): login exitoso, credenciales incorrectas, usuario inactivo, throttling tras intentos fallidos.
- [ ] Escribir tests de frontend (Vitest + RTL): render del formulario, validación de campos vacíos, redirección tras login exitoso.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Revisar y ajustar los tiempos de expiración de access/refresh token según necesidad operativa.
- [ ] Revisar el umbral de intentos fallidos del throttling si se detectan falsos positivos o ataques reales.