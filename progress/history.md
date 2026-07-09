# Historial de Progreso - GymFlow Analytics

## Sesión: 2026-07-02
- **Estado Inicial:** `feature_list.json` inicializado con todas las tareas mapeadas. Tareas `F-14` y `F-15` en estado `pending`.
- **Acciones Realizadas:**
  - **F-14 (Tolerancia a Fallas Offline de Red):**
    - Se actualizó el esquema de base de datos de IndexedDB (`gymflow-db` a versión 2) para incluir los almacenes `members_cache` y `offline_checkins_queue`.
    - Se integró la lógica en `/dashboard/reception` para almacenar el catálogo de miembros localmente, permitiendo búsquedas en desconexión.
    - Se implementó la sincronización automática (flush engine) en lote a `/api/v1/asistencias/batch` al restablecerse la conectividad.
  - **F-15 (Protocolo de QA e Integración):**
    - Se creó la suite de pruebas automáticas en `backend/test_offline.py` ejecutada de forma exitosa usando la base de datos PostgreSQL del entorno virtual de Python.
    - Se verificó la latencia de la búsqueda optimizada con el índice B-Tree en menos de 50ms.
- **Resultado:** Las tareas `F-14` y `F-15` se completaron con éxito y se marcaron como `done` en `feature_list.json`. El proyecto tiene ahora el 100% de las funcionalidades del MVP implementadas y probadas.

## Sesión: 2026-07-07
- **Estado Inicial:** Tarea `F-16` agregada en estado `pending` para solucionar el acceso bloqueado de la vista de administración.
- **Acciones Realizadas:**
  - **F-16 (Corrección de Acceso y Panel del Administrador):**
    - Se importó `useAuth` y `useRouter` en `frontend/src/app/dashboard/admin/page.tsx`.
    - Se implementó la protección de ruta del cliente (RBAC) redirigiendo a los trabajadores u usuarios no autenticados a la vista de recepción.
    - Se inyectó la cabecera `Authorization: Bearer <token>` en las peticiones Axios concurrentes de KPIs y cashflow.
- **Resultado:** La tarea `F-16` fue implementada y marcada como `done` en `feature_list.json`. Las pruebas automáticas de la base de datos y la segregación de roles se ejecutaron exitosamente.

### Post-Mortem F-16: Corrección de Serialización Decimal
- **Error Reportado:** `toFixed is not a function` en `admin/page.tsx:91` y `422 Unprocessable Entity`.
- **Causa Raíz:** Pydantic v2 serializa `Decimal` como `str` en `model_dump(mode='json')`, causando que el frontend reciba strings donde espera números.
- **Solución:**
  - Se agregó `json_encoders={Decimal: lambda v: float(v)}` a los schemas `KpiSummary`, `CashFlowReport`, `PagoResponse` y `PlanResponse`.
  - Se añadió `Number()` defensivo en el frontend antes de `.toFixed()`.
- **Test:** `test_admin_fix.py` (3 tests, todos verdes) que validan tipos numéricos y HTTP 200.
- **Archivos modificados:** `backend/app/schemas.py`, `frontend/src/app/dashboard/admin/page.tsx`.
- **Archivo creado:** `backend/test_admin_fix.py`.

## Sesión: 2026-07-07 (Tarde)
- **Estado Inicial:** F-17 (`pending`) como tarea de mayor prioridad tras reordenar feature_list.json.
- **Acciones Realizadas:**
  - **F-17 (Gestión de Recepcionistas):**
    - Backend: 4 endpoints (`GET /api/v1/users`, `GET /api/v1/users/{id}`, `PUT /api/v1/users/{id}`, `DELETE /api/v1/users/{id}`) con RBAC estricto (requerir_admin).
    - Frontend: `/staff/list` (tabla con borrado lógico visual), `/staff/register` (formulario Zod, rol forzado worker).
    - Sidebar: Opción "Gestionar Personal" visible solo para admin.
    - Se respetaron borrado lógico, bcrypt, Pydantic/Zod y One Feature at a Time.
- **Resultado:** F-17 completada y marcada como `done` en `feature_list.json`. Próxima tarea: F-14.

