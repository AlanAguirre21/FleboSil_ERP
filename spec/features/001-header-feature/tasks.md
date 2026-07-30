# 001 · header — tareas

- [ ] Crear `frontend/src/styles/variables.css` (si aún no existe desde otra feature) con las variables de color de marca y estado definidas en `tech-stack.md`.
- [ ] Crear `frontend/src/components/layout/Header.jsx` con la estructura base: logo enlazado al Dashboard, texto "Enterprise Manager", botón de despliegue de sidebar, ícono de notificaciones, menú de usuario.
- [ ] Crear `frontend/src/components/layout/Header.module.css`, consumiendo variables de `variables.css` — sin colores hardcodeados.
- [ ] Crear `frontend/src/hooks/useUsuarioActual.js` — hook de React Query que expone `{ nombre, rol }` desde `/api/usuarios/me/`.
- [ ] Backend: crear endpoint `GET /api/inventario/alertas/` en `backend/apps/inventario/views.py`, filtrando `stock_actual < stock_minimo` en `InventarioSucursalProducto` y `InventarioSucursalMateriaPrima`.
- [ ] Crear `frontend/src/hooks/useAlertasStock.js` — hook de React Query que consume el endpoint anterior, con `staleTime` configurado (ej. 60s).
- [ ] Implementar el dropdown de notificaciones en `Header.jsx`, mostrando nombre del ítem y sucursal afectada por cada alerta.
- [ ] Crear `frontend/src/components/layout/Sidebar.jsx`, recibiendo el rol como prop y filtrando el array de módulos antes de renderizar (nunca ocultando con CSS).
- [ ] Definir el diccionario "módulo → roles permitidos" como fuente única de verdad, referenciado tanto por `Sidebar.jsx` como por los permisos de DRF en el backend.
- [ ] Crear `frontend/src/components/layout/MainLayout.jsx`, combinando `Header` + `Sidebar` + `<Outlet />` de React Router.
- [ ] Integrar `MainLayout` en `frontend/src/App.jsx`, envolviendo las rutas autenticadas.
- [ ] Implementar estado de carga (skeleton) en `Header`/`Sidebar` mientras `useUsuarioActual` y `useAlertasStock` resuelven.
- [ ] Implementar comportamiento responsive: sidebar colapsado por defecto por debajo del breakpoint `md`, desplegable con el botón correspondiente.
- [ ] Implementar acciones del menú de usuario: acceso a "Información de Usuario" y "Cerrar sesión" (invalidando el token/sesión).
- [ ] Escribir tests con Vitest + React Testing Library para: filtrado de sidebar por rol, render del contador de notificaciones, y navegación del logo al Dashboard.
- [ ] Escribir test de backend (pytest-django) para el endpoint `/api/inventario/alertas/`, cubriendo caso con y sin ítems en alerta.
- [ ] Actualizar `frontend/src/api/inventario.js` con la función que consume el nuevo endpoint de alertas, si no se centralizó ya en el paso del hook.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Agregar el módulo nuevo al diccionario "módulo → roles permitidos" compartido entre `Sidebar.jsx` y los permisos de DRF.
- [ ] Confirmar que el módulo nuevo no aparece en el sidebar para roles que no deben verlo, verificando el HTML renderizado (no solo visualmente).