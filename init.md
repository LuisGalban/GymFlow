# Protocolo de Iniciación (init.md)
**Objetivo:** Verificar que el entorno de desarrollo de GymFlow es estable.

### Checklist de Ejecución Obligatoria:
1. **Verificación de Stack:**
   - [ ] Python >= 3.9 disponible (Backend FastAPI).
   - [ ] Node.js y PNPM instalados (Frontend Next.js).
2. **Conectividad:**
   - [ ] Conexión exitosa a PostgreSQL (Base de datos transaccional).
3. **Documentación:**
   - [ ] Archivo `feature_list.json` presente y legible.
   - [ ] `progress/current.md` listo para anotar el sprint actual

**Acción si falla:** El agente debe detenerse inmediatamente y reportar el error en la terminal, sin intentar modificar el código de la aplicación.
