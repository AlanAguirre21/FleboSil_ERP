# 008 · Personas

**Estado:** propuesta

## Qué hace

Permite gestionar las cuatro entidades de persona del sistema mediante una vista con selector: Clientes, Proveedores, Empleados y Usuarios. Clientes y Proveedores admiten CRUD sin restricción de rol (cualquier usuario autenticado puede crear/editar, por ejemplo al registrar un cliente nuevo durante una venta). Empleados y Usuarios son de solo lectura para el rol operador; solo el admin puede crear, editar o desactivar. Los empleados son globales a la empresa, sin asociación a una sucursal específica. El formulario de Clientes incluye una sección de datos fiscales (RFC, razón social, código postal fiscal, régimen fiscal, uso de CFDI), obligatoria únicamente si el cliente va a recibir factura.

## Por qué

Es prerrequisito de Ventas (necesita Clientes), Compras (necesita Proveedores) y Producción/Inventario indirectamente (Materia Prima ya referencia `proveedor_principal_id`, definido como FK pendiente en la feature anterior). Además, es donde vive la gestión real de acceso al sistema — dar de alta o desactivar un usuario — que hasta ahora solo existía como registro necesario para que Login funcionara, sin interfaz de administración.

## Criterios de aceptación

- [ ] Existe un selector para alternar entre Clientes, Proveedores, Empleados y Usuarios, sin recargar la página.
- [ ] CRUD de Clientes: cualquier usuario autenticado puede crear, editar y desactivar. Incluye datos fiscales opcionales (obligatorios solo si se marca "requiere factura").
- [ ] Si el cliente requiere factura, el backend valida que RFC, razón social, código postal fiscal y régimen fiscal estén completos antes de permitir guardar esa marca como verdadera.
- [ ] CRUD de Proveedores: cualquier usuario autenticado puede crear, editar y desactivar, con los mismos campos base (nombre, RFC, contacto, teléfono, email, dirección).
- [ ] CRUD de Empleados: solo admin puede crear, editar y desactivar; operador solo consulta. Campos: nombre completo, puesto, teléfono, email, fecha de contratación, salario, activo.
- [ ] CRUD de Usuarios: solo admin puede crear, editar y desactivar; operador solo consulta (sin ver contraseñas ni hashes, obviamente). Al crear un usuario, se puede vincular opcionalmente a un empleado existente mediante un selector.
- [ ] La contraseña de un usuario nuevo se genera o se define en el alta, y se almacena únicamente como hash — nunca se muestra en texto plano en ninguna pantalla, ni siquiera al admin.
- [ ] Desactivar un cliente, proveedor o empleado no elimina físicamente el registro ni rompe referencias en ventas, compras o nómina históricas — solo deja de aparecer como opción seleccionable en formularios nuevos.
- [ ] Desactivar un usuario (`activo=false`) le impide iniciar sesión de inmediato, incluso si su sesión JWT actual aún no ha expirado (el backend valida `activo` en cada petición autenticada, no solo al momento del login).
- [ ] El backend rechaza cualquier intento de escritura sobre Empleados o Usuarios desde un rol operador, incluso llamando directo a la API.

## Fuera de alcance

- No incluye el envío de factura al cliente — corresponde a `017 · Facturación`, que consumirá los datos fiscales capturados aquí.
- No incluye gestión de nómina o pagos a empleados — el campo `salario` es informativo, no genera movimientos de caja automáticos.
- No incluye recuperación de contraseña de otro usuario por parte del admin — el flujo de recuperación (`004`/`005`) es siempre autoservicio del propio usuario mediante su correo.