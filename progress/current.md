# Sprint Actual: Resiliencia Offline y QA (F-14 & F-15)

## Estado del Entorno
- **Python:** Virtualenv activado en `backend/venv` (Python 3.14.5).
- **Node.js:** Instalado (v24.16.0), gestor `pnpm` (11.8.0).
- **PostgreSQL:** Conexión exitosa a la base de datos `gymflow_db`.
- **Diagnóstico init.md:** Entorno verificado y estable.

## Tareas Completadas

### [x] F-14: Tolerancia a Fallas Offline de Red
- **Descripción:** Implementación de persistencia local y sincronización asíncrona.
- **Plan de Acción / Criterios de Aceptación:**
  1. [x] Crear almacén local `members_cache` en IndexedDB para búsquedas locales offline en recepción.
  2. [x] Implementar la cola de check-ins locales `offline_checkins_queue` en IndexedDB.
  3. [x] Modificar la lógica en `frontend/src/app/dashboard/reception/page.tsx` para interceptar la desconexión:
     - Buscar en `members_cache` al no haber red.
     - Almacenar check-ins en cola local al fallar la red.
     - Configurar `window.addEventListener("online")` para enviar los check-ins en lote mediante `/api/v1/asistencias/batch` y purgar la cola local.

### [x] F-15: Protocolo de QA y Pruebas Unitarias/Integración
- **Descripción:** Suite de validación de calidad técnica según el PRD sin dependencias externas pesadas.
- **Plan de Acción / Criterios de Aceptación:**
  1. [x] Escribir el script de prueba `backend/test_offline.py` usando `unittest`.
  2. [x] Ejecutar las pruebas utilizando el entorno virtual local para certificar:
     - Latencia de búsqueda optimizada (B-Tree index verificado en < 50ms).
     - Procesamiento de check-ins offline en lote sincronizados a `/api/v1/asistencias/batch`.
     - Segregación lógica de roles y acceso a KPIs de administrador.
  3. [x] Integrar reportes de tests y certificar el estado en `progress/history.md`.
