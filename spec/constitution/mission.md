# Misión

## Qué construimos

**FleboSil - Enterprise Manager** (flebosil-erp.net) es una aplicación web para la gestión de la empresa **FleboSil** de tamaño pequeño pero con opciones de crecimiento. Busca poder administrar los movimientos financieros de la empresa en términos de ventas (principalmente) y compras, así como tener control de inventarios, producción, empleados y sucursales.

**Nota sobre alcance de sucursal:** la gestión de ganancias, caja y empleados es global a la empresa, no segmentada por sucursal. El concepto de sucursal aplica únicamente a nivel de inventario físico (dónde está el stock, hacia dónde entra una compra, de dónde sale una venta). No existe un filtro de sucursal a nivel de reportes financieros ni de caja.

**Nota sobre facturación y contabilidad:** FleboSil - Enterprise Manager integra facturación fiscal electrónica (CFDI 4.0) para las ventas, mediante un Proveedor Autorizado de Certificación (PAC) externo, y expone reportes contables básicos (libro diario, balance de comprobación) que sirven de insumo para el sistema contable formal de la empresa. El sistema no reemplaza al contador certificado ni genera estados financieros formales (balance general, estado de resultados) — esa responsabilidad legal sigue siendo del contador externo de la empresa.

La aplicación consta de las siguientes ventanas:
Nota: Los puntos del 1 al 3 tienen diseños particulares, que muestran el logotipo de la empresa; los puntos del 4 al 16 usan un estilo de *header* y *footer* de página, con diseño central de la ventana según su función.

- **Header**. Consta de una barra horizontal principal con la opción de abrir la barra vertical (left sidebar). Barra principal: muestra el logotipo de la empresa en la esquina superior izquierda (imagen), que a su vez es un acceso al *dashboard*; debajo del logotipo el texto *Enterprise Manager*; muestra el botón de despliegue de la barra vertical; botón de *notificaciones/alertas* que despliega una lista con alertas de stock mínimo tanto para productos como para materia prima (indicando la sucursal afectada); usuario actual + menú de sesión, que muestra nombre del usuario logueado, rol, opción de cerrar sesión y acceso a ventana *Información de usuario*. No incluye selector de sucursal — la sucursal se selecciona de forma contextual dentro de los módulos que la requieren (Ventas, Compras, Inventario). Sidebar: su función es navegación entre módulos, que son *Ventas*, *Compras*, *Producción*, *Inventario*, *Facturación*, *Caja*, *Catálogo*, *Personas*, *Sucursales*, *Contabilidad*, *Configuración Fiscal* y *Usuarios* (Facturación visible para todos los roles; Contabilidad y Configuración Fiscal únicamente visibles para rol administrador; renderizado según el rol en backend). Contiene las referencias a los archivos de diseño CSS.
- **Footer**. Versión del sistema (v1.0) y copyright/nombre de la empresa. Contiene las referencias a la lógica en JavaScript de React.

