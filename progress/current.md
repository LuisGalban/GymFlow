# 🚀 Fase 3: Estabilización de UX Core y Blindaje

## Estado del Entorno
- **Python 3.14.5** ✅ (vía `backend/venv`)
- **Node.js v24.16.0 + PNPM 11.8.0** ✅
- **PostgreSQL 18.4** — Conexión exitosa a `gymflow_db` ✅
- **init.md:** Entorno verificado y estable ✅
- **Frontend:** Servidor de producción activo (`pnpm start`) ✅
- **Backend:** FastAPI en `localhost:8000` ✅
- **MVP Completado:** F-01 a F-24 — 28 tests, todos verdes ✅

## 🧪 Auditoría Técnica — Panel Admin Bloque B (Completado)
- **Analista:** Revisión exhaustiva de F2-01, F2-02, F2-03.
- **Hallazgos críticos (P0-P1):** 0 — Sin violaciones de reglas de negocio, sin fallas de seguridad.
- **Hallazgos secundarios (P2-P3):** 4 — Movidos a `docs/backlog.md` (sección Icebox).
- **Veredicto:** Panel Admin sólido para cierre de fase. `docs/backlog.md` actualizado.

## 🎯 Objetivos de la Fase

### Bloque A: Pulido Profesional (UX)
| ID | Tarea | Estado |
|----|-------|--------|
| F2-04 | Debounce en Búsqueda de Recepción (300ms) | ✅ |
| F2-05 | Skeleton Components para Tablas | ✅ |
| F2-06 | Sidebar Responsive con Menú Hamburguesa | ✅ |

### Bloque B: Analytics del Panel Admin
| ID | Tarea | Estado |
|----|-------|--------|
| F2-01 | Filtros Financieros (día/semana/mes/año/rango) | ✅ |
| F2-02 | Detalle Transaccional — Modal Interactivo | ✅ |
| F2-03 | Transparencia de Alertas — Lista de Vencidos | ✅ |

## ✅ **Fase 2 Completada** — Todas las tareas F2-01 a F2-09 implementadas, revisadas y cerradas.

---

## 🎯 Fase 3: Estabilización de UX Core y Blindaje — Abierta

| ID | Tarea | Prioridad | Estado |
|----|-------|-----------|--------|
| F3-01 | Sanitización y Validación de Cédula en Recepción | P1 | ✅ Ya completada (F2-07) |
| F3-02 | Prevención de Race Conditions en Admin Dashboard | P1 | ✅ Ya completada (F2-08) |
| F3-03 | Corrección de Layout y Capas en Sidebar Mobile | P2 | ✅ |
| F3-04 | Renderizado Condicional del Sidebar Mobile | P2 | ✅ |
| F3-05 | Adaptabilidad de Tablas Deslizables en Mobile | P2 | ✅ |
| F3-06 | Corrección de Contraste de Color en Dropdowns y Planes | P3 | ✅ |

### Bloque C: Seguridad y Calidad (Post-Auditoría)
| ID | Tarea | Estado |
|----|-------|--------|
| F2-07 | Sanitización y Validación de Cédula en Recepción | ✅ |
| F2-08 | Prevención de Race Conditions en Admin Dashboard | ✅ |

### Bloque D: UX y Baja Carga Cognitiva
| ID | Tarea | Estado |
|----|-------|--------|
| F2-09 | Prefijo de Cédula Implícito (V- automático) | ✅ |

## 🔍 Auditoría Técnica — Bloques B + A (Completada)
- **Analista:** Auditoría exhaustiva de F2-04, F2-05, F2-06.
- **Hallazgos P0:** 0 — Sin violaciones de borrado lógico ni normalización USD.
- **Hallazgos P1 (nuevas tareas):** 2 — F2-07 (Sanitización de Cédula en Recepción), F2-08 (Race Conditions en Admin Dashboard). Insertadas en `feature_list.json` con estado `pending`.
- **Hallazgos P2 (Icebox):** 4 — OPT-05 a OPT-08 movidos a `docs/backlog.md`.
- **Hallazgos P3 (Post-MVP):** 4 — OPT-09 a OPT-11 + aplazables visuales movidos a `docs/backlog.md`.
- **Nota PO:** Tarea "Período de gracia hardcodeado" enriquecida con directiva de UI configurable por el Admin.
- **Roadmap refinado:** `feature_list.json` y `docs/backlog.md` actualizados. Fase 2 cerrada, siguiente sprint = F2-07.

