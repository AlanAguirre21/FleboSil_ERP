# 008 · Personas — Tareas

- [ ] Crear modelo `Cliente` y su migración.
- [ ] Crear modelo `DatosFiscalesCliente` (FK 1:1 a `Cliente`) y su migración.
- [ ] Crear modelo `Proveedor` y su migración.
- [ ] Crear modelo `Empleado` y su migración.
- [ ] Extender modelo `Usuario` con `empleado_id` (FK nullable), si no existe ya desde la feature 003.
- [ ] Completar la migración diferida de `MateriaPrima.proveedor_principal_id` apuntando a `Proveedor`.
- [ ] Crear serializers y ViewSets de `Cliente`, `Proveedor` (permiso: cualquier autenticado escribe).
- [ ] Crear serializers y ViewSets de `Empleado`, `Usuario` (permiso: solo admin escribe).
- [ ] Implementar validación de datos fiscales completos si `requiere_factura=True` en `ClienteSerializer`.
- [ ] Implementar hasheo de contraseña vía `set_password()` en `UsuarioSerializer`, excluyendo el campo de las respuestas de lectura.
- [ ] Verificar/implementar validación de `activo=True` en cada petición autenticada, no solo en login.
- [ ] Registrar rutas de los cuatro recursos en el router principal.
- [ ] Crear `frontend/src/api/personas.js` con funciones CRUD de los cuatro tipos.
- [ ] Crear hooks `useClientes.js`, `useProveedores.js`, `useEmpleados.js`, `useUsuarios.js`.
- [ ] Crear `frontend/src/pages/Personas/Personas.jsx` con selector de pestañas.
- [ ] Implementar sección colapsable de datos fiscales en el formulario de Cliente.
- [ ] Implementar formulario de Usuario con selector de Empleado y campo de contraseña solo en creación.
- [ ] Ocultar botones de escritura de Empleados/Usuarios para rol operador; mantenerlos visibles en Clientes/Proveedores para cualquier rol.
- [ ] Configurar `staleTime` corto en `useUsuarioActual` para reflejar desactivaciones casi de inmediato.
- [ ] Agregar la ruta `/personas` en `App.jsx` y el módulo al diccionario "módulo → roles permitidos".
- [ ] Escribir tests de backend: validación de datos fiscales condicional, hasheo de contraseña, rechazo de escritura de Empleados/Usuarios por operador, usuario desactivado pierde acceso de inmediato.
- [ ] Escribir tests de frontend: cambio entre pestañas, visibilidad condicional de botones por entidad y rol, formulario fiscal condicional.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

_Sin pasos recurrentes identificados para esta feature._