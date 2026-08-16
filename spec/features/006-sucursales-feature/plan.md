# 006 · sucursales — Plan

## Enfoque

CRUD estándar sobre un solo modelo (`Sucursal`), sin lógica de negocio compleja — es la feature más simple del roadmap hasta ahora. Backend: ViewSet de DRF con permisos diferenciados por método HTTP (lectura para cualquier rol autenticado, escritura solo admin). Frontend: página con tabla de listado + modal de formulario para crear/editar, reutilizando componentes comunes que se definirán aquí por primera vez (`Tabla`, `Modal`, `BotonPrimario`) para que las features siguientes ya los encuentren construidos.

**Extensión (reactivación, nombre duplicado, bloqueo de movimientos, historial):** la reactivación se expone como una acción dedicada del ViewSet (`POST /sucursales/{id}/reactivar/`), no como un `PATCH` genérico de `activo` — mismo criterio ya aplicado en Compras/Ventas para operaciones que disparan un efecto secundario auditable (aquí, el registro en `HistorialEstadoSucursal`). La validación de nombre+ubicación se centraliza en una función compartida, invocada tanto desde `SucursalSerializer.validate()` (crear/editar) como desde la acción `reactivar()`, para no duplicar la regla en dos lugares. El bloqueo de `MovimientoInventario` para sucursales inactivas **no se implementa en este código** — vive en `009 · Inventario` (y en `010`/`011`/`012`, que son quienes crean movimientos) — aquí solo se establece `Sucursal.activo` como la única fuente de verdad que esas features deben consultar. `MovimientoCaja` queda deliberadamente fuera de cualquier validación de sucursal, por ser una entidad global (ver `constitution/mission.md`).

## Implementación

1. Backend — crear modelo `Sucursal` en `backend/apps/sucursales/models.py`: `nombre`, `direccion`, `telefono`, `activo`.
2. Backend — crear migración correspondiente.
3. Backend — crear `SucursalSerializer` en `backend/apps/sucursales/serializers.py`.
4. Backend — crear `SucursalViewSet` en `backend/apps/sucursales/views.py`, con permiso personalizado: `SAFE_METHODS` (GET) para cualquier usuario autenticado, métodos de escritura (`POST`, `PUT`, `PATCH`, `DELETE`) solo para rol admin.
5. Backend — sobreescribir el método de borrado del ViewSet para que un `DELETE` real se convierta en `activo=False` (soft delete), nunca una eliminación física de la fila.
6. Backend — registrar las rutas en `backend/apps/sucursales/urls.py` e incluirlas en el router principal.
7. Frontend — crear componentes comunes reutilizables (si no existen aún): `frontend/src/components/common/Tabla.tsx`, `Modal.tsx`, `BotonPrimario.tsx`, con sus `.module.css` correspondientes, componiendo clases de Tailwind vía `@apply` (`@reference` a `index.css`) sobre los tokens del `@theme`.
8. Frontend — crear `frontend/src/api/sucursales.ts` con las funciones CRUD contra el endpoint.
9. Frontend — crear `frontend/src/hooks/useSucursales.ts` con React Query (listado, creación, edición, desactivación).
10. Frontend — crear `frontend/src/pages/Sucursales/Sucursales.tsx`: tabla con datos, botones de acción visibles solo si `rol === 'admin'` (leyendo de `useUsuarioActual`, ya creado en la feature 001).
11. Frontend — crear el formulario de alta/edición dentro de un `Modal`, reutilizado para ambos casos.
12. Frontend — agregar la ruta `/sucursales` en `frontend/src/App.tsx`, protegida y envuelta en `MainLayout`.

### Extensión

