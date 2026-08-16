# 001 · header — tareas

- [x] Crear `frontend/src/index.css` (si aún no existe desde otra feature) como punto de entrada de Tailwind (`@import "tailwindcss";`), con las variables de color de marca y estado definidas en `tech-stack.md` dentro del bloque `@theme`.
- [x] Crear `frontend/src/components/layout/Header.tsx` con la estructura base: logo enlazado al Dashboard, texto "Enterprise Manager", botón de despliegue de sidebar, ícono de notificaciones, menú de usuario.
- [x] Crear `frontend/src/components/layout/Header.module.css`, con `@reference "../../index.css"` y clases de Tailwind compuestas vía `@apply` sobre los tokens del `@theme` — sin colores hardcodeados.
- [x] Crear `frontend/src/hooks/useUsuarioActual.ts` — hook de React Query que expone `{ nombre, rol }` desde `/api/usuarios/me/`.
- [x] Backend: crear endpoint `GET /api/inventario/alertas/` en `backend/apps/inventario/views.py`, filtrando `stock_actual < stock_minimo` en `InventarioSucursalProducto` y `InventarioSucursalMateriaPrima`.
- [x] Crear `frontend/src/hooks/useAlertasStock.ts` — hook de React Query que consume el endpoint anterior, con `staleTime` configurado (ej. 60s).
- [x] Implementar el dropdown de notificaciones en `Header.tsx`, mostrando nombre del ítem y sucursal afectada por cada alerta.
- [x] Crear `frontend/src/components/layout/Sidebar.tsx`, recibiendo el rol como prop y filtrando el array de módulos antes de renderizar (nunca ocultando con CSS).
- [x] Definir el diccionario "módulo → roles permitidos" como fuente única de verdad, referenciado tanto por `Sidebar.tsx` como por los permisos de DRF en el backend.
- [x] Crear `frontend/src/components/layout/MainLayout.tsx`, combinando `Header` + `Sidebar` + `<Outlet />` de React Router.
- [x] Integrar `MainLayout` en `frontend/src/App.tsx`, envolviendo las rutas autenticadas.
- [x] Implementar estado de carga (skeleton) en `Header`/`Sidebar` mientras `useUsuarioActual` y `useAlertasStock` resuelven.
- [x] Implementar comportamiento responsive: sidebar colapsado por defecto por debajo del breakpoint `md`, desplegable con el botón correspondiente.
- [x] Implementar acciones del menú de usuario: acceso a "Información de Usuario" y "Cerrar sesión" (invalidando el token/sesión).
- [x] Escribir tests con Vitest + React Testing Library para: filtrado de sidebar por rol, render del contador de notificaciones, y navegación del logo al Dashboard.
- [x] Escribir test de backend (pytest-django) para el endpoint `/api/inventario/alertas/`, cubriendo caso con y sin ítems en alerta.
- [x] Actualizar `frontend/src/api/inventario.ts` con la función que consume el nuevo endpoint de alertas, si no se centralizó ya en el paso del hook.
- [x] Validar contra los criterios de aceptación de `spec.md`.
- [x] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Agregar el módulo nuevo al diccionario "módulo → roles permitidos" compartido entre `Sidebar.tsx` y los permisos de DRF.
- [ ] Confirmar que el módulo nuevo no aparece en el sidebar para roles que no deben verlo, verificando el HTML renderizado (no solo visualmente).
