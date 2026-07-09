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

## Sprint de Preparación para Producción — F-20 Estabilizado (Hotfix)

### Correcciones Realizadas (F-20)
1. **Backend** — Cookie HttpOnly `gymflow_token` agregada en respuesta de `/api/v1/auth/login` mediante `response.set_cookie()` con flags `httponly=True, samesite="lax", secure=False` (dev).
2. **Backend** — Nuevo endpoint `GET /api/v1/auth/session` que lee el token de la cookie, lo decodifica y devuelve usuario + token.
3. **Backend** — Helper `obtener_usuario_por_token(token, db)` extraído para reutilización.
4. **Backend** — CORS ajustado a `allow_origins=["http://localhost:3000"]` con `allow_credentials=True`.
5. **Frontend** — `AuthContext.tsx` migrado de `localStorage` a cookie session: elimina `localStorage.getItem/setItem`, usa `restoreSession()` vía `GET /api/v1/auth/session`.
6. **Frontend** — Interceptor global de Axios (401 → redirect `/login`) agregado tanto en instancia default como en `api` exportada.
7. **Frontend** — `withCredentials: true` configurado globalmente en Axios.
8. **Frontend** — `useRouter` reemplazado por `window.location.href` para evitar dependencia del router de Next.js.
9. **[F-19 Fix]** `backup.ps1` y `schedule_backup.ps1` agregados a `.gitignore`.
10. **[F-19 Fix]** Carpeta `backups/` agregada a `.gitignore`.

### Hotfix Aplicado (Bucle Infinito de Refresco)
1. **AuthContext.tsx** — Flag `isRestoring` añadido para diferencial el interceptor 401: no redirige durante `restoreSession()`.
2. **AuthContext.tsx** — `restoreSession()` usa `validateStatus: s => s < 500` para evitar que axios rechace automáticamente en 401.
3. **AuthContext.tsx** — `login()` usa `router.push` en vez de `window.location.href` para evitar reload completo post-login.
4. **AuthContext.tsx** — `useRouter` re-importado para redirects internos; `window.location.href` solo se usa en `logout()`.
5. **`backend/test_f20_session.py`** — 5 tests nuevos que validan cookie HttpOnly, session restore, 401 sin cookie y flujo completo sin loop.
6. **Tests:** 14/14 verdes (9 existentes + 5 nuevos), TypeScript 0 errores.
7. **Reviewer:** Aprobó — no viola business_rules.md.

## Completada — F-21 (Logging Configurado para Producción)

### Criterios de Aceptación ✅
1. ✅ `logging.basicConfig` + `TimedRotatingFileHandler` en `main.py` con nivel INFO y `force=True`.
2. ✅ Archivo de log en `backend/logs/gymflow.log` con rotación `when="midnight"` y `backupCount=7`.
3. ✅ Endpoints críticos registran eventos: login (exitoso + fallido), pagos (register + by-cedula), cron, y error handler global 500.

### Resumen de Cambios
| Archivo | Cambio |
|---------|--------|
| `backend/app/main.py:1-29` | Import logging + TimedRotatingFileHandler, config logging con `force=True`, logger module-level |
| `backend/app/main.py:64-71` | Exception handler global con `logger.error()` para 500 |
| `backend/app/main.py:90-95` | Login: `logger.warning()` en fallido, `logger.info()` en exitoso |
| `backend/app/main.py:427` | Payment register: `logger.info()` con id, monto, membresía, usuario |
| `backend/app/main.py:501` | Payment by-cedula: `logger.info()` con id, monto, cédula, usuario |
| `backend/app/main.py:598` | Cron: `logger.info()` con count de membresías bloqueadas |
| `backend/test_logging.py` | 6 tests: handler configurado, archivo existe, escritura info/error, formato correcto, nivel INFO |
| `backend/logs/` | Directorio creado con `.gitkeep` |

### Tests
- 6 tests nuevos en `test_logging.py`: **6/6 verdes**
- Suite completa (20 tests): **20/20 verdes**

## Completada — F-22 (CHECK Constraints en Modelos SQLAlchemy)

### Criterios de Aceptación ✅
1. ✅ `__table_args__` con `CheckConstraint` en `Plan.precio_usd >= 0`, `Pago.monto_original > 0`, `Pago.tasa_cambio > 0`.
2. ✅ Migración Alembic manual (`add_check_constraints_precio_monto_tasa`) que aplica constraints sin drop.
3. ✅ Test que inserta precio negativo, monto cero y tasa negativa — todos rechazados por BD.

### Resumen de Cambios
| Archivo | Cambio |
|---------|--------|
| `backend/app/models.py:4-6` | Importado `CheckConstraint` |
| `backend/app/models.py:67-69` | `Plan.__table_args__` con `ck_plan_precio_usd_no_negativo` |
| `backend/app/models.py:96-99` | `Pago.__table_args__` con `ck_pago_monto_original_positivo` y `ck_pago_tasa_cambio_positivo` |
| `backend/alembic/versions/*add_check_constraints_*.py` | Migración manual con `op.create_check_constraint` |
| `backend/test_check_constraints.py` | 3 tests que verifican `IntegrityError` con nombre de constraint |

### Tests
- 3 tests nuevos en `test_check_constraints.py`: **3/3 verdes**
- Suite completa (23 tests): **23/23 verdes**

## Completada — F-23 (Health Check Endpoint)

### Criterios de Aceptación ✅
1. ✅ Endpoint `GET /api/v1/health` retorna `{"status": "ok", "database": "connected", "timestamp": "..."}`.
2. ✅ Verifica conexión activa a PostgreSQL mediante `db.execute(text("SELECT 1"))`.
3. ✅ No requiere autenticación — endpoint público, sin dependencia de `obtener_usuario_actual`.

### Resumen de Cambios
| Archivo | Cambio |
|---------|--------|
| `backend/app/main.py:99-109` | Nuevo endpoint `GET /api/v1/health` con verificación de BD |
| `backend/test_health.py` | 5 tests: status 200, status "ok", database "connected", timestamp, sin auth |

### Tests
- 5 tests nuevos en `test_health.py`: **5/5 verdes**
- Suite completa (28 tests): **28/28 verdes**

## Completada — F-24 (Script de Restart Rápido)

### Criterios de Aceptación ✅
1. ✅ Script `restart.ps1` creado en la raíz del proyecto.
2. ✅ Ejecuta secuencialmente: `git pull`, limpieza de `__pycache__`, reinicio de uvicorn, rebuild y restart de Next.js.
3. ✅ Ejecutable con un solo clic: `.\restart.ps1` o `.\restart.ps1 -DryRun` para simular.

### Resumen de Cambios
| Archivo | Cambio |
|---------|--------|
| `restart.ps1` | Script de 4 pasos: git pull, limpiar `__pycache__`, reiniciar uvicorn (por puerto 8000), rebuild + start Next.js (puerto 3000). Soporta `-DryRun`. Manejo de errores con `exit 1`. |

### Tests
- Validación de sintaxis PowerShell: `powershell -NoProfile -Command "& '.\restart.ps1' -DryRun"` ✅
- Suite backend completa (28 tests): **28/28 verdes** (sin regresiones)

### Pendientes
**— Ninguna. Todas las tareas del sprint de preparación para producción han sido completadas.**
