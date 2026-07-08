# Sprint Actual: Post-MVP — Auditoría y Estabilización

## Estado del Entorno
- **Python 3.14.5** ✅ (vía `backend/venv`)
- **Node.js v24.16.0 + PNPM 11.8.0** ✅
- **PostgreSQL 18.4** — Conexión exitosa a `gymflow_db` ✅
- **init.md:** Entorno verificado y estable ✅
- **Frontend:** Servidor de producción activo (`pnpm start`) ✅
- **Backend:** FastAPI en `localhost:8000` ✅

## Estado: Auditoría Completada — Estabilizado ✅

### Correcciones Realizadas Post-Auditoría
1. **Backend** — `UserUpdate` faltante en import (`main.py:13`). `/openapi.json` ahora responde 200 OK.
2. **Frontend** — Raíz `/` ahora redirige a `/login` (antes template Next.js default).
3. **Dev Server** — Bug de Turbopack identificado y mitigado usando servidor de producción.

### Tests (Todos Verdes)
- `backend/test_f14_offline.py` — 2/2
- `backend/test_admin_fix.py` — 4/4
- `backend/test_offline.py` — 3/3
- TypeScript: 0 errores

### Nota Técnica
Next.js 16.2.9 + Turbopack tiene bugs confirmados de bucle de rendering con AuthContext + useEffect + router.push. Para auditoría usar `pnpm build && pnpm start`. Para desarrollo usar `pnpm dev --webpack`.

## Sprint Siguiente: Preparación para Producción

Luego del análisis técnico completo, se refinó la hoja de ruta priorizando **seguridad y estabilidad** antes del despliegue en producción. Se agregaron 7 nuevas tareas a `feature_list.json`:

| ID | Prioridad | Tarea |
|----|-----------|-------|
| F-18 | P0 | Alembic Migrations — Control de versiones de BD |
| F-19 | P0 | Backups Automatizados (pg_dump) |
| F-20 | P0 | HttpOnly Cookies + Interceptor 401 |
| F-21 | P1 | Logging Configurado para Producción |
| F-22 | P1 | CHECK Constraints en Modelos SQLAlchemy |
| F-23 | P1 | Health Check Endpoint |
| F-24 | P1 | Script de Restart Rápido (One-Click) |

Tareas aplazadas y descartadas movidas a `docs/backlog.md`.

## Próximo Paso
- Iniciar **F-18 (Alembic Migrations)** como primera tarea del sprint de preparación para producción.
