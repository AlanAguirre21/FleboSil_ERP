# 003 · login — Plan

## Enfoque

Backend: endpoint de autenticación vía `djangorestframework-simplejwt`, que valida credenciales contra el modelo `Usuarios` (extendiendo o integrando con `django.contrib.auth`) y emite un par de tokens (access + refresh). Frontend: pantalla `Login.jsx` independiente del `MainLayout` (diseño propio, sin Header/Sidebar), con manejo de estado del formulario, llamada a la API, y almacenamiento del token en un contexto de autenticación de React que envuelve toda la aplicación.

## Implementación

1. Backend — configurar `djangorestframework-simplejwt` en `config/settings/base.py` (tiempos de expiración de access/refresh token).
2. Backend — crear endpoint `POST /api/auth/login/` en `backend/apps/usuarios/views.py`, validando `activo=True` además de la contraseña antes de emitir el token.
3. Backend — implementar throttling (limitación de intentos) usando las clases de throttle de DRF sobre el endpoint de login, para mitigar fuerza bruta.
4. Frontend — crear `frontend/src/context/AuthContext.jsx`, exponiendo `login()`, `logout()`, y el estado de sesión actual a toda la aplicación.
5. Frontend — crear `frontend/src/pages/Login/Login.jsx` con el formulario (correo, contraseña), validación básica de campos vacíos, y llamada a `AuthContext.login()`.
6. Frontend — crear `frontend/src/pages/Login/Login.module.css` con diseño particular (no reutiliza `MainLayout`).
7. Frontend — en `frontend/src/api/auth.js`, centralizar la llamada `POST /api/auth/login/` y el manejo de la respuesta (token + datos básicos de usuario).
8. Frontend — configurar interceptor de Axios en `frontend/src/api/axiosClient.js` para adjuntar el JWT automáticamente en cada petición subsecuente.
9. Frontend — configurar rutas protegidas en `frontend/src/App.jsx`: si no hay sesión válida, cualquier ruta protegida redirige a `/login`.
10. Frontend — agregar enlace a "Recuperar contraseña" en `Login.jsx`, apuntando a la ruta de la feature `004`.

## Decisiones

- **JWT en vez de sesiones tradicionales de Django** — ya establecido en la arquitectura general por la separación backend/frontend; se mantiene consistente aquí en vez de reconsiderar sesiones basadas en cookies.
- **Throttling a nivel de backend (DRF), no solo bloqueo visual en frontend** — un atacante puede saltarse cualquier límite implementado solo en el cliente llamando la API directamente; la protección real debe vivir en el servidor.
- **Mensaje de error genérico ante credenciales inválidas** — se descarta indicar específicamente "correo no encontrado" vs. "contraseña incorrecta", porque esa distinción facilita a un atacante enumerar correos válidos registrados en el sistema.
- **Login como pantalla independiente sin `MainLayout`** — coherente con la spec general del proyecto, que define diseño particular para los puntos 1 al 3 (con logotipo propio), distinto del resto de ventanas con header/footer estándar.

## Riesgos

- **Almacenamiento inseguro del token en el cliente (ej. `localStorage` expuesto a ataques XSS)** — mitigación: evaluar `httpOnly cookies` para el refresh token si el riesgo se considera relevante para el volumen de datos financieros que maneja el sistema; como mínimo, sanitizar cualquier entrada de usuario en el frontend para reducir superficie de XSS.
- **Expiración de token durante una operación larga (ej. registrar una venta con muchos productos), causando pérdida de datos no guardados** — mitigación: implementar refresh automático de token en el interceptor de Axios antes de que expire, de forma transparente para el usuario.
- **Confusión entre "usuario inactivo" y "credenciales incorrectas" si no se prueban ambos casos por separado** — mitigación: cubrir explícitamente ambos escenarios en los tests de backend, no solo el caso feliz.