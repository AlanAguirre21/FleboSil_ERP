# 016 · Configuración Fiscal

**Estado:** propuesta

## Qué hace

Permite al administrador capturar y mantener los datos fiscales de la empresa (RFC, razón social, régimen fiscal), gestionar la conexión con el Proveedor Autorizado de Certificación (PAC) mediante sus credenciales de API, y administrar el catálogo de series y folios que se usarán al timbrar facturas. Es la configuración base sin la cual `017 · Facturación` no puede operar.

## Por qué

Separa la configuración fiscal (poco frecuente, sensible, exclusiva de admin) de la operación diaria de facturar (`017`), siguiendo el mismo principio ya aplicado entre Catálogo/Sucursales (configuración) y Ventas/Compras (operación). Además, aísla las credenciales del PAC en un solo lugar, evitando que terceros o roles no autorizados tengan visibilidad de esas credenciales.

## Criterios de aceptación

- [ ] Esta vista es visible únicamente para el rol admin, tanto en el sidebar como en sus endpoints correspondientes.
- [ ] El admin puede capturar y editar los datos fiscales de la empresa: RFC, razón social, régimen fiscal, código postal fiscal.
- [ ] El admin puede capturar las credenciales de conexión al PAC (API key, endpoint del proveedor, y cualquier identificador adicional que el PAC requiera).
- [ ] Las credenciales del PAC nunca se muestran en texto plano una vez guardadas — al editar, el campo aparece vacío o enmascarado, y solo se actualiza si se ingresa un nuevo valor.
- [ ] El admin puede crear y editar series de facturación, cada una con su folio actual, y el sistema incrementa automáticamente el folio cada vez que se timbra una factura con esa serie (esta última parte se implementa en `017`, aquí solo se define y gestiona el catálogo).
- [ ] No es posible eliminar una serie que ya tiene folios usados — solo desactivarla.
- [ ] Si los datos fiscales de la empresa o las credenciales del PAC están incompletos, el sistema lo indica visualmente en esta pantalla (ej. un aviso "Configuración incompleta"), anticipando que `017 · Facturación` no podrá timbrar sin esto resuelto.
- [ ] El backend rechaza cualquier intento de acceso a estos endpoints desde un rol distinto a admin, incluso llamando directo a la API.

## Fuera de alcance

- No incluye la lógica de timbrado en sí (llamada real al PAC para generar un CFDI) — corresponde a `017 · Facturación`.
- No incluye gestión del Certificado de Sello Digital (CSD) como archivo criptográfico cargado en el sistema — se documenta como posible ampliación futura si el PAC elegido lo requiere directamente en vez de manejarlo él mismo (la mayoría de los PACs actuales gestionan el CSD de su lado, no del sistema del cliente).
- No incluye pruebas de conexión automatizadas con el PAC desde esta pantalla — se documenta como mejora futura (botón "Probar conexión").