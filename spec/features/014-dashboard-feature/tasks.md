# 014 · Dashboard — Tareas

- [ ] Crear app `backend/apps/reportes/` (si no existe) con `views.py`, `urls.py`.
- [ ] Implementar el endpoint `GET /api/reportes/resumen/` con agregación de Ventas/Compras según periodo.
- [ ] Definir y documentar explícitamente qué estados de venta/compra cuentan para el cálculo de ganancia.
- [ ] Implementar la serie de puntos por día dentro del periodo, para alimentar la gráfica.
- [ ] Verificar/crear índice sobre `fecha` en `Ventas` y `Compras`.
- [ ] Registrar la ruta del endpoint en el router principal.
- [ ] Crear `frontend/src/api/reportes.js`.
- [ ] Crear `frontend/src/hooks/useResumenDashboard.js` con `staleTime` corto.
- [ ] Crear `frontend/src/pages/Dashboard/Dashboard.jsx` con selector de periodo, tarjetas de totales y gráfica.
- [ ] Crear `frontend/src/pages/Dashboard/Dashboard.module.css`.
- [ ] Implementar botones de acceso directo a "Nueva venta" y "Nueva compra".
- [ ] Implementar estado vacío cuando no hay datos suficientes.
- [ ] Configurar la ruta raíz autenticada para apuntar al Dashboard tras login.
- [ ] Escribir tests de backend: cálculo correcto de ganancia por periodo, exclusión de ventas/compras canceladas, serie de puntos correcta para la gráfica.
- [ ] Escribir tests de frontend: cambio de periodo recalcula datos, render de estado vacío, navegación de los accesos directos.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._