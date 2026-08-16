# 009 · inventario — Plan

_Cómo se implementa lo descrito en `spec.md`. Debe respetar la `constitution/`._

## Enfoque

Esta feature es de solo lectura desde la perspectiva del usuario — no crea flujos de escritura propios, expone lo que otras features (aún no construidas) van a generar. Backend: modelos `InventarioSucursalProducto`, `InventarioSucursalMateriaPrima` y `MovimientosInventario`, con endpoints de solo consulta (`GET`) y filtros vía query params de DRF. Frontend: página con selector de tipo + selector de sucursal + tabla de stock, y una sección aparte de historial con sus propios filtros, reutilizando `Tabla` de `006`.

## Implementación

1. Backend — crear modelo `InventarioSucursalProducto` en `backend/apps/inventario/models.py`: `sucursal_id` (FK), `producto_id` (FK), `stock_actual` (Decimal), `stock_minimo` (Decimal), con `unique_together = ('sucursal', 'producto')`.
2. Backend — crear modelo `InventarioSucursalMateriaPrima`: misma estructura, con `materia_prima_id` en vez de `producto_id`.
3. Backend — crear modelo `MovimientosInventario`: `sucursal_id`, `item_id`, `tipo_item` (producto/materia_prima), `tipo_movimiento` (entrada/salida), `cantidad`, `motivo`, `referencia_id` (entero simple, resuelto a nivel de aplicación), `stock_resultante`, `usuario_id`, `fecha`.
4. Backend — crear migraciones de los tres modelos.
5. Backend — crear serializers de solo lectura para los tres modelos (sin `create`/`update` expuestos en esta feature).
6. Backend — crear `InventarioSucursalProductoViewSet`/`MateriaPrimaViewSet` como `ReadOnlyModelViewSet` de DRF, con filtros por `sucursal_id`.
7. Backend — crear `MovimientosInventarioViewSet` como `ReadOnlyModelViewSet`, con filtros por `item_id`, `sucursal_id`, `tipo_movimiento` vía `django-filter` o query params manuales.
8. Backend — crear endpoint agregado `GET /api/inventario/alertas/` si no quedó ya cubierto desde la feature `001 · Header` (verificar y reutilizar, no duplicar).
9. Frontend — crear `frontend/src/api/inventario.ts` con las funciones de consulta (stock por tipo+sucursal, historial con filtros).
10. Frontend — crear `frontend/src/hooks/useInventario.ts` y `useMovimientosInventario.ts` con React Query.
11. Frontend — crear `frontend/src/pages/Inventario/Inventario.tsx`: selector de tipo (producto/materia prima), selector de sucursal, tabla de stock con indicador visual de alerta (usando el token `--color-advertencia` del bloque `@theme` de `index.css`, vía la clase de utilidad `text-advertencia`/`bg-advertencia` de Tailwind).
12. Frontend — agregar sección de historial dentro de la misma página, con sus propios filtros (producto/materia prima, sucursal, tipo de movimiento), sin botones de acción.
13. Frontend — agregar la ruta `/inventario` en `App.tsx`, sin restricción de rol.

## Decisiones

- **`ReadOnlyModelViewSet` en vez de `ModelViewSet` con permisos restringidos** — refuerza a nivel de framework que esta feature no expone escritura alguna; es más seguro que solo bloquear con permisos, porque el método HTTP de escritura ni siquiera existe en la ruta.
- **Sin restricción de rol para consulta** — el inventario es información operativa que cualquier usuario necesita ver a diario (ej. antes de prometer una venta), a diferencia de Catálogo o Sucursales que son configuración administrativa.
- **Historial y stock actual en la misma página, no en rutas separadas** — mantiene coherente el patrón de "una página por módulo con secciones internas" ya usado en Catálogo y Personas, evitando fragmentar la navegación.
- **`referencia_id` resuelto a nivel de aplicación, no como FK real** — decisión ya justificada en el diseño de datos original: esta tabla es de auditoría/historial, prioriza tener un registro cronológico único sobre integridad referencial estricta hacia tres tablas distintas.

## Riesgos

- **Sin datos de Compras/Ventas/Producción aún construidos, esta feature no tiene forma de probarse con datos reales de extremo a extremo** — mitigación: crear un fixture o script de carga de datos de prueba (`management command` de seed) que inserte movimientos ficticios, solo para validar visualmente esta feature antes de que las features generadoras existan.
- **El filtro combinado (tipo + sucursal + producto + tipo de movimiento) podría generar consultas lentas si el historial crece mucho** — mitigación: agregar índices de base de datos sobre `sucursal_id`, `item_id` y `fecha` en `MovimientosInventario` desde la migración inicial, no como optimización posterior.
- **Confusión entre "sin registro de inventario" (ítem nunca comprado en esa sucursal) y "stock en cero por venta"** — mitigación: el criterio de aceptación ya cubre esto (mostrar 0 en ambos casos desde la interfaz), pero verificar que la consulta backend maneje explícitamente la ausencia de fila con un `LEFT JOIN` o equivalente en el ORM, no un error 404.