13. Backend — crear modelo `HistorialEstadoSucursal` en `backend/apps/sucursales/models.py`: `sucursal` (FK), `estado_anterior` (Boolean), `estado_nuevo` (Boolean), `usuario` (FK), `fecha` (`auto_now_add`). Sin `update`/`delete` expuestos — solo lectura interna y creación programática, igual que `MovimientosCaja`/`MovimientosInventario`.
14. Backend — crear la migración del nuevo modelo.
15. Backend — crear una función de validación compartida (ej. `apps/sucursales/validators.py::validar_nombre_disponible(nombre, ubicacion, excluir_pk=None)`) que implemente la regla de nombre duplicado: rechaza si existe otra sucursal **activa** con ese nombre, o si existe otra sucursal (activa o inactiva) con ese mismo nombre **y** esa misma ubicación.
16. Backend — invocar `validar_nombre_disponible()` desde `SucursalSerializer.validate()`, cubriendo tanto creación como edición (incluyendo el renombrado de una sucursal ya existente).
17. Backend — modificar `SucursalViewSet.perform_destroy()` para que, dentro de `transaction.atomic()`, además de `activo=False`, cree el `HistorialEstadoSucursal` correspondiente (`estado_anterior=True`, `estado_nuevo=False`).
18. Backend — crear la acción `POST /api/sucursales/{id}/reactivar/` en `SucursalViewSet` (mismo permiso que el resto de escritura: solo admin) que, dentro de `transaction.atomic()` con `select_for_update()`: invoca `validar_nombre_disponible()` sobre el nombre/ubicación actuales de la sucursal, establece `activo=True`, y crea el `HistorialEstadoSucursal` (`estado_anterior=False`, `estado_nuevo=True`).
19. Frontend — extender `frontend/src/api/sucursales.ts` con `reactivarSucursal(id)`.
20. Frontend — extender `frontend/src/hooks/useSucursales.ts` con `useReactivarSucursal()`, invalidando la misma `queryKey` que el resto de mutaciones.
21. Frontend — en `Sucursales.tsx`, agregar el botón "Reactivar" en `renderAcciones` cuando `!fila.activo` (visible solo para admin), con su propio modal de confirmación (mismo patrón que "Desactivar").
22. Frontend — verificar que los mensajes de error devueltos por `validar_nombre_disponible()` (clave `nombre_sucursal`) se muestren en el formulario de alta/edición reutilizando el manejo de errores ya existente (`datos?.nombre_sucursal?.[0]`), sin necesitar un nuevo camino de error en el frontend.

## Decisiones

