# FleboSil · Enterprise Manager

Sistema de gestión empresarial (ERP) de **FleboSil**: ventas, compras, producción, inventario por sucursal, caja, catálogo, terceros, recursos humanos y nómina, facturación electrónica (CFDI 4.0 vía PAC), contabilidad básica, reportes y usuarios con roles.

- **Frontend:** `erp.flebosil.com` · **API:** `api.erp.flebosil.com` · **Correo:** `no-reply@notificaciones.flebosil.com`
- `flebosil.com` y `www.flebosil.com` quedan reservados para el sitio web y la tienda en línea; el DNS del dominio vive en Cloudflare.

## Contenido

- [Módulos](#módulos)
- [Tecnologías](#tecnologías)
- [Estructura](#estructura)
- [Desarrollo local](#desarrollo-local)
- [Pruebas y calidad](#pruebas-y-calidad)
- [Comandos de administración](#comandos-de-administración)
- [Producción](#producción)
- [Respaldos](#respaldos)
- [Reglas del dominio](#reglas-del-dominio)

## Módulos

| Módulo | Qué hace |
|---|---|
| Dashboard | Resumen de ganancias, ventas contra compras y accesos directos. |
| Ventas | Ventas por sucursal, ticket en PDF y paso a facturación. |
| Compras | Compras de producto o materia prima hacia una sucursal. |
| Producción | Recetas y producciones que consumen materia prima. |
| Inventario | Existencias por sucursal, traslados e historial de movimientos. |
| Catálogo | Productos, materia prima y categorías. |
| Terceros | Clientes (con datos fiscales) y proveedores. |
| RRHH | Empleados, puestos y nómina. |
| Caja | Movimientos de caja globales e ingresos o retiros manuales (solo admin). |
| Facturación | Timbrado, cancelación, XML/PDF y complementos de pago. |
| Contabilidad | Catálogo de cuentas, libro diario y balance de comprobación (solo admin). |
| Configuración fiscal | Datos fiscales, conexión al PAC, series y folios (solo admin). |
| Reportes | Ventas, compras, productos y clientes principales, caja y facturación. |
| Usuarios | Altas, roles (admin / operador) e historial de accesos. |

Las sucursales solo separan el **inventario**. Caja, ganancias y personal son globales a la empresa.

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12, Django 6, Django REST Framework, JWT (simplejwt) |
| Base de datos | PostgreSQL 16 |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS 4, React Query, React Router |
| Pruebas | pytest + pytest-django · Vitest + React Testing Library |
| Producción | Railway (backend, PostgreSQL, Volume) · Cloudflare Pages (frontend) · Resend (correo) · Cloudflare R2 (respaldos) |

## Estructura

```
code/
├── requirements.txt         dependencias de producción del backend
├── requirements-dev.txt     + pruebas y lint
├── .python-version          Python 3.12 (Railway)
├── backend/                 Django
│   ├── config/              settings, urls, wsgi
│   ├── core/                permisos, errores JSON, IP del cliente, correo por Resend
│   ├── apps/                una app por módulo (ventas, caja, inventario, …, respaldos)
│   ├── scripts/             respaldo local en Windows (PowerShell)
│   ├── railway.json         despliegue del backend
│   └── railway.respaldos.json + Dockerfile.respaldos   trabajo programado de respaldos
└── frontend/                React + Vite
    └── src/
        ├── api/             una función por endpoint
        ├── hooks/           React Query por entidad
        ├── components/      comunes (Tabla, Modal, …) y layout
        ├── pages/           una carpeta por módulo
        └── index.css        tokens de diseño y clases globales
```

## Desarrollo local

### Requisitos

- Python 3.12 (por ejemplo, un entorno conda)
- PostgreSQL 16
- Node.js 22

### Backend

```bash
cd code/backend
pip install -r ../requirements-dev.txt
cp .env.example .env          # llenar SECRET_KEY, FISCAL_ENCRYPTION_KEY, DB_*, ADMIN_PASSWORD
python manage.py migrate
python manage.py createcachetable
python manage.py asegurar_admin
python manage.py runserver    # http://localhost:8000
```

En `.env.example` se explica cada variable y cómo generar las claves. Sin `EMAIL_HOST` ni `RESEND_API_KEY`, los correos (por ejemplo, la recuperación de contraseña) se imprimen en la consola.

### Frontend

```bash
cd code/frontend
npm install
cp .env.example .env          # VITE_API_URL=http://localhost:8000/api
npm run dev                   # http://localhost:5173
```

El backend acepta por defecto el origen `http://localhost:5173` (`CORS_ALLOWED_ORIGINS`).

### Usuario administrador

`admin@flebosil.com` siempre existe: `asegurar_admin` lo crea o lo restaura con la contraseña de `ADMIN_PASSWORD`. No se puede modificar ni desactivar desde la app ni desde el admin de Django; solo se pueden editar su nombre y su foto.

## Pruebas y calidad

```bash
# backend (code/backend)
pytest
ruff check .

# frontend (code/frontend)
npm run test
npm run lint
npx tsc -b
npm run build
```

## Comandos de administración

| Comando | Para qué |
|---|---|
| `asegurar_admin` | Crea o restaura el administrador protegido. Corre en cada despliegue. |
| `importar_datos_iniciales --ventas <xlsx> --inventario <xlsx> --usuario <correo> [--simular]` | Carga histórica inicial en una base vacía. Todo o nada; con `--simular` deshace la carga al final. |
| `respaldar --destino r2\|local` | Respaldo cifrado de la base y rotación de los anteriores. |
| `restaurar_respaldo <archivo> --base <nombre>` | Restaura un respaldo en una base vacía. |
| `descifrar_respaldo <archivo> --salida <ruta>` | Descifra un respaldo de la base o de una factura. |
| `subir_facturas_pendientes [--descargar]` | Sube a R2 las facturas que falten, o las descarga a la carpeta local. |

Todos se corren con `python manage.py <comando>` desde `code/backend`.

## Producción

### Backend en Railway

- **Servicio:** root directory `code` (ahí están `requirements.txt` y `.python-version`; los comandos entran a `backend/`) y config file `/code/backend/railway.json`. Un Volume montado en `/data` y PostgreSQL **16** en el mismo proyecto (fijar la etiqueta `:16` de la imagen: los respaldos usan `pg_dump` 16).
- **En cada despliegue:** `migrate`, `createcachetable` y `asegurar_admin`. Luego `collectstatic`, la subida de facturas pendientes y Gunicorn. Railway espera a que `/salud/` responda antes de pasarle tráfico.
- **Variables:** las de `.env.example`, con valores de producción:
  - `DEBUG=False`
  - `ALLOWED_HOSTS=api.erp.flebosil.com`
  - `CSRF_TRUSTED_ORIGINS=https://api.erp.flebosil.com`
  - `CORS_ALLOWED_ORIGINS=https://erp.flebosil.com`
  - `NUM_PROXIES=1`
  - `DB_*` como referencias a Postgres (`${{Postgres.PGHOST}}`, …)
  - `MEDIA_ROOT`, `EMPLEADOS_FOTOS_ROOT` y `USUARIOS_FOTOS_ROOT` dentro de `/data`
  - `RESEND_API_KEY` y `DEFAULT_FROM_EMAIL`
  - `ADMIN_PASSWORD` fuerte, distinta a la local
  - `SECRET_KEY` y `FISCAL_ENCRYPTION_KEY` propias de producción
- **Dominio de la API:** `api.erp.flebosil.com` va en Cloudflare DNS como **DNS only** (nube gris). Es de dos niveles y el certificado gratuito de Cloudflare solo cubre uno; el certificado lo emite Railway.
- **Correo:** sale por la API HTTP de Resend, con `notificaciones.flebosil.com` verificado en Resend.

### Frontend en Cloudflare Pages

- Root directory `code/frontend`, build `npm run build`, salida `dist`.
- Variable `VITE_API_URL=https://api.erp.flebosil.com/api`. Se lee al compilar: si cambia, hay que volver a desplegar.
- Dominio `erp.flebosil.com`. Pages sirve `index.html` en cualquier ruta, así que recargar `/ventas` funciona.

### Carga inicial de datos

Se corre desde un equipo local con los xlsx, que no están en el repositorio. Los `DB_*` apuntan a la conexión pública de la base de Railway, definidos solo en esa terminal y nunca en `.env`:

```bash
python manage.py importar_datos_iniciales --ventas "VENTAS 2025 - corregido.xlsx" \
  --inventario "INVENTARIO PRODUCTOS FleboSil - corregido.xlsx" --usuario admin@flebosil.com --simular
```

Si el resumen coincide, se vuelve a correr sin `--simular`.

## Respaldos

Cada **domingo a las 3:00** (hora de la Ciudad de México), la base se respalda cifrada con `RESPALDO_PASSWORD` en dos lugares:

1. **Cloudflare R2:** servicio programado de Railway con root `code`, config file `/code/backend/railway.respaldos.json` y las mismas variables que el backend más `R2_*` y `RESPALDO_AVISO_EMAIL`.
2. **Equipo local (Windows):** copiar `code/backend/.env.respaldo.example` a `.env.respaldo`, llenarlo y luego:
   ```powershell
   cd code\backend\scripts
   .\respaldar_local.ps1              # prueba manual; registro en <carpeta>\respaldos.log
   .\instalar_tarea_respaldo.ps1      # tarea semanal
   .\instalar_tarea_respaldo.ps1 -Pausar | -Reanudar | -Estado | -Ahora | -Quitar
   ```

**Qué se conserva:** los 12 respaldos semanales más recientes y el primero de cada mes durante 12 meses, en cada destino. Los XML y PDF de las facturas se copian cifrados a R2 al timbrarse y no rotan. Las fotos no se respaldan.

**Si un respaldo falla,** no se borra ninguno anterior y llega un aviso por correo.

> Guarda `RESPALDO_PASSWORD` en un gestor de contraseñas: sin ella, ningún respaldo se puede abrir.

**Restaurar** (siempre en una base nueva y vacía):

```bash
python manage.py restaurar_respaldo flebosil_AAAA-MM-DD_HHMM.dump.cifrado --base flebosil_restaurada
```

## Reglas del dominio

- **Movimientos que no se editan:** los de caja y de inventario nunca se editan ni se borran. Se corrigen con un movimiento inverso.
- **Existencias:** solo cambian a través de un movimiento de inventario. Las escrituras usan `select_for_update()` y `transaction.atomic()`.
- **Dinero y cantidades:** siempre `Decimal`.
- **Precios congelados:** el precio y el costo quedan fijos en el detalle de cada venta o compra.
- **Permisos y validación:** los permisos se revisan en el backend y los serializers de DRF son la única validación de entrada.
- **Errores de la API:** siempre en JSON `{"detail": "..."}`.
- **Borrado lógico:** los catálogos se desactivan (`activo`) en vez de borrarse.
- **Secretos:** ninguna credencial va al repositorio (`.env`, `.env.respaldo`, respaldos y datos están en `.gitignore`).
