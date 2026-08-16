# 008 · personas — Plan

## Enfoque

Cuatro ViewSets de DRF (`ClienteViewSet`, `ProveedorViewSet`, `EmpleadoViewSet`, `UsuarioViewSet`), con dos niveles de permiso distintos: Clientes/Proveedores abiertos a escritura para cualquier autenticado, Empleados/Usuarios restringidos a admin — reutilizando y extendiendo la clase de permisos ya definida en `006`/`007`. El modelo `Usuario` ya existe parcialmente desde `003 · Login`; aquí se completa con el CRUD administrativo y la relación opcional con `Empleado`. Frontend: misma estructura de selector de pestañas que `007 · Catálogo`, reutilizando `Tabla` y `Modal`.

## Implementación

1. Backend — crear modelo `Cliente` en `backend/apps/personas/models.py`: `nombre`, `telefono`, `email`, `direccion`, `activo`.
2. Backend — crear modelo `DatosFiscalesCliente`: `cliente_id` (FK 1:1), `rfc`, `razon_social`, `codigo_postal_fiscal`, `regimen_fiscal`, `uso_cfdi_default`, `requiere_factura` (booleano).
3. Backend — crear modelo `Proveedor`: `nombre`, `rfc`, `contacto_nombre`, `telefono`, `email`, `direccion`, `activo`.
4. Backend — crear modelo `Empleado`: `nombre_completo`, `puesto`, `telefono`, `email`, `fecha_contratacion`, `salario` (Decimal), `activo`.
5. Backend — extender el modelo `Usuario` (creado en `003`) agregando `empleado_id` (FK nullable a `Empleado`), si no se incluyó desde esa feature.
6. Backend — completar la migración pendiente de `MateriaPrima.proveedor_principal_id` (declarada como FK diferida en `007 · Catálogo`), apuntando ya al modelo `Proveedor` recién creado.
7. Backend — crear serializers y ViewSets de los cuatro modelos: `ClienteViewSet`/`ProveedorViewSet` con permiso "cualquier autenticado puede escribir"; `EmpleadoViewSet`/`UsuarioViewSet` reutilizando el permiso "solo admin escribe" de `006`/`007`.
8. Backend — en `ClienteSerializer`, validar que si `requiere_factura=True`, los campos de `DatosFiscalesCliente` estén completos antes de permitir el guardado.
9. Backend — en `UsuarioSerializer`, manejar el hasheo de contraseña en la creación (`set_password()`, nunca asignar el campo directo), y excluir el campo de contraseña de cualquier respuesta de lectura.
10. Backend — verificar que el middleware/permiso de autenticación valide `activo=True` en cada petición autenticada (no solo en login), para que desactivar a un usuario surta efecto de inmediato.
11. Frontend — crear `frontend/src/api/personas.ts` con funciones CRUD de los cuatro tipos.
12. Frontend — crear hooks `useClientes.ts`, `useProveedores.ts`, `useEmpleados.ts`, `useUsuarios.ts` con React Query.
13. Frontend — crear `frontend/src/pages/Personas/Personas.tsx` con selector de pestañas (Clientes / Proveedores / Empleados / Usuarios).
14. Frontend — formulario de Cliente con sección colapsable de "Datos fiscales", visible/obligatoria solo si se marca "requiere factura".
15. Frontend — formulario de Usuario con selector de Empleado existente (opcional) y campo de contraseña solo visible en creación, nunca en edición (para editar contraseña se redirige al flujo de recuperación, no se reescribe aquí).
16. Frontend — ocultar botones de escritura de Empleados y Usuarios si `rol !== 'admin'`; Clientes y Proveedores muestran escritura para cualquier rol.
17. Frontend — agregar la ruta `/personas` en `App.tsx`.

## Decisiones

- **Clientes y Proveedores sin restricción de rol para escritura, a diferencia de Empleados/Usuarios** — reflejan operación diaria real (un operador necesita poder registrar un cliente nuevo en el momento de una venta); Empleados y Usuarios son administrativos por naturaleza, alineado con Sucursales y Catálogo.
- **Contraseña editable solo en creación de Usuario, no en edición desde este formulario** — evita reintroducir un canal alterno para cambiar contraseñas que evada el flujo ya definido (`004`/`005`) y sus validaciones de seguridad (throttling, hash, etc.).
- **Validación de `activo` en cada petición autenticada, no solo en login** — decisión de seguridad explícita: sin esto, desactivar a un usuario no tendría efecto inmediato si su JWT sigue vigente, dejando una ventana de acceso indebido hasta que expire el token.
- **`DatosFiscalesCliente` como tabla separada en vez de campos directos en `Cliente`** — la mayoría de los clientes no van a requerir factura; separar evita que el formulario básico de cliente se sienta sobrecargado con campos fiscales que casi nunca se usan.

## Riesgos

- **Migrar la FK diferida de `MateriaPrima.proveedor_principal_id` podría fallar si ya existen registros de materia prima sin proveedor asignado y el campo se define como no-nullable por error** — mitigación: confirmar explícitamente que el campo es `null=True, blank=True` antes de aplicar la migración.
- **Un usuario podría quedar sin poder editarse su propia información básica si el CRUD de Usuario queda 100% restringido a admin** — mitigación: este comportamiento es intencional (la edición de datos propios vive en `016 · Información de Usuario`, no aquí); documentar la distinción para no duplicar lógica entre ambas features.
- **Desactivar un usuario que tiene sesión activa podría no reflejarse de inmediato si el frontend cachea la respuesta del endpoint `/api/usuarios/me/` con un `staleTime` largo** — mitigación: mantener `staleTime` corto para ese hook específico, o invalidar la cache activamente cuando el backend responda `401` por usuario inactivo.