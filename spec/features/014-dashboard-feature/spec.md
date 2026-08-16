# 014 · Dashboard

**Estado:** propuesta

## Qué hace

Es la vista principal de la aplicación, mostrada tras iniciar sesión. Presenta el resumen de ganancias globales de la empresa (día, semana, mes) con una gráfica simple y sus valores numéricos, sin segmentación por sucursal. Muestra también el total de ventas contra el total de compras del periodo seleccionado. Incluye accesos directos a "Nueva venta" y "Nueva compra" para agilizar las acciones más frecuentes del sistema.

## Por qué

Es el primer punto de contacto del usuario con el estado real del negocio, y depende de que Ventas, Compras y Caja ya generen datos reales — por eso se construye al final del bloque operativo, no al inicio, a pesar de ser la pantalla que aparece primero al navegar. Un dashboard construido antes de tener datos reales solo podría mostrarse con datos ficticios, sin valor de validación real.

## Criterios de aceptación

- [ ] Al iniciar sesión exitosamente, el usuario es dirigido a esta pantalla.
- [ ] Se muestra el título "Resumen FleboSil".
- [ ] Existe un selector de periodo (día / semana / mes) que recalcula los datos mostrados sin recargar la página.
- [ ] La ganancia del periodo se calcula como `total de ventas − total de compras` del periodo seleccionado, a nivel global de la empresa (sin filtro de sucursal).
- [ ] Se muestra una gráfica simple (de línea o barras) representando la evolución de ganancias dentro del periodo seleccionado.
- [ ] Se muestran los totales numéricos de ventas y compras del periodo, uno junto al otro para comparación directa.
- [ ] Existen dos accesos directos visibles: "Nueva venta" (redirige al formulario de `011 · Ventas`) y "Nueva compra" (redirige al formulario de `010 · Compras`).
- [ ] Si aún no hay datos suficientes para el periodo seleccionado (ej. la empresa apenas empieza a operar), se muestra un estado vacío claro, no una gráfica rota ni un error.
- [ ] Cualquier usuario autenticado puede ver este dashboard, sin restricción de rol — es la pantalla de entrada general del sistema.
- [ ] Los datos del dashboard se actualizan (sin recargar manualmente) al volver a esta pantalla después de registrar una venta o compra desde otro módulo.
- [ ] El frontend de esta feature está implementado en TypeScript (`.tsx` para componentes, `.ts` para lógica sin JSX), pasando `npx tsc --noEmit` sin errores, según lo definido en `constitution/tech-stack.md`.

## Fuera de alcance

- No incluye desglose de ganancias por sucursal — ya definido en la constitución del proyecto: la sucursal es una dimensión de inventario, no de negocio.
- No incluye métricas de margen por producto — corresponde a la idea de backlog ya documentada ("Reportes de margen por producto"), no a esta feature.
- No incluye alertas de stock — esas ya viven en el dropdown de notificaciones del Header (`001`), este dashboard no las duplica.