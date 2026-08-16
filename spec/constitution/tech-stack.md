# Tech stack y convenciones

## Tecnologías

- **Lenguaje:** Python 3.12 (backend) + TypeScript 5.x (frontend, target ES2022, `strict: true`, `noUncheckedIndexedAccess: true`)
- **Framework / runtime:** Django 5.x + Django REST Framework (backend) / React 19.2.8 con Vite + Tailwind CSS v4 (`@tailwindcss/vite`, sin `tailwind.config.js`) + CSS Modules (frontend)
- **Base de datos:** PostgreSQL 16, ORM nativo de Django (sin Prisma — no aplica, es exclusivo del ecosistema Node)
- **Tests:** Pytest + pytest-django (backend), Vitest + React Testing Library (frontend)
- **Despliegue:** VPS único (Docker + docker-compose), Gunicorn detrás de Nginx, frontend compilado como estático servido por el mismo Nginx

## Archivos / módulos clave

- `backend/apps/ventas/` — lógica de Ventas y DetalleVenta; punto de origen de movimientos de caja e inventario automáticos.
- `backend/apps/inventario/` — InventarioSucursalProducto/MateriaPrima y MovimientosInventario; toda modificación de stock pasa por aquí, nunca directo desde otra app.
- `backend/apps/produccion/` — Receta y Produccion; ejecuta la transacción atómica de consumo de materia prima + generación de producto.
- `backend/core/permissions.py` — clases de permisos DRF compartidas (validación de rol admin/operador); ninguna vista debe reimplementar esta lógica.
- `frontend/src/api/` — una función por endpoint, agrupada por módulo, en archivos `.ts`; cada módulo exporta también las interfaces TypeScript de su request/response junto a las funciones (sin carpeta `types/` separada); ningún componente llama `axios` directo, siempre pasa por aquí.
- `frontend/src/hooks/` — hooks de React Query por entidad, en archivos `.ts`; centraliza cache y estados de carga/error, tipados a partir de las interfaces exportadas por `api/`.
- `frontend/tsconfig.json` — configuración de TypeScript en modo `strict`, compartida por todo `frontend/src/`; sin path aliases, imports relativos (consistente con la simplicidad ya buscada en el proyecto).
- `frontend/src/index.css` — punto de entrada de Tailwind (`@import "tailwindcss";`) y definición de los tokens de diseño en el bloque `@theme` (colores de marca, colores de estado, tipografía, breakpoints) como variables CSS; todo archivo `.module.css` las consume vía clases de utilidad de Tailwind con `@apply` (ej. `bg-primario`, `text-error`), nunca hardcodea un color directo.
- `frontend/src/components/*/Componente.module.css` — un archivo de estilos por componente, junto a su `.tsx`, con `@reference "<ruta a index.css>"` al inicio para poder usar `@apply`; nunca estilos inline, clases de utilidad de Tailwind directas en el JSX, ni CSS mezclado dentro del JSX.

## Comandos

- `python manage.py runserver` — arranca el backend en local.
- `npm run dev` — arranca el frontend en local (Vite).
- `pytest` — ejecuta los tests del backend.
- `npm run test` — ejecuta los tests del frontend (Vitest).
- `ruff check .` — lint de Python.
- `npm run lint` — lint de TypeScript/React (ESLint + `typescript-eslint`).
- `npx tsc --noEmit` — verificación de tipos sin generar archivos de salida; debe pasar sin errores antes de dar una feature por terminada.
- `python manage.py migrate` — aplica migraciones a la base de datos.
- `npm run build` — compila el frontend para producción.

## Modelo de datos / dominio

- `Decimal`, nunca `Float` — todo campo monetario o de cantidad de inventario.
- `MovimientosCaja` / `MovimientosInventario` — tablas **INSERT-only**; ninguna corrección se hace vía `UPDATE`/`DELETE`, siempre con movimiento inverso.
- `select_for_update()` — obligatorio al leer stock dentro de cualquier transacción que lo modifique (venta, compra, producción), para evitar condiciones de carrera entre usuarios simultáneos.
- `transaction.atomic()` — obligatorio en toda operación que toque más de una tabla relacionada (venta completa, compra completa, producción completa); si un paso falla, se revierte todo.
- Patrón cabecera-detalle — `Ventas`/`DetalleVenta`, `Compras`/`DetalleCompra*` — el precio/costo se congela en el detalle al momento de la transacción, nunca se referencia el precio actual del catálogo.

