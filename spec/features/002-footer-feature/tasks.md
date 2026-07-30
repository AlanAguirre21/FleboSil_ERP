# 002 · footer — Tareas

- [ ] Crear `frontend/src/config/version.js` con la constante `APP_VERSION`.
- [ ] Crear `frontend/src/components/layout/Footer.jsx`, mostrando versión y copyright con año dinámico.
- [ ] Crear `frontend/src/components/layout/Footer.module.css`, usando variables de `variables.css` para texto discreto.
- [ ] Modificar `frontend/src/components/layout/MainLayout.jsx` para incluir `<Footer />` debajo del `<Outlet />`.
- [ ] Verificar que el layout use scroll interno en el contenido, no en la página completa, para que el footer no quede oculto en pantallas con tablas largas.
- [ ] Escribir test con Vitest + React Testing Library validando que el año de copyright coincide con `new Date().getFullYear()`.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Actualizar `APP_VERSION` en `frontend/src/config/version.js` al valor de la nueva versión liberada.