## ✅ Completada — F2-01 (Filtros Financieros)

### Resumen de cambios
- **Backend** (`backend/app/main.py:619-698`): Helper `_calcular_rango_fechas` + filtros `rango`, `desde`, `hasta` en endpoints `GET /api/v1/admin/kpis` y `GET /api/v1/admin/cashflow`. Se agrega JOIN a Miembro para excluir borrados lógicos (`estado_logico = False`). Solo suma `monto_usd`.
- **Frontend** (`frontend/src/app/dashboard/admin/page.tsx`): Selectores de filtro (Hoy, Esta Semana, Este Mes, Este Año, Personalizado) + datepickers para rango manual. Re-fetch automático al cambiar filtro.
- **Tests** (`backend/test_admin_fix.py`): 7 tests nuevos (test_5 a test_11) para cada rango, personalizado con/sin datos, y compatibilidad sin parámetros.
- **35 tests, todos OK** — TypeScript sin errores.

## ✅ Completada — F2-02 (Detalle Transaccional — Modal Interactivo)

### Resumen de cambios
- **Backend** (`backend/app/schemas.py:162-166`): Nuevo schema `PagoDetalleResponse` que extiende `PagoResponse` con `miembro_nombre`, `miembro_cedula`, `plan_nombre`, `registrador_nombre`.
- **Backend** (`backend/app/main.py:703-743`): Nuevo endpoint `GET /api/v1/admin/payments/{id}` que retorna detalle completo con joins a Miembro/Plan/Usuario sin filtrar por estado_logico. Si miembro o registrador tiene `estado_logico=False`, devuelve `"[Registro desactivado]"`.
- **Frontend** (`frontend/src/app/dashboard/admin/page.tsx`): Tabla de ingresos ahora tiene `onClick` por fila que abre un modal con todos los detalles del pago. Modal se cierra con botón X o clic fuera.
- **Tests** (`backend/test_admin_fix.py`): 3 tests nuevos (test_12 a test_14): detalle con datos correctos, miembro desactivado muestra "[Registro desactivado]", y 404 para ID inexistente.
- **38 tests, todos OK** — TypeScript sin errores.

## ✅ Completada — F2-03 (Transparencia de Alertas — Lista de Vencidos)

### Resumen de cambios
- **Backend** (`backend/app/main.py:737-768`): Nuevo endpoint `GET /api/v1/admin/vencidos` que retorna lista de miembros con membresía vencida (`estatus_pago='vencido'`, `fecha_vencimiento < hoy`, `estado_logico=True`). Cada entrada incluye `id`, `cedula`, `nombre`, `dias_vencido`, `telefono`.
- **Frontend** (`frontend/src/app/dashboard/admin/page.tsx`): Reemplazado contador de "Alertas Vencidas" por lista expandible con scroll (max-h-48). Cada item muestra nombre, cédula, "X días vencido". Es un enlace `<a href="/dashboard/reception?cedula=...">`. Si no hay vencidos, muestra "No hay miembros vencidos" en verde.
- **Tests** (`backend/test_admin_fix.py`): 2 tests nuevos (test_15 a test_16): verifica que el endpoint retorna 200 con formato correcto, y que excluye miembros con `estado_logico=False`.
- **40 tests, todos OK** — TypeScript sin errores.

## ✅ Hotfix 2 — F2-03 (Link a recepción no auto-busca la cédula)

### Problema
Link en Admin envía `?cedula=...` pero ReceptionPage no leía `useSearchParams()`.
Navegaba a `/dashboard/reception?cedula=X` y no ejecutaba la búsqueda automática.

### Corrección
1. **`reception/page.tsx:4`**: Import `useSearchParams` de `next/navigation`.
2. **`reception/page.tsx:67-74`**: `useEffect` que al montar lee `cedula` de query params y dispara `buscar(cedulaParam)`.
3. **`reception/page.tsx:76`**: `buscar()` refactorizada a `buscar(cedulaInput?: string)` para funcionar sin evento de form.
4. Se preservó guard `if (!token) return;` del hotfix anterior.
- **TypeScript:** 0 errores. **Reviewer:** Aprobó.

## ✅ Hotfix 4 Aplicado — F2-06 (Sidebar: dual rendering desktop/mobile)

### Problema raíz
Tailwind v4 no detectaba `md:static` en template literals con comentarios. El wrapper DIV sin `shrink-0` se comprimía en el flex layout.

