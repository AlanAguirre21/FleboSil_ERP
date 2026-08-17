# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This repo is currently a bare scaffold, not yet an implemented app:

- `code/backend/` is a fresh `django-admin startproject` (only `config/`, no apps yet, PostgreSQL dev DB, `DEBUG=True`).
- `code/frontend/` is a fresh Vite + React 19 template (no router, no API layer, no components beyond the default template yet).

The conda env `erp_flebosil` already has `Django`, `djangorestframework`, and `django-cors-headers` installed, but no `requirements.txt`/`pyproject.toml` is committed yet — add one when dependencies are first pinned. `pytest-django` and `ruff` are referenced by the spec (see below) but not yet installed.

All real feature work is driven by the spec files under `spec/` — read those before writing code, since the actual architecture (apps, models, endpoints) doesn't exist on disk yet and only exists as spec.

## Spec-driven development (mandatory workflow)

This project follows **Spec Driven Development**: spec → plan → tasks → code, in that order. Never write feature code without a matching spec.

- `spec/constitution/mission.md` — what FleboSil ERP is, its screens/modules, and product principles. Read this first for any domain question.
- `spec/constitution/tech-stack.md` — the authoritative tech stack, file/module conventions, domain-model rules, and hard limits (see below). **This overrides ad-hoc choices** — if a feature conflicts with it, the feature gets rethought, not the constitution.
- `spec/constitution/roadmap.md` — the 18 features in build order (`001-header` through `018-contabilidad`); nothing here is marked done yet, all are "Siguiente".
- `spec/features/NNN-nombre-feature/` — one folder per feature, each with `spec.md` (what + acceptance criteria), `plan.md` (technical approach + decisions + risks), `tasks.md` (checklist).
- `Base de Datos FleboSil.txt` (repo root) — a reference listing of the 30 expected tables (`erp_flebosil_db`) with candidate field names/FKs. Useful as a starting point for Django models, but **the spec files (`spec/constitution/`, `spec/features/`) take priority whenever they conflict** — this doc's entity/field names haven't been fully verified and may contain errors (e.g. naming mismatches against `tech-stack.md`, possible typos in individual field names). Cross-check against the spec, and flag discrepancies to the user rather than assuming this file is correct, before committing a name to a migration.

## Commands

Backend (from `code/backend/`, conda env `erp_flebosil`):
- `python manage.py runserver` — run the dev server.
- `python manage.py migrate` — apply migrations.
- `python manage.py makemigrations <app>` — create migrations for an app.
- `pytest` — run backend tests (once `pytest-django` is installed and configured).
- `ruff check .` — lint Python (once `ruff` is installed).

Frontend (from `code/frontend/`):
- `npm run dev` — Vite dev server.
- `npm run build` — production build.
- `npm run lint` — ESLint.
- `npm run test` — Vitest (once test setup exists).

## Architecture rules from the constitution

These are load-bearing conventions for FleboSil ERP; apply them to every new app/module, not just the one that first defined them:

- **Domain shape**: sucursales (`006`) are inventory-only locations — profit, cash (`caja`), and staff are global to the company, never segmented by branch. Don't add a branch filter to financial/HR views.
- **Stock changes are one-way through inventario**: `backend/apps/inventario/` owns `InventarioSucursalProducto`/`MateriaPrima` and `MovimientosInventario`; no other app writes to stock directly. `stock_actual` is never modified directly — every change is an audited `MovimientoInventario`.
- **Ledger tables are insert-only**: `MovimientosCaja` and `MovimientosInventario` are never `UPDATE`d or `DELETE`d — corrections are always a new, inverse movement. Same soft-delete pattern applies to catalog entities generally (e.g. `Sucursal.activo`, established in feature `006` as the reusable pattern for Productos, MateriaPrima, Clientes, etc.) — no hard `DELETE`, override the ViewSet's destroy to flip a flag instead.
- **Money and quantity fields are always `Decimal`**, never `FloatField`/`float`, no exceptions.
- **Concurrency-safe stock writes**: `select_for_update()` when reading stock inside any transaction that will modify it, and `transaction.atomic()` around any operation touching more than one related table (a full venta, compra, or producción) so a failed step rolls back everything.
- **Header-detail pricing freeze**: `Ventas`/`DetalleVenta`, `Compras`/`DetalleCompra*` freeze price/cost on the detail row at transaction time — never re-derive from the current catalog price later.
- **Backend is the sole permissions authority**: DRF views enforce role checks (admin vs operador); the frontend only hides UI for UX, never as the actual access control. Reuse `backend/core/permissions.py` for shared DRF permission classes — don't reimplement role checks per view. A common pattern per `006`: one ViewSet, `SAFE_METHODS` open to any authenticated user, write methods restricted to admin — prefer that over separate read/write views.
- **DRF serializers are the only input validation layer** — never trust frontend-only validation.
- **API errors** are always structured JSON (`{"detail": "..."}`), never a raw stack trace (`DEBUG=False` in production).

## Frontend conventions

- `frontend/src/api/` — one function per endpoint, grouped by module; components never call `axios` directly.
- `frontend/src/hooks/` — one React Query hook per entity, centralizing cache/loading/error state.
- `frontend/src/styles/variables.css` — global CSS variables (brand colors, status colors, typography, breakpoints). Every `*.module.css` consumes these via `var(--nombre)`; never hardcode a color.
- Styling is one `Componente.module.css` per component, imported as `styles` and applied via `className={styles.x}` — no inline styles, no CSS mixed into TSX.
- Common reusable components (`Tabla`, `Modal`, `BotonPrimario`, under `frontend/src/components/common/`) were established in feature `006` specifically so later features don't re-solve table/modal patterns — check there before building a new one.
- Naming: `snake_case` for Django models/fields, `camelCase` for TS/React variables and functions.
- **Language: UI text, user-facing messages, and variable/function/model names are all in Spanish.** Technical comments are also written in Spanish.

## Hard limits (do not violate)

- No `FloatField`/float for money or inventory quantities, ever.
- No editing or deleting rows in `MovimientosCaja` or `MovimientosInventario` — insert-only.
- No frontend-only role/permission checks — every access rule must also be enforced server-side.
- No committing `.env` or PAC/SMTP credentials.
- No new dependencies without weighing them against the constitution's "simplicity over premature scalability" principle (single long-term maintainer).
- No direct writes to `stock_actual` outside the `MovimientosInventario` flow.
