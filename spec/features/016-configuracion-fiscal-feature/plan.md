# 016 · configuracion-fiscal — Plan

## Enfoque

Configuración global de la empresa (no por sucursal, no por usuario) almacenada en un modelo singleton-like: se asume una sola fila de configuración fiscal y una sola configuración de PAC activa a la vez, ya que el sistema sirve a una sola empresa (FleboSil), consistente con "Qué NO es: no es un sistema multiempresa". Las credenciales sensibles del PAC se almacenan cifradas, nunca en texto plano en la base de datos.

## Implementación

1. Backend — crear modelo `DatosFiscalesEmpresa` en `backend/apps/configuracion_fiscal/models.py`: `rfc`, `razon_social`, `regimen_fiscal`, `codigo_postal_fiscal` — con restricción de que solo debe existir una fila (validación a nivel de aplicación, ej. `get_or_create` con id fijo).
2. Backend — crear modelo `ConfiguracionPAC`: `proveedor` (nombre del PAC), `api_key` (almacenado cifrado, usando `django-cryptography` o cifrado manual con una clave de entorno), `api_endpoint`, `activo`.
3. Backend — crear modelo `SerieFolio`: `serie`, `folio_actual` (entero), `activo`.
4. Backend — crear migraciones de los tres modelos.
5. Backend — crear serializers: el de `ConfiguracionPAC` nunca devuelve `api_key` en texto plano en las respuestas de lectura (se enmascara o se omite), solo acepta escritura.
6. Backend — crear ViewSets/vistas restringidas exclusivamente a rol admin para los tres modelos.
7. Backend — implementar la lógica de cifrado/descifrado de `api_key` (cifrado al guardar, descifrado solo internamente cuando `017 · Facturación` necesite usarlo para llamar al PAC — nunca expuesto vía API de lectura).
8. Backend — implementar validación de que no se pueda desactivar/eliminar una `SerieFolio` con `folio_actual > 0` (folios ya usados) salvo desactivación (soft delete, mismo patrón ya establecido).
9. Backend — registrar rutas en el router principal, protegidas para admin.
10. Frontend — crear `frontend/src/api/configuracionFiscal.ts` con funciones de consulta/actualización de los tres recursos.
11. Frontend — crear `frontend/src/hooks/useConfiguracionFiscal.ts` con React Query.
12. Frontend — crear `frontend/src/pages/ConfiguracionFiscal/ConfiguracionFiscal.tsx`: formulario de datos fiscales de la empresa, formulario de conexión al PAC (con campo de API key enmascarado tipo password), tabla de series/folios con alta/edición.
13. Frontend — implementar el indicador visual de "configuración incompleta" si falta algún dato fiscal o credencial del PAC.
14. Frontend — agregar la ruta `/configuracion-fiscal` en `App.tsx`, protegida exclusivamente para admin.

## Decisiones

- **Modelos tratados como singleton (una sola fila activa), no una tabla de configuraciones múltiples** — consistente con que el sistema sirve a una sola empresa; evita complejidad innecesaria de selección de "cuál configuración usar" que nunca se necesitará en este contexto.
- **`api_key` del PAC cifrada en base de datos, no en texto plano** — es una credencial de alto riesgo: si la base de datos se ve comprometida, una credencial en texto plano expondría directamente la capacidad de timbrar facturas fiscales a nombre de la empresa.
- **`api_key` nunca devuelta en respuestas de lectura, ni siquiera al admin** — mismo principio ya aplicado a contraseñas de usuario en `008`: una vez guardado un secreto, la interfaz nunca debe mostrarlo de vuelta, solo permitir sobrescribirlo.
- **Restricción total a rol admin, sin excepción de lectura para operador** — a diferencia de Catálogo/Sucursales (que sí permiten lectura a operador), esta configuración contiene credenciales sensibles que no deben ser visibles ni siquiera en modo lectura para un rol no administrativo.

## Riesgos

- **Gestión de la clave de cifrado de `api_key`** — si la clave usada para cifrar se pierde o se rota sin plan de migración, las credenciales guardadas quedarían irrecuperables; mitigación: almacenar la clave de cifrado como variable de entorno (`.env`, ya excluido del repositorio según límites duros del tech-stack) y documentar el proceso de rotación antes de implementarlo en producción.
- **Definir la estructura exacta de credenciales sin conocer aún qué PAC específico se va a contratar** — distintos PACs (Facturama, SW, Bind) pueden requerir campos ligeramente distintos (algunos piden usuario+contraseña además de API key); mitigación: diseñar `ConfiguracionPAC` con un campo adicional `configuracion_extra` (JSON) para credenciales específicas del proveedor elegido, sin necesitar una migración nueva si cambia el PAC contratado.
- **Confusión entre "configuración incompleta" y "configuración con error real de conexión"** — mitigación: esta feature solo valida completitud de campos, no conectividad real (ya documentado como fuera de alcance); dejar claro en el mensaje de la interfaz que "incompleta" no implica "probada y funcional".