- **Soft delete (`activo=False`) en vez de borrado físico, forzado a nivel de ViewSet** — ya establecido como principio general en la constitución (trazabilidad total); aquí se implementa por primera vez como patrón reutilizable para las features siguientes que también lo necesitarán (Productos, MateriaPrima, Clientes, etc.).
- **Componentes comunes (`Tabla`, `Modal`, `BotonPrimario`) se construyen aquí, no en el Header** — esta es la primera feature con un CRUD real de la aplicación; construirlos ahora evita duplicar patrones de tabla/modal en cada feature posterior (Catálogo, Personas, etc., todos van a necesitar lo mismo).
- **Permisos diferenciados por método HTTP en un único ViewSet, no dos vistas separadas (una de lectura, otra de escritura)** — reduce duplicación de código y mantiene el patrón estándar de DRF (`SAFE_METHODS`), más simple de mantener para un solo desarrollador que dos endpoints paralelos.
- **Sin filtros de búsqueda en el listado** — se descarta añadir buscador/paginación en esta feature dado el volumen esperado (2-3 sucursales); se añadiría solo si el número crece de forma significativa.
- **Reactivación como acción dedicada (`POST .../reactivar/`), no un `PATCH` de `activo`** — mismo criterio ya aplicado a "recibir"/"cancelar" en Compras y Ventas: el cambio de estado dispara un efecto secundario auditable (`HistorialEstadoSucursal`) que no debe quedar oculto dentro de una actualización genérica de recurso. Además, `activo` ya es `read_only` en `SucursalSerializer`; exponerlo por `PATCH` habría requerido remover esa protección para todos los casos, no solo para la reactivación.
- **Validación de nombre duplicado centralizada en una función compartida, no repetida en el serializer y en la acción de reactivar** — evita que ambos caminos diverjan con el tiempo; es la misma regla de negocio ("¿puede existir esta sucursal con este nombre y ubicación ahora mismo?") vista desde dos operaciones distintas.
- **Comparación de nombre/ubicación exacta (sensible a mayúsculas y espacios), sin normalizar** — decisión explícita por simplicidad; se documenta como posible ajuste futuro si en la práctica genera duplicados accidentales por diferencias de mayúsculas o espacios.
- **Sin campo `activo` en `InventarioSucursalProducto`/`InventarioSucursalMateriaPrima`** — su disponibilidad se deriva por completo de `Sucursal.activo`; agregar un campo espejo introduciría un estado redundante que sincronizar (y que podría desincronizarse) sin aportar información nueva.
- **`MovimientoInventario` valida `sucursal.activo` en el código de `009`/`010`/`011`/`012`, no aquí** — esta feature no crea `MovimientoInventario`; solo establece la fuente de verdad (`Sucursal.activo`) que esas features deben consultar en su propia `transaction.atomic()`. Se documenta como dependencia cruzada explícita para no perderla de vista al planificar esas features.
- **`MovimientoCaja` queda fuera de cualquier validación de sucursal** — Caja es global por decisión ya tomada en la constitución (`mission.md`, `CLAUDE.md`: "profit, cash (caja)... are global to the company, never segmented by branch"); la protección ante una sucursal inactiva llega de forma indirecta, vía el rollback de la transacción atómica de la operación que combina inventario y caja (ej. una venta).
- **Sin endpoint/vista de consulta para `HistorialEstadoSucursal` en esta iteración** — decisión explícita: por ahora es un registro de auditoría interno (se crea, nunca se lee vía API); se añadiría como extensión menor (endpoint de solo lectura + tabla) si surge la necesidad real de consultarlo desde la interfaz.

## Riesgos

- **Los componentes comunes (`Tabla`, `Modal`) definidos aquí podrían no anticipar necesidades de features futuras (ej. columnas dinámicas, paginación) y requerir refactor posterior** — mitigación: diseñarlos con props flexibles desde el inicio (columnas configurables vía props, no hardcodeadas), aunque esta feature en particular no las necesite todas todavía.
- **Un usuario operador podría intentar forzar la escritura llamando directo a la API (bypass del frontend)** — mitigación: ya cubierta por el permiso a nivel de ViewSet en el backend, no solo ocultando botones en el frontend, consistente con el límite duro ya establecido en el tech-stack.
- **Desactivar una sucursal con inventario activo podría generar confusión operativa (ej. un producto con stock que ya no es seleccionable en Ventas)** — mitigación: mostrar advertencia clara al admin antes de desactivar si la sucursal tiene inventario con `stock_actual > 0` en alguna de sus tablas relacionadas (validación a implementar cuando exista la feature de Inventario, documentado aquí como dependencia futura).
- **Condición de carrera en la validación de nombre duplicado** si dos admins registran/reactivan simultáneamente la misma combinación nombre+ubicación antes de que la primera transacción confirme — mitigación: `select_for_update()` sobre las filas candidatas dentro de `transaction.atomic()` (mismo estándar ya exigido en el tech-stack para operaciones que modifican estado compartido), no confiar únicamente en la validación a nivel de aplicación sin bloqueo.
- **Si `009 · Inventario`, `010 · Compras`, `011 · Ventas` o `012 · Producción` se planifican sin volver a este documento, podrían omitir el bloqueo de `MovimientoInventario` para sucursales inactivas** — mitigación: cuando se escriba el `plan.md` de cada una de esas features, debe referenciar explícitamente este criterio de `006` antes de darse por completo.