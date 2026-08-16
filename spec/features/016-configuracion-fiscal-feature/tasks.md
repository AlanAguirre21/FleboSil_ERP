# 016 · Configuración Fiscal — Tareas

- [ ] Crear modelo `DatosFiscalesEmpresa` y su migración.
- [ ] Crear modelo `ConfiguracionPAC` (con campo `configuracion_extra` JSON) y su migración.
- [ ] Crear modelo `SerieFolio` y su migración.
- [ ] Implementar cifrado/descifrado de `api_key` usando una clave de entorno (`.env`).
- [ ] Crear serializers, asegurando que `api_key` nunca se devuelve en texto plano en lectura.
- [ ] Crear vistas/ViewSets restringidos exclusivamente a rol admin para los tres modelos.
- [ ] Implementar validación de que una `SerieFolio` con folios usados solo puede desactivarse, no eliminarse.
- [ ] Registrar rutas en el router principal.
- [ ] Crear `frontend/src/api/configuracionFiscal.ts`.
- [ ] Crear `frontend/src/hooks/useConfiguracionFiscal.ts`.
- [ ] Crear `frontend/src/pages/ConfiguracionFiscal/ConfiguracionFiscal.tsx` con los tres formularios/tablas.
- [ ] Implementar campo de API key enmascarado tipo password en el formulario.
- [ ] Implementar indicador visual de "configuración incompleta".
- [ ] Agregar la ruta `/configuracion-fiscal` en `App.tsx` y el módulo al diccionario "módulo → roles permitidos" (solo admin).
- [ ] Escribir tests de backend: cifrado/descifrado correcto de `api_key`, rechazo de acceso para rol operador, bloqueo de eliminación de serie con folios usados.
- [ ] Escribir tests de frontend: enmascarado del campo de API key, indicador de configuración incompleta, ocultamiento del módulo para operador.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

## Mantenimiento (checklist recurrente)

- [ ] Actualizar `ConfiguracionPAC` con las nuevas credenciales y, si aplica, la estructura de `configuracion_extra` según los requisitos del nuevo proveedor.
- [ ] Verificar que la clave de cifrado de `api_key` sigue vigente y no requiere rotación.