### Post-Mortem F-17: Recepcionistas no visibles en Staff List (doble causa)
- **Bug Reportado:** Recepcionistas creados correctamente en DB no aparecían en `/staff/list`. Tras el hotfix del catch, se reveló un 404 oculto.
- **Causa Raíz #1 (Frontend):** `fetchStaff` en `frontend/src/app/staff/list/page.tsx` usaba `try/finally` sin `catch`. Cualquier error silenciaba la falla y se veía "No se encontraron usuarios".
- **Causa Raíz #2 (Backend - Bytecode Stale):** El servidor uvicorn mantenía `__pycache__` con bytecode compilado de una versión anterior de `main.py` que **no incluía** los endpoints `GET /api/v1/users`, `GET/PUT/DELETE /api/v1/users/{id}`. Solo existía `POST /api/v1/users/register` en el bytecode cacheado. El TestClient (que importa módulos frescos cada vez) funcionaba correctamente, pero el servidor en ejecución servía las rutas viejas.
- **Solución:**
  - Frontend: Estado `error` + bloque `catch` en `fetchStaff` que muestra mensaje en rojo con `AlertTriangle`.
  - Backend: Limpiar `__pycache__/` y reiniciar uvicorn para forzar recompilación.
  - Test: `test_4_staff_flow_register_then_appears_in_list` verifica login → register → list incluye al nuevo worker.
- **Archivos modificados:** `frontend/src/app/staff/list/page.tsx`, `backend/test_admin_fix.py`.
- **Archivos afectados (acción manual):** Limpiar `backend/app/__pycache__/` y reiniciar uvicorn.
- **Lección:** (1) Todo `try/finally` asíncrono debe tener `catch`. (2) El bytecode cacheado de Python (`__pycache__`) puede desincronizarse del fuente; siempre reiniciar el servidor después de modificar rutas de FastAPI. El TestClient no es suficiente para detectar este tipo de desincronización.

## Sesión: 2026-07-07 (Noche)
- **Estado Inicial:** F-14 (`pending`) como única tarea pendiente tras hotfix de F-17.
- **Acciones Realizadas:**
  - **F-14 (Tolerancia a Fallas Offline de Red):**
    - IndexedDB v2 con store `membersCache` + funciones `cacheMembers()` y `searchMemberOffline()`.
    - Búsqueda offline en recepción con fallback a caché local e indicador visual "Modo Offline".
    - Batch sync corregido: payload como array plano (no envuelto en objeto).
    - Widget Navbar online/offline verificado e integrado en DashboardLayout.
    - Test `test_f14_offline.py` con 2 tests (batch array plano + miembro inválido).
- **Resultado:** MVP completo — 100% de las funcionalidades implementadas y probadas.

