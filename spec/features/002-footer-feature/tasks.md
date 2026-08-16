# 002 · footer — Tareas

- [x] Crear `frontend/src/config/version.ts` con la constante `APP_VERSION`.
- [x] Crear `frontend/src/components/layout/Footer.tsx`, mostrando versión y copyright con año dinámico.
- [x] Crear `frontend/src/components/layout/Footer.module.css`, con `@reference` a `index.css` y clases de Tailwind compuestas vía `@apply` para el texto discreto.
- [x] Modificar `frontend/src/components/layout/MainLayout.tsx` para incluir `<Footer />` debajo del `<Outlet />`.
- [x] Verificar que el layout use scroll interno en el contenido, no en la página completa, para que el footer no quede oculto en pantallas con tablas largas.
- [x] Escribir test con Vitest + React Testing Library validando que el año de copyright coincide con `new Date().getFullYear()`.
- [x] Validar contra los criterios de aceptación de `spec.md`.
- [x] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Actualizar `APP_VERSION` en `frontend/src/config/version.ts` al valor de la nueva versión liberada.
