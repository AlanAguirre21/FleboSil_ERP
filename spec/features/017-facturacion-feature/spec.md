# 017 · Facturación

**Estado:** propuesta

## Qué hace

Permite generar un CFDI (factura fiscal electrónica) a partir de una venta ya registrada, siempre que el cliente asociado tenga sus datos fiscales completos. El proceso envía la información a un PAC (Proveedor Autorizado de Certificación) configurado en `016 · Configuración Fiscal`, obtiene el XML y PDF timbrados, y los deja disponibles para descarga. Permite cancelar una factura ya timbrada siguiendo el flujo de motivos definidos por el SAT, y registrar Complementos de Pago para facturas con método de pago en parcialidades (PPD). Cualquier usuario autenticado puede generar, consultar y cancelar facturas.

## Por qué

Cierra el ciclo comercial completo iniciado en `011 · Ventas`, dando a la empresa la capacidad de emitir comprobantes fiscales válidos ante el SAT sin depender de un proceso manual externo. Depende de que `016 · Configuración Fiscal` ya tenga los datos de la empresa y del PAC configurados, y de que `008 · Personas` ya haya capturado los datos fiscales del cliente.

## Criterios de aceptación

- [ ] El botón "Generar factura" en el detalle de una venta (`011`) está habilitado únicamente si el cliente de esa venta tiene datos fiscales completos.
- [ ] Al generar una factura, el sistema arma el CFDI con los datos de la venta (`Venta` + `DetalleVenta`), los datos fiscales del cliente, y los datos fiscales de la empresa (`016`), y lo envía al PAC configurado para su timbrado.
- [ ] Si el timbrado es exitoso, se guarda el folio fiscal (UUID), el XML y el PDF resultantes, y la factura queda en estado `timbrada`.
- [ ] Si el PAC rechaza el timbrado (datos inválidos, servicio no disponible, etc.), se muestra el motivo del rechazo de forma clara, y la factura queda en estado `error` sin bloquear un reintento posterior.
- [ ] Es posible descargar el XML y el PDF de cualquier factura ya timbrada.
- [ ] Es posible cancelar una factura timbrada, seleccionando uno de los cuatro motivos de cancelación definidos por el SAT.
- [ ] Al cancelar, el sistema respeta el flujo de aceptación del receptor (ventana de 72 horas) tal como lo exige el SAT, dejando la factura en estado `pendiente de cancelación` hasta la confirmación o vencimiento del plazo.
- [ ] Es posible registrar un Complemento de Pago para una factura con `metodo_pago = PPD`, indicando monto y fecha del pago, lo cual genera su propio folio fiscal timbrado por separado.
- [ ] La lista de facturas es filtrable por estado, fecha y cliente.
- [ ] Cualquier usuario autenticado puede generar, consultar y cancelar facturas — no hay restricción de rol en este módulo.
- [ ] Ninguna factura se puede editar una vez timbrada — solo cancelar y, si aplica, volver a generar una nueva a partir de la misma venta.

## Fuera de alcance

- No incluye la gestión de credenciales del PAC ni datos fiscales de la empresa — corresponde a `016 · Configuración Fiscal`, ya construida.
- No incluye la captura o edición de datos fiscales del cliente — corresponde a `008 · Personas`.
- No incluye reintentos automáticos programados ante fallos del PAC — el reintento es manual, iniciado por el usuario.