### Corrección
- **Sidebar.tsx**: Dual rendering. Desktop: `<aside>` con clases ORIGINALES exactas + `max-md:hidden`. Mobile: `<aside>` separado con `md:hidden`, overlay slide-in. Contenido extraído a `SidebarContent` (sin duplicación).
- **DashboardLayout.tsx** y **Navbar.tsx**: Sin cambios (ya revertidos a original).
- **TypeScript:** 0 errores. **Reviewer:** Aprobó.

## ✅ Completada — F2-05 (Skeleton Components para Tablas)

### Resumen de cambios
- **Componente creado** (`frontend/src/app/components/TableSkeleton.tsx`): Reusable con `kinetic-glass`, `animate-pulse` y columnas de ancho variable cíclico (30/25/20/15/10%).
- **Members list** (`members/list/page.tsx`): Spinner `Loader2` → `<TableSkeleton rows={6} columns={6} />`.
- **Staff list** (`staff/list/page.tsx`): Spinner `Loader2` → `<TableSkeleton rows={6} columns={6} />`.
- **Admin dashboard** (`dashboard/admin/page.tsx`): Loading principal → 3 KPI skeleton cards + `<TableSkeleton rows={5} columns={4} />`. Modal → barras skeleton de anchos progresivos.
- **Tests:** TypeScript sin errores. Sin regresión en estados de error/vacío.

## ✅ Completada — F2-04 (Debounce en Búsqueda de Recepción)

### Resumen de cambios
- **Frontend** (`frontend/src/app/dashboard/reception/page.tsx`): Agregados `debounceRef` y `abortRef` con `useRef`. `onChange` resetea resultados y programa búsqueda con `setTimeout(300ms)`. `buscar()` cancela petición previa con `AbortController` e ignora `CanceledError`. Cleanup de efecto cancela debounce al desmontar. Se preservaron auto-search por `?cedula=` y botón "Buscar" manual.
- **Tests:** 0 regresiones — TypeScript sin errores.

## ✅ Hotfix 1 — F2-03 (Redirect Loop al hacer clic en alerta vencida)

### Problema
Link `<a href>` en admin causaba navegación completa → React re-monta → `syncPending` corría sin token → 401 → `/login`.
2. **`admin/page.tsx`**: `<a>` → `<Link>` de `next/link` para navegación cliente-side.
- **TypeScript:** 0 errores. **Reviewer:** Aprobó.

## ✅ Completada — F2-07 (Sanitización y Validación de Cédula en Recepción)

### Resumen de cambios
- **Frontend** (`reception/page.tsx`): Triple capa de validación: (1) `maxLength={20}` en `<input>`, (2) sanitizer en `onChange` que filtra caracteres no válidos con `replace(/[^VJEGP\d-]/g, "")` y solo permite debounce si pasa regex estricto `/^[VJEGP]-?\d{1,10}$/`, (3) guard en `buscar()` que rechaza inputs inválidos antes del API call. Auto-search por `?cedula=` también sanitizado con `toUpperCase()` + regex guard.
- **Tests** (`frontend/tests/cedula-validation.test.mjs`): 26 tests — cubren SQL injection, XSS, path traversal, null bytes, dígitos límite, formatos válidos/inválidos. Todos pasan.
- **Reviewer:** APPROVED (16/16 checklist items). TypeScript: 0 errores.

## ✅ Completada — F2-08 (Prevención de Race Conditions en Admin Dashboard)

### Resumen de cambios
- **Frontend** (`admin/page.tsx`): Integrado `AbortController` via `abortRef` (mismo patrón que F2-04 en recepción). Cada cambio de filtro (`filtroRango`, `filtroDesde`, `filtroHasta`) aborta la petición HTTP previa antes de iniciar la nueva. Cleanup del `useEffect` cancela requests en curso al desmontar. `CanceledError`/`ERR_CANCELED` ignorados silenciosamente en catch.
- **Tests** (`frontend/tests/admin-race-condition.test.mjs`): 30 tests — simulación de race condition, abort chain, 10 cambios rápidos de filtro, useEffect cleanup, smoke test del source code (verifica `abortRef`, `AbortController`, `CanceledError`, `ERR_CANCELED`, `controller.signal`, cleanup `return`). Todos pasan.
- **Reviewer:** APPROVED (16/16 checklist items). TypeScript: 0 errores.

## 🔒 **Auditoría Post-Implementación Cerrada** — F2-07 y F2-08 completadas. Todas las tareas P1 del roadmap resueltas.

## ✅ Completada — F2-09 (Prefijo de Cédula Implícito en Registro de Atletas)