## Convenciones

- `snake_case` para modelos y campos de Django; `camelCase` para variables y funciones en React/TypeScript.
- TypeScript en modo estricto (`strict: true` en `tsconfig.json`, heredado del scaffold de Vite); `any` solo permitido con un comentario técnico explicando por qué no se pudo tipar (ej. una librería de terceros sin tipos). Componentes React se escriben como `.tsx`; lógica sin JSX (`api/`, `hooks/`, `context/`, utilidades) se escribe como `.ts`.
- Estilos: Tailwind CSS v4 vía `@tailwindcss/vite` (configuración *CSS-first*, sin `tailwind.config.js`) es el framework de utilidades del proyecto. Un archivo `Componente.module.css` por componente, importado como `import styles from './Componente.module.css'` y aplicado vía `className={styles.boton}`; dentro de cada `.module.css` las clases de Tailwind se componen con `@apply`, nunca como className de utilidad directo en el JSX ni como CSS inline.
- Tests junto a la app que prueban: `apps/ventas/tests/test_models.py`, no en carpeta centralizada separada.
- Validación de entrada: los serializers de DRF son la única capa de validación de datos entrantes — nunca confiar en validación solo del frontend.
- Errores de API: siempre responden con estructura JSON consistente (`{"detail": "mensaje"}`), nunca stack traces expuestos en producción (`DEBUG = False`).
- Idioma: interfaz y mensajes de usuario en español; nombres de variables, funciones y modelos en español; comentarios técnicos también en español.

## Estilo visual

- **Paleta de color:** definida como tokens de Tailwind en el bloque `@theme` de `frontend/src/index.css` (variables CSS que Tailwind expone como clases de utilidad, ej. `bg-primario`, `text-error`):
  - `--color-primario` (rosa oscuro) — acciones principales, elementos de marca.
  - `--color-secundario` (verde claro, marca) — distinto del verde de estado, para no generar ambigüedad visual.
  - `--color-fondo` (blanco) — fondo base.
  - `--color-texto` (negro) — tipografía principal, íconos, bordes.
- **Colores de estado (independientes de la paleta de marca), también como tokens `@theme`:**
  - `--color-exito` (verde, tono distinto al de marca) — confirmaciones, stock suficiente, operación completada.
  - `--color-error` (rojo) — validaciones fallidas, stock insuficiente, cancelaciones.
  - `--color-advertencia` (amarillo) — alertas de stock bajo el mínimo, acciones que requieren confirmación.
- **Tipografía:** fuente del sistema, definida como `--font-base` en el bloque `@theme` de `index.css`, aplicada vía la utilidad `font-base` (`@apply font-base` en `body`).
- **Responsive:** breakpoints definidos como tokens `@theme` (`--breakpoint-sm`, `--breakpoint-md`, `--breakpoint-lg`); sidebar colapsable por debajo de `--breakpoint-md`.

## Límites duros

- No usar `FloatField` para dinero ni cantidades de inventario, bajo ninguna circunstancia.
- No editar ni borrar registros de `MovimientosCaja` o `MovimientosInventario` — solo `INSERT`.
- No validar permisos de rol únicamente en el frontend — toda regla de acceso se repite y se hace cumplir en el backend.
- No hacer commit de `.env` ni credenciales del PAC/SMTP al repositorio.
- No añadir librerías nuevas al proyecto sin evaluarlas contra el principio de "simplicidad sobre escalabilidad prematura" definido en la constitución.
- No modificar `stock_actual` directo en una tabla de inventario sin pasar por la lógica de `MovimientosInventario` — cualquier cambio de stock debe quedar auditado.