# 006 · sucursales — Plan

## Enfoque

CRUD estándar sobre un solo modelo (`Sucursal`), sin lógica de negocio compleja — es la feature más simple del roadmap hasta ahora. Backend: ViewSet de DRF con permisos diferenciados por método HTTP (lectura para cualquier rol autenticado, escritura solo admin). Frontend: página con tabla de listado + modal de formulario para crear/editar, reutilizando componentes comunes que se definirán aquí por primera vez (`Tabla`, `Modal`, `BotonPrimario`) para que las features siguientes ya los encuentren construidos.

## Implementación

1. Backend — crear modelo `Sucursal` en `backend/apps/sucursales/models.py`: `nombre`, `direccion`, `telefono`, `activo`.
2. Backend — crear migración correspondiente.
3. Backend — crear `SucursalSerializer` en `backend/apps/sucursales/serializers.py`.
4. Backend — crear `SucursalViewSet` en `backend/apps/sucursales/views.py`, con permiso personalizado: `SAFE_METHODS` (GET) para cualquier usuario autenticado, métodos de escritura (`POST`, `PUT`, `PATCH`, `DELETE`) solo para rol admin.
5. Backend — sobreescribir el método de borrado del ViewSet para que un `DELETE` real se convierta en `activo=False` (soft delete), nunca una eliminación física de la fila.
6. Backend — registrar las rutas en `backend/apps/sucursales/urls.py` e incluirlas en el router principal.
7. Frontend — crear componentes comunes reutilizables (si no existen aún): `frontend/src/components/common/Tabla.jsx`, `Modal.jsx`, `BotonPrimario.jsx`, con sus `.module.css` correspondientes, consumiendo `variables.css`.
8. Frontend — crear `frontend/src/api/sucursales.js` con las funciones CRUD contra el endpoint.
9. Frontend — crear `frontend/src/hooks/useSucursales.js` con React Query (listado, creación, edición, desactivación).
10. Frontend — crear `frontend/src/pages/Sucursales/Sucursales.jsx`: tabla con datos, botones de acción visibles solo si `rol === 'admin'` (leyendo de `useUsuarioActual`, ya creado en la feature 001).
11. Frontend — crear el formulario de alta/edición dentro de un `Modal`, reutilizado para ambos casos.
12. Frontend — agregar la ruta `/sucursales` en `frontend/src/App.jsx`, protegida y envuelta en `MainLayout`.

## Decisiones

- **Soft delete (`activo=False`) en vez de borrado físico, forzado a nivel de ViewSet** — ya establecido como principio general en la constitución (trazabilidad total); aquí se implementa por primera vez como patrón reutilizable para las features siguientes que también lo necesitarán (Productos, MateriaPrima, Clientes, etc.).
- **Componentes comunes (`Tabla`, `Modal`, `BotonPrimario`) se construyen aquí, no en el Header** — esta es la primera feature con un CRUD real de la aplicación; construirlos ahora evita duplicar patrones de tabla/modal en cada feature posterior (Catálogo, Personas, etc., todos van a necesitar lo mismo).
- **Permisos diferenciados por método HTTP en un único ViewSet, no dos vistas separadas (una de lectura, otra de escritura)** — reduce duplicación de código y mantiene el patrón estándar de DRF (`SAFE_METHODS`), más simple de mantener para un solo desarrollador que dos endpoints paralelos.
- **Sin filtros de búsqueda en el listado** — se descarta añadir buscador/paginación en esta feature dado el volumen esperado (2-3 sucursales); se añadiría solo si el número crece de forma significativa.

## Riesgos

- **Los componentes comunes (`Tabla`, `Modal`) definidos aquí podrían no anticipar necesidades de features futuras (ej. columnas dinámicas, paginación) y requerir refactor posterior** — mitigación: diseñarlos con props flexibles desde el inicio (columnas configurables vía props, no hardcodeadas), aunque esta feature en particular no las necesite todas todavía.
- **Un usuario operador podría intentar forzar la escritura llamando directo a la API (bypass del frontend)** — mitigación: ya cubierta por el permiso a nivel de ViewSet en el backend, no solo ocultando botones en el frontend, consistente con el límite duro ya establecido en el tech-stack.
- **Desactivar una sucursal con inventario activo podría generar confusión operativa (ej. un producto con stock que ya no es seleccionable en Ventas)** — mitigación: mostrar advertencia clara al admin antes de desactivar si la sucursal tiene inventario con `stock_actual > 0` en alguna de sus tablas relacionadas (validación a implementar cuando exista la feature de Inventario, documentado aquí como dependencia futura).