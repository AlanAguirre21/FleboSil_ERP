# 014 · dashboard — Plan

## Enfoque

Feature puramente de lectura agregada — no crea modelos nuevos, solo endpoints de agregación sobre `Ventas`, `Compras` y `MovimientosCaja` ya existentes. Backend: un endpoint de resumen que recibe el periodo como parámetro y devuelve totales ya calculados (agregación con el ORM de Django, no traer todas las filas al frontend). Frontend: página con selector de periodo, tarjetas de totales, gráfica con `recharts`, y dos botones de acceso directo con React Router.

## Implementación

1. Backend — crear vista `GET /api/reportes/resumen/?periodo=dia|semana|mes` en `backend/apps/reportes/views.py` (nueva app, ya contemplada en la estructura de carpetas original).
2. Backend — implementar la agregación: `Ventas.objects.filter(fecha__range=..., estado__in=['entregada','pendiente']).aggregate(Sum('total'))` y equivalente para `Compras`, calculando la ganancia como la resta de ambos totales.
3. Backend — para la gráfica, devolver una serie de puntos (ej. ganancia por día dentro del periodo seleccionado), no solo el total agregado — necesario para que `recharts` pueda dibujar la evolución.
4. Backend — decidir y documentar qué estados de venta/compra cuentan para el cálculo (ej. una venta `cancelada` no debe sumar a ganancias, una `pendiente` sí porque el stock y caja ya se afectaron al registrarla, según lo definido en `011`).
5. Frontend — crear `frontend/src/api/reportes.js` con la función de consulta del resumen.
6. Frontend — crear `frontend/src/hooks/useResumenDashboard.js` con React Query, parametrizado por periodo, con `staleTime` corto para reflejar cambios recientes de Ventas/Compras.
7. Frontend — crear `frontend/src/pages/Dashboard/Dashboard.jsx`: selector de periodo, tarjetas de "Ventas totales" / "Compras totales" / "Ganancia", gráfica con `recharts`, botones de acceso directo.
8. Frontend — crear `frontend/src/pages/Dashboard/Dashboard.module.css`.
9. Frontend — configurar la ruta raíz autenticada (`/` o `/dashboard`) en `App.jsx` para que apunte aquí tras login exitoso.
10. Frontend — implementar estado vacío (ilustración o mensaje simple) cuando la agregación devuelve ceros o listas vacías.

## Decisiones

- **Agregación calculada en el backend con el ORM, no en el frontend trayendo todas las filas** — con el volumen de datos creciendo con el tiempo, traer todas las ventas/compras al cliente para sumarlas en JavaScript no escala y expone más datos de los necesarios; el backend siempre debe devolver totales ya calculados.
- **`staleTime` corto en el hook del dashboard** — a diferencia de otros módulos más estáticos (Catálogo, Sucursales), el dashboard debe reflejar rápidamente una venta recién registrada, consistente con el criterio de aceptación de actualización sin recarga manual.
- **Nueva app `reportes` en vez de agregar estas vistas dentro de `ventas` o `compras`** — mantiene la separación de responsabilidades ya definida en la estructura de carpetas original del tech-stack; los reportes cruzan múltiples dominios (ventas + compras), no pertenecen exclusivamente a uno.
- **Gráfica con `recharts`** — ya definida como librería disponible en el stack de React desde el inicio de la conversación; se descarta introducir una librería de gráficas nueva solo para esta feature.

## Riesgos

- **Definición ambigua de qué estados de venta/compra cuentan para "ganancia"** — mitigación: se documenta explícitamente en el paso 4 de implementación como algo a decidir y fijar en código con un comentario claro, no dejarlo implícito en la lógica de agregación donde sería fácil de malinterpretar después.
- **La gráfica podría verse vacía o poco útil en las primeras semanas de uso real de la empresa, antes de acumular suficientes datos** — mitigación: el estado vacío ya contemplado en la spec cubre este caso, mostrando un mensaje en vez de una gráfica confusa con muy pocos puntos.
- **Consultas de agregación lentas si el volumen de ventas/compras crece significativamente sin índices adecuados sobre `fecha`** — mitigación: agregar índice sobre `fecha` en `Ventas` y `Compras` si aún no existe desde sus respectivas migraciones.