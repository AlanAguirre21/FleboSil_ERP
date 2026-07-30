# Roadmap

Orden y estado de las features. Es la vista de "qué hay hecho, qué toca ahora y qué viene". Cada entrada apunta a su carpeta en `features/`. Consta de 18 features, que conforman la aplicación web; el resto son backlogs que respetan la constitución.

## Hecho ✅


## Siguiente 🔜

1. **001 · Header** — Establece el encabezado general de la aplicación web.
2. **002 · Footer** — Establece el pie de página general para la aplicación web.
3. **003 · Login** — Permite el ingreso del usuario.
4. **004 · Recuperar contraseña** — Permite acceder a la feature de *Cambiar contraseña*.
5. **005 · Cambiar contraseña** — Permite cambiar la contraseña del usuario.
6. **006 · Sucursales** — Vista de sucursales, con manejo según el rol del usuario.
7. **007 · Catálogo** — Vista con CRUD de productos, materia prima y categorías (productos).
8. **008 · Personas** — Vista con selección entre clientes, proveedores, empleados y usuarios.
9. **009 · Inventario** — Vista con los inventarios de productos y materia prima.
10. **010 · Compras** — Vista con lo relacionado a las compras.
11. **011 · Ventas** — Vista con lo relacionado a las ventas.
12. **012 · Producción** — Vista con lo relacionado a la producción y gestión de recetas.
13. **013 · Caja** — Vista de movimientos de caja; para el rol admin.
14. **014 · Dashboard** — Es la vista principal de la aplicación.
15. **015 · Información de Usuario** — Permite cambiar la información de usuario con autorización del mismo.
16. **016 · Configuración Fiscal** — Datos fiscales de la empresa. Conexión al PAC. Catálogo de series y folios de facturación. Para rol admin.
17. **017 · Facturación** — Lista de facturas. Genera facturas.
18. **018 · Contabilidad** — Catálogo de cuentas contables. Libro diario. Balance de comprobación.

## Backlog / ideas 💡

- **Importación masiva desde Excel** — Management command de Django para cargar catálogo/inventario inicial sin captura manual.
- **App móvil consumiendo la misma API** — Reutiliza el backend sin reescribirlo.
- **Respaldo descargable manual desde el panel admin** — Complementa el backup automatizado por cron, dando control adicional al admin sin depender solo de la terminal del servidor.
- **Reportes de margen por producto** — Usa `costo_produccion` vs `precio_venta` ya definidos, para identificar qué productos son más rentables — dato que el dashboard actual no expone directamente.

> Cada feature nueva se crea como `features/NNN-nombre-feature/` con `spec.md`, `plan.md` y `tasks.md` antes de tocar código.