# 002 · footer — Plan

## Enfoque

Construir el Footer como componente de layout simple (`Footer.tsx` + `Footer.module.css`), sin estado ni llamadas a API — toda la información que muestra (versión, año) es estática o calculada en el cliente, a diferencia del Header que sí depende de datos remotos. Se integra en `MainLayout.tsx`, debajo del `<Outlet />`, junto al Header ya construido en la feature 001.

## Implementación

1. Crear `frontend/src/config/version.ts` — exporta una constante `APP_VERSION = "1.0"`, como fuente única de verdad para no hardcodear el número en el componente.
2. Crear `frontend/src/components/layout/Footer.tsx` — renderiza `APP_VERSION` y el copyright con `new Date().getFullYear()` calculado dinámicamente.
3. Crear `frontend/src/components/layout/Footer.module.css` — estilos discretos (texto pequeño, color de bajo contraste) compuestos con `@apply` de Tailwind (`@reference` a `index.css`) sobre los tokens del `@theme`.
4. Modificar `frontend/src/components/layout/MainLayout.tsx` (creado en la feature 001) para incluir `<Footer />` debajo del `<Outlet />`.

## Decisiones

- **Versión centralizada en un archivo de configuración, no hardcodeada en el componente** — permite actualizar el número de versión en un solo lugar cuando se libere una nueva versión del sistema, en vez de buscarlo dentro del JSX.
- **Año de copyright calculado dinámicamente, no escrito a mano** — evita que el footer muestre un año desactualizado si el proyecto sigue en producción varios años sin que alguien recuerde actualizarlo manualmente.
- **Footer sin estado ni llamadas a API** — se descarta agregar indicador de sincronización o última actualización en esta feature, manteniendo el componente simple; si se requiere después, es una feature aparte que si necesitaría estado.

## Riesgos

- **Olvidar actualizar `APP_VERSION` al liberar cambios significativos, dejando el footer desactualizado** — mitigación: agregar la actualización de este valor como paso explícito en el checklist de release del proyecto (fuera del alcance de esta feature, pero documentado como recordatorio en `tasks.md`).
- **El footer podría quedar oculto detrás de contenido largo en tablas grandes (ej. lista extensa de ventas) si no se maneja el layout con scroll interno correctamente** — mitigación: verificar que `MainLayout` use scroll en el contenedor de contenido, no en la página completa, para que el footer permanezca siempre visible al fondo.