### Resumen de cambios
- **Frontend** (`members/register/page.tsx`): Nuevo state `prefijo` (default "V"). Selector de prefijo `<select>` (V/J/E/G/P) junto a input numérico con `onChange` que filtra no-dígitos (`replace(/\D/g, "")`) y `maxLength={10}`. `handleSubmit` concatena `{prefijo}-{cedula}` y valida con regex F2-07 antes del envío. Label cambiado a "Cédula". Placeholder solo dígitos.
- **Tests** (`frontend/tests/cedula-prefix-register.test.mjs`): 16 tests — concatenación correcta, caracteres no numéricos rechazados, cambio de prefijo, edge cases (vacío, maxLength, todos los prefijos). Todos pasan.
- **Reviewer:** APPROVED (8/8 criterios de aceptación). TypeScript: 0 errores.

## ✅ Completada — F3-03 (Corrección de Layout y Capas en Sidebar Mobile)

### Resumen de cambios
- **Frontend** (`Navbar.tsx:37`): Padding compensatorio `pl-14 pr-6 md:px-6` — en mobile, left padding de 56px desplaza el contenido del Navbar a la derecha del botón hamburguesa fijo. En desktop, `md:px-6` restaura el padding original. Sin state lifting ni reestructuración de componentes.
- **Reviewer:** APPROVED (4/4 criterios de aceptación). TypeScript: 0 errores.

## ✅ Completada — F3-04 (Renderizado Condicional del Sidebar Mobile)

### Resumen de cambios
- **Frontend** (`Sidebar.tsx:110`): Reemplazada ocultación CSS (`-translate-x-full`/`translate-x-0`) por renderizado condicional React `{mobileOpen && (...)}`. El `<aside>` mobile, overlay backdrop y botón X se agrupan en un único bloque condicional. Al cerrar, los nodos se desmontan completamente del DOM — sin focus traps, sin nodos invisibles.
- **Reviewer:** APPROVED (12/12 checklist items). TypeScript: 0 errores.

## ✅ Completada — F3-05 (Adaptabilidad de Tablas Deslizables en Mobile)

### Resumen de cambios
- **Frontend** (`members/list/page.tsx:103`, `staff/list/page.tsx:113`): Reemplazada clase `overflow-hidden` por `overflow-x-auto` en el contenedor de cada tabla (`kinetic-glass rounded-2xl`). Tablas ahora son deslizables horizontalmente en mobile; sin regresión en desktop.
- **Reviewer:** APPROVED (7/7 checklist items). TypeScript: 0 errores.

## ✅ Completada — F3-06 (Corrección de Contraste de Color en Dropdowns y Planes)

### Resumen de cambios
- **Frontend** (`globals.css:92-95`): Agregadas reglas CSS `select option { background-color: #1a1a2e; color: #f4f4f5; }` para forzar fondo oscuro y texto claro en todos los `<option>` nativos. Soluciona bug de texto blanco sobre fondo blanco en dropdowns de plan (members/register, payments/register) y selector de método de pago. Fix CSS-only — sin cambios en classNames de los `<select>`.
- **Reviewer:** APPROVED (12/12 checklist items). TypeScript: 0 errores.

---

## 🔒 Auditoría Técnica Fase 3 — Presentación/UX (Cerrada)

- **Alcance:** F3-03 (Layout Sidebar), F3-04 (Renderizado Condicional), F3-05 (Tablas Deslizables), F3-06 (Contraste Dropdowns).
- **Analista:** Auditoría exhaustiva de código frontend contra `docs/PRD.md` y `docs/business_rules.md`.
- **Hallazgos P0-P1 (Bloqueantes):** 0 — Sin violaciones de borrado lógico, normalización USD ni RBAC.
- **Hallazgos P2 (Icebox):** 2 — OPT-13 (Scroll Sidebar), OPT-14 (ARIA Sidebar). Movidos a `docs/backlog.md`.
- **Hallazgos P3 (Post-MVP):** 1 — OPT-12 (color-scheme dropdowns). Movido a `docs/backlog.md`.
- **`docs/backlog.md` actualizado** con OPT-12, OPT-13, OPT-14.
- **`feature_list.json` verificado** — F3-03, F3-04, F3-05, F3-06 en estado `done`.
- **Veredicto:** Componentes visuales de Fase 3 aprobados. El desarrollo se prepara para la estabilización de los endpoints críticos restantes de la Fase 3 antes del salto a la arquitectura SaaS.

---

