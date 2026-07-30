# 017 · facturacion — Plan

## Enfoque

Modelo `Factura` con relación 1:1 a `Venta`, y `ComplementoPago` como líneas asociadas a una factura con método PPD. La comunicación con el PAC se aísla en un módulo de servicio dedicado (`backend/apps/facturacion/services/pac_client.py`), de forma que si la empresa cambia de proveedor de PAC en el futuro, solo se reemplaza esa capa, sin tocar vistas, modelos ni frontend. El estado de la factura refleja fielmente el ciclo de vida real de un CFDI ante el SAT (pendiente, timbrada, pendiente de cancelación, cancelada, error).

## Implementación

1. Backend — crear modelo `Factura` en `backend/apps/facturacion/models.py`: `venta_id` (FK 1:1), `folio_fiscal`, `serie`, `folio_interno` (usa `SerieFolio` de `016`), `xml_path`, `pdf_path`, `estado`, `fecha_timbrado`, `motivo_cancelacion`, `uso_cfdi`, `forma_pago`, `metodo_pago`.
2. Backend — crear modelo `ComplementoPago`: `factura_id` (FK), `monto_pagado` (Decimal), `fecha_pago`, `folio_fiscal_rep`.
3. Backend — crear migraciones de ambos modelos.
4. Backend — crear `backend/apps/facturacion/services/pac_client.py`: clase con métodos `timbrar(datos_cfdi)`, `cancelar(folio_fiscal, motivo)`, `timbrar_complemento_pago(datos)`, que internamente arma la petición HTTP al PAC configurado (leyendo credenciales descifradas de `ConfiguracionPAC`), y devuelve una respuesta normalizada (éxito/error + datos).
5. Backend — crear `FacturaSerializer` y `FacturaViewSet` con acciones: `create` (arma el CFDI desde la venta y llama a `pac_client.timbrar()`), `cancelar` (llama a `pac_client.cancelar()`), `descargar_xml`, `descargar_pdf`.
6. Backend — en la acción `create()`: validar que el cliente de la venta tenga datos fiscales completos antes de intentar timbrar; si el PAC responde error, guardar la factura en estado `error` con el detalle, sin lanzar excepción no controlada.
7. Backend — en la acción `cancelar()`: cambiar estado a `pendiente_cancelacion`; implementar un mecanismo (management command programado, o verificación al consultar) que, tras 72 horas sin respuesta del receptor, marque automáticamente como `cancelada`.
8. Backend — crear `ComplementoPagoSerializer`/`ComplementoPagoViewSet`, reutilizando `pac_client.timbrar_complemento_pago()`.
9. Backend — registrar rutas en el router principal.
10. Frontend — crear `frontend/src/api/facturacion.js` con funciones de listado, generación, cancelación, descarga y registro de complemento de pago.
11. Frontend — crear `frontend/src/hooks/useFacturas.js` con React Query.
12. Frontend — modificar `frontend/src/pages/Ventas/DetalleVenta.jsx` (de `011`) para habilitar el botón "Generar factura" según los datos fiscales del cliente.
13. Frontend — crear `frontend/src/pages/Facturacion/Facturacion.jsx`: lista filtrable por estado/fecha/cliente, con acciones de descarga y cancelación según el estado de cada factura.
14. Frontend — crear el formulario de cancelación con selector de motivo (catálogo SAT).
15. Frontend — crear el formulario de registro de Complemento de Pago, visible solo en facturas con `metodo_pago = PPD`.
16. Frontend — agregar la ruta `/facturacion` en `App.jsx`, sin restricción de rol.

## Decisiones

- **Comunicación con el PAC aislada en una capa de servicio separada, no llamadas HTTP directas desde la vista** — si la empresa cambia de proveedor de PAC (razón de costo, soporte, etc.), solo se reescribe `pac_client.py`, sin tocar el resto del sistema; reduce el costo de mantenimiento futuro para el único desarrollador del proyecto.
- **Estado `error` explícito en vez de excepción no controlada ante fallo del PAC** — un rechazo del PAC es un escenario esperado y frecuente (datos fiscales mal capturados, catálogos desactualizados), no un caso excepcional del sistema; se documenta como estado válido del ciclo de vida, permitiendo reintentar sin perder el registro del intento fallido.
- **Sin restricción de rol para generar/cancelar facturas** — decisión ya confirmada: consistente con el criterio de operación diaria abierta ya aplicado a Ventas/Compras/Producción.
- **Ciclo de 72 horas para confirmación de cancelación manejado con verificación periódica, no con un webhook del PAC** — se descarta depender de que el PAC notifique activamente (no todos lo hacen de forma confiable); se opta por un mecanismo de verificación propio más simple de mantener.

## Riesgos

- **Dependencia total del PAC contratado: si su servicio cae, no se pueden timbrar facturas** — mitigación: aceptado como riesgo externo fuera del control del sistema; el estado `error` permite reintentar cuando el servicio se restablezca, sin perder la venta original.
- **Datos fiscales del cliente incompletos o mal capturados detectados solo al momento de intentar timbrar, generando fricción en el flujo de venta** — mitigación: ya cubierto por el criterio de aceptación que deshabilita el botón "Generar factura" preventivamente si los datos están incompletos, evitando el peor caso (llegar hasta el PAC y fallar ahí).
- **Recibir el CSD y credenciales incorrectas del PAC solo se detecta hasta el primer intento real de timbrado, no en `016 · Configuración Fiscal`** — mitigación: documentado como fuera de alcance de `016` (sin prueba de conexión), por lo que el primer timbrado real de esta feature funciona también como validación de que la configuración es correcta; comunicar esto al usuario como parte de la puesta en marcha.