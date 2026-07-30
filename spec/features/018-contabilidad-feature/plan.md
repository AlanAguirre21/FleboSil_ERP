# 018 · contabilidad — Plan

## Enfoque

Tres modelos (`CuentaContable`, `AsientoContable`, `MovimientoContable`), donde la generación de asientos ocurre mediante señales de Django (`post_save`) o llamadas explícitas desde el mismo servicio que confirma una venta, compra o movimiento de caja — nunca como un proceso separado que el usuario dispare manualmente. Se centraliza la lógica de generación de asientos en un servicio (`backend/apps/contabilidad/services/generador_asientos.py`) para no duplicar reglas contables en cada app (ventas, compras, caja).

## Implementación

1. Backend — crear modelo `CuentaContable` en `backend/apps/contabilidad/models.py`: `codigo`, `nombre`, `tipo`, `cuenta_padre_id` (FK nullable), `activo`.
2. Backend — crear modelo `AsientoContable`: `fecha`, `concepto`, `referencia_id`, `tipo_origen` (venta/compra/caja/ajuste), `usuario_id`.
3. Backend — crear modelo `MovimientoContable`: `asiento_id` (FK), `cuenta_contable_id` (FK), `tipo_movimiento` (cargo/abono), `monto`.
4. Backend — crear migraciones de los tres modelos, y una migración de datos (`data migration`) que precargue el catálogo de cuentas contables base (caja, ventas, inventario, proveedores, clientes) para que el sistema no arranque sin ninguna cuenta configurada.
5. Backend — crear `backend/apps/contabilidad/services/generador_asientos.py`: funciones `generar_asiento_venta(venta)`, `generar_asiento_compra(compra)`, `generar_asiento_caja(movimiento_caja)`, cada una construyendo el `AsientoContable` + sus `MovimientoContable` de cargo/abono dentro de `transaction.atomic()`, validando que la suma de cargos sea igual a la suma de abonos antes de confirmar.
6. Backend — modificar `backend/apps/ventas/views.py` (de `011`) para invocar `generar_asiento_venta()` dentro de la misma transacción de confirmación de venta.
7. Backend — modificar `backend/apps/compras/views.py` (de `010`) para invocar `generar_asiento_compra()` dentro de la acción `recibir()`.
8. Backend — modificar `backend/apps/caja/models.py` o su servicio de creación (de `013`) para invocar `generar_asiento_caja()` en cada movimiento creado.
9. Backend — crear `CuentaContableViewSet` (CRUD, solo admin) y `AsientoContableViewSet`/`endpoint de balance` (solo lectura, solo admin), con filtros por fecha/cuenta/origen.
10. Backend — crear endpoint de exportación (`GET /api/contabilidad/exportar/?formato=csv`) que genere el archivo de libro diario o balance de comprobación.
11. Backend — registrar rutas en el router principal.
12. Frontend — crear `frontend/src/api/contabilidad.js` con funciones CRUD de cuentas, consulta de libro diario, balance, y exportación.
13. Frontend — crear `frontend/src/hooks/useCuentasContables.js`, `useLibroDiario.js`, `useBalanceComprobacion.js`.
14. Frontend — crear `frontend/src/pages/Contabilidad/Contabilidad.jsx`: selector entre "Catálogo de cuentas", "Libro diario" y "Balance de comprobación".
15. Frontend — implementar la vista expandible de cada asiento en el libro diario, mostrando sus líneas de cargo/abono.
16. Frontend — implementar el botón de exportación en ambas vistas (libro diario, balance).
17. Frontend — agregar la ruta `/contabilidad` en `App.jsx`, protegida exclusivamente para admin.

## Decisiones

- **Generación de asientos integrada directamente en las transacciones de Ventas/Compras/Caja ya existentes, no como un proceso batch aparte** — garantiza que nunca exista una venta o movimiento de caja sin su asiento correspondiente; un proceso separado correría el riesgo de ejecutarse tarde, fallar silenciosamente, o duplicar asientos si se corre dos veces.
- **Validación de cuadre (cargos = abonos) dentro de la misma transacción atómica que genera el asiento** — si por un error de programación un asiento quedara descuadrado, se prefiere que toda la operación (venta/compra/movimiento de caja) falle y se revierta, antes que dejar contabilidad inconsistente silenciosamente.
- **Sin creación manual de asientos por el usuario** — decisión explícita para evitar que alguien sin conocimiento contable genere asientos incorrectos o descuadrados; cualquier ajuste contable necesario se documenta como excepción a resolver directamente con el contador externo, fuera del sistema.
- **Migración de datos precargando un catálogo de cuentas base** — sin esto, el sistema no tendría ninguna cuenta contable definida al arrancar, y la primera venta fallaría al intentar generar su asiento sin cuentas destino válidas.

## Riesgos

- **Modificar Ventas, Compras y Caja (features ya completadas) para invocar la generación de asientos introduce riesgo de regresión sobre funcionalidad ya probada** — mitigación: envolver la llamada a `generar_asiento_*()` de forma que, si falla, revierta toda la transacción original (venta/compra/movimiento), tratándolo como parte integral de la operación, no como un efecto secundario opcional; correr toda la suite de tests de esas features nuevamente tras la integración.
- **El catálogo de cuentas base precargado podría no ajustarse exactamente a cómo el contador externo de la empresa organiza sus cuentas** — mitigación: el catálogo es editable por el admin después de la carga inicial; documentar que se recomienda validar la estructura de cuentas con el contador antes de operar en producción.
- **Un asiento generado automáticamente con una regla contable incorrecta (ej. cargo/abono invertido) se replicaría en todas las transacciones futuras hasta detectarse** — mitigación: escribir tests unitarios específicos de `generador_asientos.py` que verifiquen no solo que cuadra (cargos=abonos), sino que las cuentas afectadas y el sentido (cargo vs abono) son los correctos contablemente, idealmente revisados con el contador externo antes de considerar esta feature terminada.