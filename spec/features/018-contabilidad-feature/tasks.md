# 018 · Contabilidad — Tareas

- [ ] Crear modelo `CuentaContable` y su migración.
- [ ] Crear modelo `AsientoContable` y su migración.
- [ ] Crear modelo `MovimientoContable` y su migración.
- [ ] Crear migración de datos precargando el catálogo de cuentas base.
- [ ] Crear `backend/apps/contabilidad/services/generador_asientos.py` con las tres funciones de generación, validando cuadre de cargos/abonos.
- [ ] Integrar `generar_asiento_venta()` en la confirmación de venta (`011`), dentro de la misma transacción.
- [ ] Integrar `generar_asiento_compra()` en la acción `recibir()` de compras (`010`).
- [ ] Integrar `generar_asiento_caja()` en la creación de movimientos de caja (`013`).
- [ ] Crear `CuentaContableViewSet` (CRUD, solo admin).
- [ ] Crear vistas de solo lectura para libro diario y balance de comprobación, con filtros por fecha/cuenta/origen.
- [ ] Crear endpoint de exportación (CSV) del libro diario y balance de comprobación.
- [ ] Registrar rutas en el router principal.
- [ ] Crear `frontend/src/api/contabilidad.js`.
- [ ] Crear hooks `useCuentasContables.js`, `useLibroDiario.js`, `useBalanceComprobacion.js`.
- [ ] Crear `frontend/src/pages/Contabilidad/Contabilidad.jsx` con selector de secciones.
- [ ] Implementar vista expandible de asientos en el libro diario.
- [ ] Implementar botón de exportación en ambas vistas.
- [ ] Agregar la ruta `/contabilidad` en `App.jsx` y el módulo al diccionario "módulo → roles permitidos" (solo admin).
- [ ] Re-ejecutar la suite completa de tests de `011 · Ventas`, `010 · Compras` y `013 · Caja` tras integrar la generación de asientos, verificando que no hay regresión.
- [ ] Escribir tests unitarios de `generador_asientos.py`: cuadre correcto, cuentas y sentido (cargo/abono) contablemente correctos por tipo de origen.
- [ ] Escribir tests de frontend: navegación entre secciones, expansión de asientos, exportación.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Revisar si el cambio afecta la lógica de `generador_asientos.py` y actualizarla junto con la feature que la originó, para no dejar la contabilidad desincronizada de la operación real.