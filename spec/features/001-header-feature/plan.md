# 001 · header — plan

## Enfoque

Construir el Header como un componente de layout fijo (`Header.tsx` + `Header.module.css`) que envuelve todas las rutas autenticadas, consumiendo el rol del usuario desde el token JWT decodificado (o un endpoint `/api/usuarios/me/`) para renderizar el sidebar condicionalmente en el mismo componente. Se integra con React Router para el link del logo al Dashboard y con React Query para las notificaciones de stock bajo, reutilizando el mismo patrón de hooks ya definido en el tech-stack.

## Implementación

1. Crear `frontend/src/components/layout/Header.tsx` — estructura base: logo + texto "Enterprise Manager" (link a `/dashboard` vía React Router `<Link>`), botón de despliegue de sidebar, ícono de notificaciones, menú de usuario.
2. Crear `frontend/src/components/layout/Header.module.css` — estilos compuestos con `@apply` de Tailwind (`@reference "../../index.css"`) sobre los tokens del bloque `@theme` (`--color-primario`, `--color-fondo`, etc.), no colores hardcodeados.
3. Crear `frontend/src/components/layout/Sidebar.tsx` — lista de módulos de navegación; recibe el rol del usuario como prop y filtra el array de rutas antes de renderizar (no oculta con CSS, como quedó definido como límite duro en el tech-stack).
4. Crear `frontend/src/hooks/useUsuarioActual.ts` — hook de React Query que expone `{ nombre, rol }` del usuario autenticado, consumido tanto por `Header` (menú de usuario) como por `Sidebar` (filtrado de módulos).
5. Crear `frontend/src/hooks/useAlertasStock.ts` — hook de React Query que consulta un endpoint de backend (`GET /api/inventario/alertas/`) devolviendo productos/materia prima bajo `stock_minimo`, usado por el dropdown de notificaciones.
6. Backend — crear endpoint `GET /api/inventario/alertas/` en `backend/apps/inventario/views.py`, que consulta `InventarioSucursalProducto`/`MateriaPrima` filtrando `stock_actual < stock_minimo`.
7. Crear `frontend/src/components/layout/MainLayout.tsx` — componente contenedor que combina `Header` + `Sidebar` + `<Outlet />` de React Router, usado como layout raíz para todas las rutas protegidas.
8. Integrar `MainLayout` en `frontend/src/App.tsx`, envolviendo las rutas autenticadas mediante rutas anidadas de React Router.

## Decisiones

- **Filtrado de sidebar por rol ocurre en TypeScript, con datos ya confirmados por el backend** — se descarta ocultar visualmente con CSS (`display: none`), porque contradice el límite duro ya establecido en el tech-stack de no validar permisos únicamente en frontend; el array de módulos disponibles nunca incluye rutas que el rol no debe ver, en vez de incluirlas y esconderlas.
- **Notificaciones consultan un endpoint dedicado (`/alertas/`) en vez de traer todo el inventario y filtrar en el cliente** — se descarta traer inventario completo al frontend por rendimiento y porque expondría datos de sucursales/stock que el dropdown de notificaciones no necesita mostrar completos.
- **Header y Sidebar como componentes separados dentro de un mismo `MainLayout`, no un solo componente monolítico** — permite reusar el Sidebar de forma independiente si más adelante se necesita (ej. una vista de solo lectura sin header completo), y separa responsabilidades para facilitar mantenimiento individual.
- **No se incluye selector de sucursal en el Header** — decisión ya tomada previamente en la spec: sucursal es una dimensión de inventario, no un filtro global; se descarta agregarlo aquí para no reintroducir el diseño revertido.

## Riesgos

- **El rol del usuario podría no estar disponible en el primer render (carga async del JWT/endpoint), causando parpadeo del sidebar completo antes de filtrarse** — mitigación: mostrar un estado de carga (skeleton) en el sidebar mientras `useUsuarioActual` resuelve, en vez de renderizar todos los módulos y luego ocultarlos.
- **El endpoint de alertas de stock podría volverse lento si el catálogo crece mucho, al recalcularse en cada apertura de notificaciones** — mitigación: cachear la respuesta con React Query (`staleTime` razonable, ej. 60 segundos) en vez de refetch en cada clic.
- **Inconsistencia entre lo que el sidebar permite navegar y lo que el backend realmente autoriza, si se agregan módulos nuevos sin actualizar ambos lados** — mitigación: el filtrado del sidebar y los permisos de DRF deben derivar de la misma fuente de verdad (idealmente, un solo diccionario de "módulo → roles permitidos" documentado y referenciado desde ambos lados del proyecto).