## 🚀 Fase 4: Escalabilidad Multi-Gimnasio (SaaS) — Iniciada

### Arquitectura Elegida: Aislamiento Lógico por `gym_id`
Cada tabla de negocio lleva una columna `gym_id` (FK → `gyms.id`). Todas las consultas ORM se filtran automáticamente por esta columna para garantizar aislamiento de datos entre sedes. Se descartó aislamiento por esquemas separados por complejidad operativa desproporcionada para el MVP SaaS.

### Invariantes Obligatorios de la Fase 4
Las siguientes reglas de negocio **NO se alteran** y se extienden al contexto multi-tenant:
- **Borrado Lógico:** Baja de una sede (`gyms.estado_logico=False`) NO elimina datos históricos de pagos, asistencias ni miembros.
- **Normalización USD:** Cada sede respeta su `moneda_base` y todas las transacciones se registran con su equivalente en USD según la tasa vigente al momento de la operación.
- **RBAC:** El rol `super_admin` se agrega por encima de `admin`. Ningún rol inferior accede a datos de otra sede ni al panel SuperAdmin.

### Roadmap de Migración de Datos
1. **Seed de Migración (F4-02):** Se crea `gyms` registro por defecto (`id=1, nombre='GymFlow Sede Central'`) y se asigna `gym_id=1` a TODA la data existente (fases 1-3).
2. **Invalidación de Sesiones (F4-03):** Tokens JWT legacy sin `gym_id` serán rechazados con 401 tras el deploy. Se requiere re-login de todos los usuarios.
3. **Zero-Downtime:** La migración Alembic (F4-02) agregará columnas `gym_id NOT NULL` con `DEFAULT 1` para evitar locks prolongados en tablas activas.

### Tablero de Tareas — Fase 4

| ID | Tarea | Prioridad | Estado |
|----|-------|-----------|--------|
| F4-01 | Modelo de Sedes (Gyms) | P0 | ✅ Done |
| F4-02 | Migración de Esquema — gym_id como FK | P0 | ✅ Done |
| F4-03 | Refactor de Auth — gym_id en JWT | P0 | ✅ Done |
| F4-04 | Middleware de Filtrado Automático por gym_id | P0 | ✅ Done |
| F4-05 | Panel SuperAdmin — Gestión de Sedes | P1 | ✅ Done |

### Orden de Ejecución Recomendado
`F4-01` → `F4-02` → `F4-03` → `F4-04` → `F4-05`
(Dependencias lineales: cada tarea requiere la anterior completada)

## ✅ Completada — F4-02 (Migración de Esquema — gym_id como FK)

### Resumen de cambios
- **Modelo** (`backend/app/models.py`): Agregada columna `gym_id` (Integer, FK → `gyms.id`, `ondelete="RESTRICT"`, `nullable=False`) a: `Usuario`, `Miembro`, `Plan`, `Pago`, `Asistencia`. Agregadas relaciones inversas en `Gym` (`usuarios`, `miembros`, `planes`, `pagos`, `asistencias`) y `back_populates` en cada entidad.
- **Migración Alembic** (`backend/alembic/versions/b7d3f1a9c8e2_add_gym_id_fk_to_all_entities.py`): Migración manual con: (1) `add_column` nullable para 5 tablas, (2) seed de gym default (`id=1, nombre='GymFlow Sede Central'`), (3) `UPDATE SET gym_id=1 WHERE gym_id IS NULL` para cada tabla, (4) `ALTER COLUMN NOT NULL`, (5) `create_foreign_key` con `ON DELETE RESTRICT`.
- **Tests** (`backend/test_f4_02_gym_id_migration.py`): 10 tests — columnas gym_id NOT NULL, FK RESTRICT, data seed gym_id=1, query sin filtro retorna todas las sedes, normalización USD intacta, FK RESTRICT impide delete de gym con data, planes independientes por gym, borrado lógico de planes, relaciones backref funcionales.
- **Tests existentes adaptados** (`backend/test_check_constraints.py`): Agregado `Gym` + `gym_id` a setup y test objects. Agregado `create_all`/`drop_all` para evitar interdrop con otros test files.
- **30 tests, todos OK** — Sin regresiones.
- **Reviewer:** APPROVED — Sin violaciones de borrado lógico ni normalización USD. 8/8 checklist items.

## ✅ Completada — F4-03 (Refactor de Auth — gym_id en JWT)

