# 018 · Contabilidad

**Estado:** propuesta

## Qué hace

Permite al administrador gestionar el catálogo de cuentas contables de la empresa, y consultar el libro diario (asientos contables generados automáticamente a partir de ventas, compras y movimientos de caja) y el balance de comprobación (sumas y saldos por cuenta). Ofrece exportación de esta información en un formato utilizable por el contador externo de la empresa. No genera estados financieros formales ni sustituye la responsabilidad del contador certificado.

## Por qué

Da a la empresa un puente estructurado entre su operación diaria (ya registrada en Ventas, Compras y Caja) y el proceso contable formal que realiza un tercero externo, sin que el sistema asuma responsabilidad legal sobre esa información. Se construye al final del roadmap porque depende de que todas las fuentes de datos (Ventas, Compras, Caja) ya existan y generen movimientos reales que puedan traducirse a asientos contables.

## Criterios de aceptación

- [ ] Esta vista es visible únicamente para el rol admin, tanto en el sidebar como en sus endpoints.
- [ ] El admin puede crear, editar y desactivar cuentas contables, cada una con código, nombre y tipo (activo/pasivo/capital/ingreso/egreso), con soporte de jerarquía [CONTENIDO TRUNCADO EN EL ARCHIVO ORIGINAL — pendiente de completar, no reescrito para no inventar criterios]
- [ ] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.