1. **Login**. Permite el ingreso del usuario. Pide como datos *correo electrónico* y *contraseña*, corroborados según la base de datos. A la contraseña se le aplica el método de *hashing*. Muestra una opción adicional, *Recuperar contraseña*, que lleva a la ventana pertinente. La creación de usuarios no está disponible desde aquí — se gestiona exclusivamente por un administrador desde el módulo Personas → Usuarios.
2. **Recuperar contraseña**. Permite acceder a la ventana *Cambiar contraseña*. Envía un correo a la dirección de correo electrónico del usuario en cuestión con un número de 6 dígitos aleatorio, que en caso de ingresarse correctamente en la ventana, envía a *Cambiar contraseña*. Al ingresar el correo muestra un mensaje debajo del textbox indicando si se envió el correo de recuperación. Permite enviar otro correo de recuperación con otra clave de 6 dígitos.
3. **Cambiar contraseña**. Permite cambiar la contraseña del usuario que accedió correctamente desde *Recuperar contraseña*. Pide correo y nueva contraseña, además de confirmar nueva contraseña. Una vez cambiada la contraseña se ingresa al Dashboard principal.
4. **Dashboard - MainLayout**. Título principal *Resumen FleboSil*. Resumen de ganancias globales de la empresa (día, semana, mes) con gráfica simple + números — sin segmentación por sucursal. Ventas totales contra compras totales del periodo, a nivel empresa. Accesos directos a nueva venta y nueva compra.
5. **Ventas**. Título *Ventas*. Lista de ventas, filtrable por fecha, sucursal, estado, cliente y producto. Nueva venta con selector de cliente (o sin cliente específico), selector de sucursal (determina de qué inventario se descuenta el stock), buscador de producto que se agrega a *Detalle de Venta*. *Detalle de Venta/ticket*, contiene el total de la venta y la opción de imprimir ticket, también exportable a PDF. Incluye botón *Generar factura*, visible únicamente si el cliente de la venta tiene datos fiscales completos; envía a la ventana de *Facturación* para timbrar el CFDI correspondiente.
6. **Compras**. Título *Compras*. Lista de compras filtrable por proveedor, fecha, estado. Nueva compra con selector de proveedor, selector de sucursal destino (determina a qué inventario entra el stock comprado), selección de tipo (producto o materia prima) con cantidad y costo unitario.
7. **Producción**. Título *Producción*. Lista de producciones registradas con fecha, sucursal y producto. Nueva producción con selección de producto, sucursal y cantidad a producir, válida únicamente si hay stock suficiente de materia prima en esa sucursal. Gestión de recetas, donde se define, edita y muestra la receta de cada producto.
8. **Inventario**. Título *Inventario de productos* o *Inventario de materia prima* — opción para cambiar entre ambos. Tabla con el stock actual por sucursal (seleccionable). Historial de movimientos de solo lectura, filtrable por producto/materia prima, sucursal y tipo de movimiento.
9. **Catálogo**. Título *Catálogo*. Opción para seleccionar el catálogo: productos, materia prima o categorías (de productos). CRUD de productos, materia prima o categorías.
10. **Personas**. Título *Personas*. Selección entre clientes, proveedores, empleados y usuarios. Los empleados son globales a la empresa, no asociados a una sucursal específica. CRUD clientes, con sección de datos fiscales (RFC, razón social, código postal fiscal, régimen fiscal, uso de CFDI por defecto) — obligatoria únicamente si el cliente va a recibir factura. CRUD proveedores. CRUD empleados únicamente para rol admin, rol usuario solo lectura. CRUD usuarios únicamente para rol admin, rol usuario solo lectura.
11. **Sucursales**. Título *Sucursales*. CRUD sucursales para admin, lectura para usuario. Las sucursales existen exclusivamente como unidades de inventario físico, no como unidades organizativas de personal ni financieras.
12. **Caja**. Visible únicamente para rol admin. Título *Movimientos de Caja*. Vista de movimientos de caja globales de la empresa, sin filtro ni segmentación por sucursal. Registrar ingreso/retiro manual.
13. **Configuración Fiscal**. Visible únicamente para rol admin. Título *Configuración Fiscal*. Datos fiscales de la empresa (RFC, régimen, Certificado de Sello Digital). Configuración de conexión al PAC (credenciales de API). Catálogo de series y folios de facturación.
14. **Facturación**. Título *Facturación*. Lista de facturas (CFDI), filtrable por estado, fecha y cliente. Generar factura a partir de una venta existente — requiere datos fiscales completos del cliente. Acción de timbrar (llamada al PAC). Cancelar factura, con selección de motivo según catálogo del SAT y espera de aceptación del receptor. Descarga de XML (documento con validez fiscal) y PDF (representación visual). Registro de Complemento de Pago para facturas con método de pago en parcialidades (PPD).
15. **Contabilidad**. Título *Contabilidad*. Catálogo de cuentas contables, CRUD únicamente para rol admin. Libro diario: lista de asientos contables generados automáticamente a partir de ventas, compras y movimientos de caja, filtrable por fecha, cuenta y origen. Balance de comprobación: sumas y saldos por cuenta contable. Exportación de información en formato compatible para el contador externo de la empresa.
16. **Información del usuario**. Título *Información de Usuario*. Posibilidad de cambiar datos del usuario, con modal de confirmación final *¿Estás seguro?*.

## Para quién

- Empresa *FleboSil*, tanto para empleados comunes como para managers principales de la empresa.

## Principios

- **Trazabilidad total** — ningún movimiento financiero o de inventario se edita ni se borra; se corrige con un movimiento inverso registrado.
- **El backend es la única fuente de verdad de permisos** — el frontend oculta opciones por experiencia de usuario, nunca por seguridad. Cualquier validación de rol se hace cumplir en la API.
- **Simplicidad sobre escalabilidad prematura** — cada decisión técnica se evalúa por costo de mantenimiento primero, dado que hay un único desarrollador y mantenedor a largo plazo.
- **Precisión financiera no negociable** — todo campo monetario o de cantidad de inventario usa `Decimal`, nunca tipos de punto flotante.
- **La sucursal es una dimensión de inventario, no de negocio** — ganancias, caja y personal se gestionan a nivel empresa; solo el stock físico y sus movimientos se segmentan por sucursal.
- **Separación entre operación y responsabilidad fiscal** — el sistema genera y timbra CFDI mediante un PAC certificado, pero no asume responsabilidad legal de la información contable; esa responsabilidad sigue siendo del contador de la empresa.

## Qué NO es

- El proyecto es únicamente para uso de la empresa, no es para el público general.
- No es un sistema multiempresa — está diseñado exclusivamente para FleboSil.
- No reemplaza al contador certificado ni genera estados financieros formales (balance general, estado de resultados, declaraciones fiscales) — genera el libro diario y balance de comprobación que sirven de insumo para ese proceso, realizado por el contador externo de la empresa.
- No opera de forma independiente de terceros regulados — la emisión de CFDI depende de un PAC (Proveedor Autorizado de Certificación) externo; el sistema no timbra comprobantes fiscales por sí mismo.
- No procesa pagos en línea — los movimientos de caja son registro manual de efectivo/transferencias ya realizadas por fuera del sistema.
- No es una aplicación de acceso público — no tiene e-commerce, catálogo público, ni registro abierto de usuarios.
- No trata la sucursal como unidad financiera ni administrativa — no hay reportes de ganancias por sucursal, ni personal asignado de forma fija a una sucursal.