# 003 · Login — Tareas

- [x] Instalar y configurar `djangorestframework-simplejwt` en `config/settings/base.py`.
- [x] Crear endpoint `POST /api/auth/login/` en `backend/apps/usuarios/views.py`, validando `activo=True`.
- [x] Implementar throttling sobre el endpoint de login usando clases de DRF.
- [x] Crear `frontend/src/context/AuthContext.tsx` con `login()`, `logout()` y estado de sesión.
- [x] Crear `frontend/src/pages/Login/Login.tsx` con el formulario y validación de campos vacíos.
- [x] Crear `frontend/src/pages/Login/Login.module.css` con diseño particular, sin depender de `MainLayout`.
- [x] Crear `frontend/src/api/auth.ts` centralizando la llamada de login.
- [x] Configurar interceptor de Axios en `frontend/src/api/client.ts` para adjuntar el JWT automáticamente. *(el archivo real siempre se llamó `client.ts`/`client.js`, no `axiosClient` — corregido en `plan.md`, era un desajuste preexistente entre este documento y el código)*
- [x] Configurar rutas protegidas en `frontend/src/App.tsx`, redirigiendo a `/login` sin sesión válida.
- [x] Agregar enlace a "Recuperar contraseña" en `Login.tsx`.
- [x] Implementar mensaje de error genérico ante credenciales inválidas (sin distinguir campo).
- [x] Implementar refresh automático de token antes de expiración, en el interceptor de Axios.
- [x] Escribir tests de backend (pytest-django): login exitoso, credenciales incorrectas, usuario inactivo, throttling tras intentos fallidos.
- [x] Escribir tests de frontend (Vitest + RTL): render del formulario, validación de campos vacíos, redirección tras login exitoso.
- [x] Validar contra los criterios de aceptación de `spec.md`.
- [x] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Revisar y ajustar los tiempos de expiración de access/refresh token según necesidad operativa.
- [ ] Revisar el umbral de intentos fallidos del throttling si se detectan falsos positivos o ataques reales.