### Resumen de cambios
- **Auth** (`backend/app/auth/auth.py`): `obtener_usuario_actual()` y `obtener_usuario_por_token()` ahora extraen `gym_id` del payload JWT. Rechazan con 401 si el token no contiene `gym_id` (tokens legacy).
- **Login** (`backend/app/main.py:124`): `crear_token_acceso()` ahora incluye `"gym_id": usuario.gym_id` en el payload. Respuesta incluye `gym_id` para el frontend.
- **Schemas** (`backend/app/schemas.py`): `Token` y `TokenData` actualizados con campo `gym_id: int`.
- **Tests** (`backend/test_f4_03_jwt_gym_id.py`): 5 tests — login retorna gym_id, JWT contiene gym_id, `/me` funciona, tokens legacy rechazados en `/me` y `obtener_usuario_por_token`.
- **Reviewer:** APPROVED — 8/8 checklist items. Sin regresiones.

## ✅ Completada — F4-04 (Middleware de Filtrado Automático por gym_id)

### Resumen de cambios
- **Backend** (`backend/app/main.py`): Corregidos 8 endpoints críticos sin filtro `gym_id`:
  - `PUT /api/v1/users/{id}` — Added `Usuario.gym_id == usuario_actual.gym_id` filter
  - `POST /api/v1/memberships` — Validación de miembro y plan por `gym_id`
  - `POST /api/v1/asistencias/checkin` — Filtrado de miembro por `gym_id`
  - `POST /api/v1/asistencias/batch` — Filtrado de miembros por `gym_id`
  - `GET /api/v1/admin/kpis` — Filtrado de miembros y pagos por `gym_id`
  - `GET /api/v1/admin/cashflow` — Filtrado de miembros y pagos por `gym_id`
  - `GET /api/v1/admin/payments/{id}` — Filtrado de pago por `Pago.gym_id`
  - `GET /api/v1/admin/vencidos` — Filtrado de miembros por `gym_id`
- **Modelo** (`backend/app/models.py`): Agregada `UniqueConstraint('nombre', 'gym_id', name='uq_plan_nombre_gym')` al modelo `Plan` para aislamiento de unicidad de planes por sede.
- **Migración Alembic** (`backend/alembic/versions/5e13ef50a67b_add_unique_constraint_planes_nombre_gym_.py`): Migración autogenerada para aplicar la restricción de unicidad compuesta.
- **Tests** (`backend/test_f4_04_gym_filter.py`): 15 tests de aislamiento multi-tenant:
  - Gym1 no ve miembros de Gym2 y viceversa
  - Búsqueda por cédula aislada por gym
  - Planes, KPIs, cashflow, users, vencidos filtrados por gym
  - Detalle de pago cruzado bloqueado (404)
  - Update de usuario cruzado bloqueado (404)
  - Check-in de miembro de otra sede bloqueado (404)
  - Plan con mismo nombre en diferente gym permitido
- **BD restaurada**: Tablas recreadas tras falla eléctrica + seed de datos actualizado con `gym_id`
- **Reviewer:** APPROVED — 15/15 tests pasan. Sin regresiones.

## ✅ Completada — F4-05 (Panel SuperAdmin — Gestión de Sedes y Onboarding Descentralizado)

### Resumen de cambios
- **Modelo** (`backend/app/models.py`): Agregado `super_admin` al enum `UserRole`. Agregada columna `token_sede` (UUID, nullable) al modelo `Gym` para onboarding.
- **Schemas** (`backend/app/schemas.py`): Nuevos schemas `SuperAdminGymCreate`, `SuperAdminGymResponse`, `SuscripcionUpdate`, `RegisterGymAdminRequest`.
- **Auth** (`backend/app/auth/auth.py`): Nueva dependencia `requerir_super_admin` para RBAC.
- **Endpoints** (`backend/app/main.py`): 4 nuevos endpoints:
  - `POST /api/v1/super-admin/gyms` — Crear sede (retorna token_sede UUID)
  - `GET /api/v1/super-admin/gyms` — Listar sedes con métricas
  - `PUT /api/v1/super-admin/gyms/{id}/suscripcion` — Pausar/reanudar/suspender
  - `POST /api/v1/auth/register-gym-admin` — Registro público con token (un solo admin por sede)
- **Migración** (`backend/alembic/versions/f4a05b01c123_add_token_sede_to_gyms.py`): Columna `token_sede` UUID nullable con índice único.
- **Frontend**:
  - `super-admin/gyms/page.tsx` — Panel de gestión de sedes con tabla, métricas, botón crear, visualización de token
  - `register-gym/[token_sede]/page.tsx` — Página pública de registro de dueño de sede
  - `Sidebar.tsx` — Nuevo item "Gestionar Sedes" visible solo para super_admin
  - `AuthContext.tsx` — Soporte para rol `super_admin` y flag `isSuperAdmin`
