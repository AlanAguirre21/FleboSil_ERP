# 017 · Facturación — Tareas

- [ ] Crear modelo `Factura` (FK 1:1 a `Venta`) y su migración.
- [ ] Crear modelo `ComplementoPago` y su migración.
- [ ] Crear `backend/apps/facturacion/services/pac_client.py` con métodos de timbrado, cancelación y complemento de pago.
- [ ] Crear `FacturaSerializer`/`FacturaViewSet` con acciones `create`, `cancelar`, `descargar_xml`, `descargar_pdf`.
- [ ] Implementar validación de datos fiscales completos antes de intentar timbrar.
- [ ] Implementar manejo de estado `error` ante fallo del PAC, sin excepción no controlada.
- [ ] Implementar mecanismo de verificación/expiración de las 72 horas para cancelaciones pendientes.
- [ ] Crear `ComplementoPagoSerializer`/`ComplementoPagoViewSet`.
- [ ] Registrar rutas en el router principal.
- [ ] Crear `frontend/src/api/facturacion.ts`.
- [ ] Crear `frontend/src/hooks/useFacturas.ts`.
- [ ] Modificar `DetalleVenta.tsx` para habilitar el botón "Generar factura" condicionalmente.
- [ ] Crear `frontend/src/pages/Facturacion/Facturacion.tsx` con lista filtrable.
- [ ] Implementar formulario de cancelación con selector de motivo SAT.
- [ ] Implementar formulario de Complemento de Pago para facturas PPD.
- [ ] Agregar la ruta `/facturacion` en `App.tsx` y el módulo al diccionario "módulo → roles permitidos" (sin restricción de rol).
- [ ] Escribir tests de backend: timbrado exitoso (mockeando `pac_client`), manejo de error del PAC, validación de datos fiscales incompletos, flujo de cancelación con motivo, registro de complemento de pago.
- [ ] Escribir tests de frontend: habilitación condicional del botón de factura, filtros de la lista, formulario de cancelación.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Verificar que los catálogos SAT usados (régimen fiscal, uso de CFDI, motivos de cancelación) sigan vigentes; actualizar si el SAT publica cambios.
- [ ] Revisar facturas en estado `pendiente_cancelacion` que hayan superado las 72 horas sin resolución automática, si el mecanismo de verificación falla.