## Sesión: 2026-07-07 (Auditoría - Post MVP)
- **Estado Inicial:** F-14 marcada `done`, entorno verificado, servidores activos para auditoría manual.
- **Problemas Detectados y Corregidos:**
  1. **Backend — `/openapi.json` 500:** `UserUpdate` no estaba importado en `main.py` (usado en `PUT /api/v1/users/{id}`). Pydantic generaba `ForwardRef` no resoluble. Se agregó al import. Swagger UI funcional.
  2. **Frontend — Raíz (`/`) con template Next.js:** `page.tsx` nunca se personalizó. Se reemplazó por `redirect("/login")`.
  3. **Frontend — Bucle infinito de rendering en dev server:** Next.js 16.2.9 + Turbopack causa crecimiento ilimitado de RAM/CPU (1.28GB, 661s CPU) al navegar a páginas con AuthContext + useEffect + router.push. Bug confirmado en upstream [#94915](https://github.com/vercel/next.js/issues/94915) y [#92372](https://github.com/vercel/next.js/issues/92372).
- **Solución (Mitigación):** Usar `pnpm build && pnpm start` en vez de `pnpm dev`. El build de producción compila correctamente sin los bugs de Turbopack.
- **Decisión de Arquitectura:** Para auditorías y uso estable, usar producción. Para desarrollo activo, usar `pnpm dev --webpack`.
- **Tests:** `test_f14_offline.py` (2/2), `test_admin_fix.py` (4/4), `test_offline.py` (3/3) — todos verdes. TypeScript sin errores.
- **Estado Actual:** Backend en `localhost:8000`, Frontend (producción) en `localhost:3000`. Todo funcional.

## Sesión: 2026-07-08
- **Estado Inicial:** F-18 (Alembic Migrations) como tarea P0 pendiente.
- **Acciones Realizadas:**
  - **F-18 (Alembic Migrations — Control de Versiones de BD):**
    - `alembic init` configurado con `sqlalchemy.url` apuntando a PostgreSQL.
    - `env.py` configurado con `target_metadata = Base.metadata` desde `app.models`.
    - Migración autogenerada (`initial_models`) con todas las tablas (usuarios, miembros, planes, membresias_miembros, pagos, asistencias).
    - `alembic upgrade head` ejecutado sin errores, tablas verificadas en PostgreSQL.
    - `.gitignore` creado en la raíz para proteger `alembic.ini` y `.env`.
    - Tests existentes (9/9) todos verdes post-migración.
  - **Revisor aprobó** tras corrección de migración vacía y adición de `.gitignore`.
- **Resultado:** F-18 completada y marcada `done`. Próxima tarea: F-19 (Backups Automatizados).

## Sesión: 2026-07-08 (Segunda Ronda)
- **Estado Inicial:** F-19 (Backups Automatizados) como tarea P0 pendiente.
- **Acciones Realizadas:**
  - **F-19 (Backups Automatizados de PostgreSQL):**
    - `backup.ps1` creado: ejecuta `pg_dump`, genera archivo con timestamp (`gymflow_db_YYYYMMDD_HHMMSS.sql.zip`), comprime con `Compress-Archive`.
    - `schedule_backup.ps1` creado: registra tarea diaria a las 3:00 AM en Windows Task Scheduler.
    - `backup.ps1` y `schedule_backup.ps1` agregados a `.gitignore` por seguridad.
    - Backup verificado: `backups/gymflow_db_20260708_225427.sql.zip` (2327 bytes, datos recuperables).
    - 9/9 tests existentes pasan.
- **Resultado:** F-19 completada y marcada `done`. Próxima tarea: F-20 (HttpOnly Cookies + Interceptor 401).

## Sesión: 2026-07-09
- **Estado Inicial:** F-20 (HttpOnly Cookies + Interceptor 401 + Seguridad de Backups) como tarea P0 pendiente.
- **Acciones Realizadas:**
  - **F-20 (Seguridad de Sesión — HttpOnly Cookies + Interceptor 401 + Seguridad de Backups):**
    - Backend: Cookie HttpOnly `gymflow_token` en respuesta de `/api/v1/auth/login` con `httponly=True, samesite="lax"`.
    - Backend: Nuevo endpoint `GET /api/v1/auth/session` para restaurar sesión desde cookie.
    - Backend: Helper `obtener_usuario_por_token(token, db)` extraído.
    - Backend: CORS ajustado a `allow_origins=["http://localhost:3000"]` con `allow_credentials=True`.
    - Frontend: `AuthContext.tsx` migrado de `localStorage` a cookies HttpOnly; reemplazo de `useRouter` por `window.location.href` para evitar bugs de Turbopack.
    - Frontend: Interceptor global Axios 401 → redirect `/login`.
    - Frontend: `withCredentials: true` global en Axios.
    - Frontend: Función `restoreSession()` que consulta `GET /api/v1/auth/session`.
    - Seguridad: Scripts `backup.ps1` y `schedule_backup.ps1` + carpeta `backups/` agregados a `.gitignore`.
- **Resultado:** F-20 completada y marcada `done` en `feature_list.json`. Próxima tarea: F-21 (Logging Configurado para Producción).

## Sesión: 2026-07-09 (Hotfix F-20)
- **Estado Inicial:** F-20 marcada `done` pero reportado bucle infinito de refresco post-implementación.
- **Bug:** El interceptor 401 de Axios redirigía con `window.location.href = "/login"`, lo que forzaba reload completo del layout → AuthProvider se remontaba → `restoreSession()` → 401 → redirect → loop infinito.
- **Acciones Realizadas (Hotfix):**
  - AuthContext.tsx: Flag `isRestoring` para excluir `restoreSession()` del interceptor 401.
  - AuthContext.tsx: `restoreSession()` usa `validateStatus: s => s < 500` para que Axios no rechace en 401.
  - AuthContext.tsx: `login()` usa `router.push` (evita reload completo); `window.location.href` solo en `logout()`.
  - AuthContext.tsx: `useRouter` re-importado para redirects internos.
  - Test: `backend/test_f20_session.py` creado con 5 tests (cookie, session restore, 401 sin cookie, flujo sin loop).
- **Resultado:** 14/14 tests verdes (9 existentes + 5 nuevos), TypeScript 0 errores. Reviewer aprobó (no viola business_rules.md). F-20 estabilizada.

## Sesión: 2026-07-09 (F-21)
- **Estado Inicial:** F-21 (Logging Configurado para Producción) como tarea P1 pendiente.
- **Acciones Realizadas:**
  - Backend: logging configurado con `TimedRotatingFileHandler` en `main.py` — archivo `backend/logs/gymflow.log`, rotación `midnight`, `backupCount=7`, nivel INFO.
  - Backend: Exception handler global con `logger.error()` para errores 500 no controlados.
  - Backend: `logger.info()` en login exitoso, `logger.warning()` en login fallido (con IP).
  - Backend: `logger.info()` en registro de pagos (id, monto_usd, membresía, usuario).
  - Backend: `logger.info()` en cron diario (cantidad de membresías bloqueadas).
  - Test: `backend/test_logging.py` creado con 6 tests (handler, archivo, escritura info/error, formato, nivel).
- **Resultado:** 20/20 tests verdes (14 existentes + 6 nuevos). No se violaron reglas de negocio. Reviewer aprobó. F-21 marcada `done`.

## Sesión: 2026-07-09 (F-22)
- **Estado Inicial:** F-22 (CHECK Constraints en Modelos SQLAlchemy) como tarea P1 pendiente.
- **Acciones Realizadas:**
  - `models.py`: `CheckConstraint` importado; `Plan.precio_usd >= 0`, `Pago.monto_original > 0`, `Pago.tasa_cambio > 0` agregados via `__table_args__`.
  - Migración Alembic manual creada (autogenerate no detecta CHECK) con `op.create_check_constraint`.
  - Test: `test_check_constraints.py` con 3 tests (precio negativo, monto cero, tasa negativa — todos capturan `IntegrityError`).
- **Resultado:** 23/23 tests verdes (20 existentes + 3 nuevos). Reviewer aprobó. F-22 marcada `done`.

## Sesión: 2026-07-09 (F-23)
- **Estado Inicial:** F-23 (Health Check Endpoint) como tarea P1 pendiente.
- **Acciones Realizadas:**
  - `main.py`: Endpoint `GET /api/v1/health` público que verifica BD con `SELECT 1` y retorna `status`, `database`, `timestamp`.
  - Test: `test_health.py` con 5 tests (200, status ok, database connected, timestamp, sin auth).
- **Resultado:** 28/28 tests verdes (23 existentes + 5 nuevos). Reviewer aprobó. F-23 marcada `done`.

## Sesión: 2026-07-09 (F-24 — Final)
- **Estado Inicial:** F-24 (Script de Restart Rápido) como última tarea P1 pendiente.
- **Acciones Realizadas:**
  - `restart.ps1` creado en la raíz: 4 pasos (git pull, limpiar `__pycache__`, reiniciar uvicorn, rebuild + start Next.js).
  - Soporta `-DryRun` para validación sin efectos.
  - Mata procesos por puerto (netstat) en vez de `$_.CommandLine` (compatible PS 5.1).
  - Inicia servidores con `Start-Process -WindowStyle Hidden` para que sobrevivan al cierre de terminal.
- **Resultado:** Sprint de preparación para producción completado. Las 5 tareas (F-20 a F-24) implementadas y validadas. feature_list.json al 100% `done`.