- **Tests** (`backend/test_f4_05_super_admin.py`): 12 tests — admin 403, unauthenticated, CRUD sedes, flujo onboarding, reutilización de token, token inválido, sede pausada.
- **Reviewer:** APPROVED — 12/12 checklist items. Sin regresiones.

## 🎉 **Fase 4 Completada** — Tareas F4-01 a F4-05 implementadas, revisadas y cerradas.

### Estado Final de la Fase 4
| ID | Tarea | Prioridad | Estado |
|----|-------|-----------|--------|
| F4-01 | Modelo de Sedes (Gyms) | P0 | ✅ Done |
| F4-02 | Migración de Esquema — gym_id como FK | P0 | ✅ Done |
| F4-03 | Refactor de Auth — gym_id en JWT | P0 | ✅ Done |
| F4-04 | Middleware de Filtrado Automático por gym_id | P0 | ✅ Done |
| F4-05 | Panel SuperAdmin — Gestión de Sedes | P1 | ✅ Done |

### Siguiente paso
Todas las tareas F4-01→F4-05 están en estado `done`. Auditoría técnica completada.

---

## 🔍 Auditoría Técnica Fase 4 — Multi-Tenancy (Cerrada)

- **Alcance:** F4-01, F4-02, F4-03, F4-04, F4-05 (todo el aislamiento multi-sede).
- **Analista:** Auditoría exhaustiva contra `docs/PRD.md`, `docs/business_rules.md`, `docs/design_system.md`.
- **Multi-tenancy:** 0 fugas detectadas en 17 endpoints auditados. Aislamiento por gym_id sólido.
- **Borrado lógico:** 0 violaciones. Todos los endpoints usan `estado_logico=False`.
- **Hallazgos P0 (Bloqueantes):** 2 — H-01 (JWT_SECRET default predecible), H-02 (dias_restantes_gracia ausente en schema).
- **Hallazgos P1 (Urgentes):** 5 — H-03 (Cron sin RBAC adecuado), H-04 (Cookie secure=False), H-05 (Batch sin Pydantic), H-06 (Race condition TOCTOU), H-07 (Migración vacía UniqueConstraint).
- **Hallazgos P2 (Mejoras):** 4 — H-08 a H-11 → movidos a `docs/backlog.md`.
- **Hallazgos P3 (Sugerencias):** 3 — H-12 a H-14 → movidos a `docs/backlog.md`.
- **`feature_list.json` actualizado** con H-01 a H-07 como tareas `pending`.
- **`docs/backlog.md` actualizado** con H-08 a H-14 en sección Icebox.
- **Roadmap refinado:** Fase 4 base completada. Siguiente ciclo: resolver H-01→H-07 antes de producción.

---

## 🔧 Blindaje Post-Auditoría — H-01 a H-07 (CERRADA)

| ID | Tarea | Prioridad | Estado |
|----|-------|-----------|--------|
| H-01 | Seguridad JWT — Eliminar Default de JWT_SECRET | P0 | ✅ Done |
| H-02 | Schema MiembroResponse — Agregar dias_restantes_gracia | P0 | ✅ Done |
| H-03 | RBAC Cron — Proteger endpoint update-statuses | P1 | ✅ Done |
| H-04 | Cookie Seguridad — Parametrizar secure flag | P1 | ✅ Done |
| H-05 | Batch Check-in — Agregar schema Pydantic y límite | P1 | ✅ Done |
| H-06 | Race Condition — Atomicidad en register-gym-admin | P1 | ✅ Done |
| H-07 | Migración UniqueConstraint Planes — Aplicar restricción | P1 | ✅ Done |

## ✅ Completada — H-01 (Seguridad JWT — Eliminar Default de JWT_SECRET)

### Resumen de cambios
- **Auth** (`backend/app/auth/auth.py:16-19`): Eliminado fallback `"super_secret_key_default"` de `os.getenv()`. Agregado `ValueError` explícito si `JWT_SECRET` no está configurado, siguiendo el mismo patrón de `database.py` para `DATABASE_URL`.
- **Tests** (`backend/test_h01_jwt_secret.py`): 3 tests — ValueError cuando falta env, sin default hardcodeado en source, mensaje de error contiene "JWT_SECRET".
- **Reviewer:** APPROVED — 5/5 checklist items. Sin regresiones.

