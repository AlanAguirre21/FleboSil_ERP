# 012 · Producción — Tareas

- [ ] Crear modelo `Receta` y su migración.
- [ ] Crear modelo `Produccion` (cabecera) y su migración.
- [ ] Crear modelo `DetalleProduccion` (líneas, snapshot de consumo) y su migración.
- [ ] Crear `RecetaSerializer`/`RecetaViewSet`, reutilizando el permiso "solo admin escribe".
- [ ] Crear `ProduccionSerializer`/`ProduccionViewSet` con `create` + solo lectura.
- [ ] Implementar validación de receta activa antes de permitir producción.
- [ ] Implementar `transaction.atomic()` con `select_for_update()` ordenado por `id`, validación todo-o-nada de stock de materia prima.
- [ ] Implementar creación de `DetalleProduccion` por cada materia prima consumida, con `costo_unitario_momento` congelado.
- [ ] Implementar aumento de `InventarioSucursalProducto` y creación del movimiento de entrada correspondiente.
- [ ] Registrar rutas de `Receta` y `Produccion` en el router.
- [ ] Crear `frontend/src/api/produccion.ts`.
- [ ] Crear `frontend/src/hooks/useRecetas.ts` y `useProducciones.ts`, invalidando cache de inventario.
- [ ] Crear `frontend/src/pages/Produccion/Produccion.tsx` con selector de secciones.
- [ ] Implementar gestión de recetas (CRUD, solo admin).
- [ ] Implementar formulario de nueva producción, con validación de stock en vivo antes de confirmar.
- [ ] Implementar vista de detalle de producción con desglose de `DetalleProduccion`.
- [ ] Agregar la ruta `/produccion` en `App.tsx` y el módulo al diccionario "módulo → roles permitidos".
- [ ] Escribir tests de backend: producción exitosa con múltiples materias primas, rechazo por stock insuficiente de una sola materia prima, bloqueo si no existe receta activa, orden de locks previniendo deadlock (test de concurrencia si es viable), inmutabilidad del historial ante cambio posterior de receta.
- [ ] Escribir tests de frontend: cálculo en vivo de materia prima requerida, bloqueo de confirmación si falta stock, render del desglose de consumo en el detalle.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._