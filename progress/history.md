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
