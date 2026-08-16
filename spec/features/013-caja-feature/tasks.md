# 013 · Caja — Tareas

- [ ] Verificar si el modelo `MovimientosCaja` ya existe desde `011 · Ventas`; completar sus campos si falta alguno, sin duplicar la migración.
- [ ] Crear `MovimientoCajaSerializer` con validación de monto positivo y descripción obligatoria en movimientos manuales.
- [ ] Crear `MovimientoCajaViewSet` con solo `list`, `retrieve`, `create` (sin mixins de update/destroy).
- [ ] Implementar cálculo de `saldo_resultante` y bloqueo estricto de saldo negativo con `select_for_update()`.
- [ ] Verificar que la creación automática de movimientos desde Ventas reutilice la misma función/servicio de creación, no lógica duplicada.
- [ ] Restringir el permiso completo del ViewSet a rol admin (lectura y escritura).
- [ ] Registrar rutas de `MovimientosCaja` en el router.
- [ ] Crear `frontend/src/api/caja.ts` con listado filtrable y creación de movimiento manual.
- [ ] Crear `frontend/src/hooks/useMovimientosCaja.ts`.
- [ ] Crear `frontend/src/pages/Caja/Caja.tsx` con saldo destacado, tabla filtrable y botón de registro manual.
- [ ] Implementar manejo de error claro cuando el backend rechaza un retiro por saldo insuficiente.
- [ ] Confirmar que el módulo "Caja" en el diccionario "módulo → roles permitidos" (definido en `001`) está restringido solo a admin.
- [ ] Agregar la ruta `/caja` en `App.tsx`, protegida exclusivamente para admin.
- [ ] Escribir tests de backend: creación de ingreso/retiro manual, rechazo de retiro que dejaría saldo negativo, ausencia de rutas de update/destroy (verificar 405), cálculo correcto de `saldo_resultante`, condición de carrera con `select_for_update()`.
- [ ] Escribir tests de frontend: ocultamiento del módulo para rol operador, render de saldo actual, manejo de error de saldo insuficiente.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._