## ✅ Completada — H-02 (Schema MiembroResponse — Agregar dias_restantes_gracia)

### Resumen de cambios
- **Schemas** (`backend/app/schemas.py:103`): Agregado `dias_restantes_gracia: Optional[int] = None` al schema `MiembroResponse`. El campo ya era calculado y pasado en los endpoints `GET /members` y `GET /members/search/{cedula}` pero Pydantic v2 lo descartaba silenciosamente al no estar declarado.
- **Tests** (`backend/test_h02_dias_gracia.py`): 6 tests — existencia del campo, tipo `Optional[int]`, serialización con valor explícito, default `None`, y verificación de que los endpoints usan `MiembroResponse`.
- **Reviewer:** APPROVED — 5/5 checklist items. Sin regresiones.

## ✅ Completada — H-05 (Batch Check-in — Agregar schema Pydantic y límite)

### Resumen de cambios
- **Schemas** (`backend/app/schemas.py:177-181`): Nuevos schemas `AsistenciaBatchItem(miembro_id: int, fecha_entrada: Optional[str])` y `AsistenciaBatchRequest(items: List[AsistenciaBatchItem])`.
- **Endpoint** (`backend/app/main.py:580-612`): `/api/v1/asistencias/batch` ahora usa `AsistenciaBatchRequest` en lugar de `List[dict]`. Validación explícita de límite 500 items con retorno 400 Bad Request. Iteración del schema con acceso directo a atributos en lugar de `.get()`.
- **Tests** (`backend/test_h05_batch_schema.py`): 10 tests — batch vacío, batch con miembro inexistente, batch múltiple items, batch con `fecha_entrada` opcional, batch de exactamente 500, batch que excede 500→400, body sin key `items`→422, `items` no es lista→422, item sin `miembro_id`→422, no autenticado→401.
- **Reviewer:** APPROVED — 5/5 checklist items. Sin regresiones.

## ✅ Completada — H-03 (RBAC Cron — Proteger endpoint update-statuses)

### Resumen de cambios
- **Endpoints** (`backend/app/main.py:610`): Cambiada la dependencia de `/api/v1/cron/update-statuses` de `requerir_trabajador` a `requerir_super_admin`. Ahora solo el rol super_admin puede invocar el job de mutación masiva de estados de membresía.
- **Tests** (`backend/test_h03_cron_rbac.py`): 4 tests — worker→403, admin→403, super_admin→200, unauthenticated→401.
- **Reviewer:** APPROVED — 5/5 checklist items. Sin regresiones.

---

## 🚀 Fase 4 Extensión: Gestión Avanzada y Configuración por Sede — Abierta

### Contexto
Tras completar el blindaje post-auditoría (H-01→H-07), se expande la Fase 4 con funcionalidades de gestión y configuración que aprovechan la arquitectura multi-tenant ya establecida. Estas tareas resuelven carencias funcionales identificadas en el código actual:
- Solo existen endpoints GET+POST de planes (sin PUT/DELETE, sin frontend dedicado).
- `calcular_estado_miembro()` usa literal `5` para gracia en vez de leer `Gym.dias_gracia_default`.
- Recepción solo muestra `dias_restantes_gracia`, sin días disponibles ni gracia transcurridos.
- No hay recálculo automático al modificar la duración de un plan.

### Tareas Promovidas desde Backlog
- "Período de gracia hardcodeado (5 días)" → **F4-09** (promovida a `pending`)
- "Visualización de días restantes o vencimiento en Recepción" → **F4-08** (promovida a `pending`)

### Tablero de Tareas

| ID | Tarea | Prioridad | Estado |
|----|-------|-----------|--------|
| F4-06 | Gestión Parametrizada de Planes (CRUD Completo) | P0 | ⏳ Pending |
| F4-07 | Recálculo Reactivo de Membresías al Modificar Plan | P0 | ⏳ Pending |
| F4-08 | UI de Recepción con Estatus Detallado | P1 | ⏳ Pending |
| F4-09 | Motor de Gracia Configurable por Sede | P1 | ⏳ Pending |

### Orden de Ejecución Recomendado
`F4-06` → `F4-07` → `F4-08` → `F4-09`
(Dependencias: F4-07 requiere F4-06 completada para el PUT de planes. F4-08 y F4-09 son independientes entre sí pero ambas dependen de la infraestructura multi-tenant de F4-01→F4-05.)
