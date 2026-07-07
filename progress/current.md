# Sprint Actual: Gestión de Recepcionistas (F-17) — Post-Mortem

## Estado del Entorno
- **Python:** Virtualenv activado en `backend/venv` (Python 3.14.5).
- **Node.js:** Instalado (v24.16.0), gestor `pnpm` (11.8.0).
- **PostgreSQL:** Conexión exitosa a la base de datos `gymflow_db`.
- **Diagnóstico init.md:** Entorno verificado y estable.

## Estado: COMPLETADO ✅ (con hotfix)

### Tarea Completada
**F-17: Gestión de Recepcionistas (Staff) por Administrador**

### Bug Reportado
- Los recepcionistas creados no se visualizaban en `/staff/list` aunque estaban en la base de datos.
- Error visible tras el hotfix: `Request failed with status code 404`.

### Causa Raíz (doble)
1. **Frontend:** `fetchStaff` en `staff/list/page.tsx` tenía `try/finally` **sin `catch`**. Si `api.get()` fallaba, el error se ocultaba y se veía "No se encontraron usuarios".
2. **Backend:** El servidor uvicorn mantenía `__pycache__` con bytecode **obsoleto** de una versión anterior de `main.py` que no incluía `GET /api/v1/users` ni el resto de endpoints de F-17 (solo tenía `POST /api/v1/users/register`). El TestClient funcionaba porque importa módulos frescos, pero el servidor en ejecución usaba los `.pyc` viejos.

### Fix Aplicado
1. **Frontend `staff/list/page.tsx`:**
   - Agregado estado `error` (`useState<string | null>`).
   - Agregado bloque `catch` en `fetchStaff` que captura el error, muestra mensaje en UI y resetea `staff` a `[]`.
   - Agregado banner de error con icono `AlertTriangle` en la UI.
2. **Backend:** Limpiado `__pycache__` y reiniciado el servidor uvicorn para forzar recompilación fresca del bytecode.
3. **Test `test_admin_fix.py`:** Agregado test `test_4_staff_flow_register_then_appears_in_list` que valida el flujo completo:
   - Login como admin → registrar worker → listar users → worker aparece en la lista → borrado lógico.

### Validación
- 5 endpoints de F-17 verificados vía OpenAPI del servidor en ejecución.
- `GET /api/v1/users` devuelve 200 con lista completa tras reinicio.
- 4 tests backend pasando (0 regresiones).
- TypeScript: sin errores.

## Próximo Paso
- Avanzar a **F-14 (Tolerancia Offline)**.
