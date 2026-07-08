# Backlog — Memoria de Aplazables y Descartados

> Archivo de memoria externa para tareas identificadas como no críticas para el MVP de un solo gimnasio (solopreneur). Se re-evaluarán post-producción.

## Aplazables (Post-MVP)

| Item | Motivo de Aplazamiento |
|------|------------------------|
| **Soft-Delete Global Middleware** | Actualmente el filtro `estado_logico == True` se hace manual endpoint por endpoint. Bajo riesgo si se mantiene disciplina. Implementar como `@property` del modelo o middleware cuando el código crezca. |
| **Debounce en Búsqueda de Recepción** | El buscador actual dispara en `onSubmit`, no en `onKeyPress`. No hay saturación de llamadas API. Redundante mientras no se implemente búsqueda en tiempo real. |
| **Skeleton Components para Tablas** | Las tablas usan `Loader2` spinner genérico. Funcional. Mejorar UX con esqueletos cuando sobre tiempo. |
| **Sidebar Responsive (Hamburguesa)** | El sidebar es `w-64` fijo, sin colapso en móvil. Aceptable si el gimnasio opera con tablets/desktop. Si requieren celulares, sube a prioridad. |
| **Passlib vs Raw bcrypt** | El código usa `bcrypt` directamente en vez de `passlib[bcrypt]`. Funcionalmente idéntico. Refactor cosmético, no urgente. |
| **CORS Restrictivo (`allow_origins` fijo)** | Actualmente `allow_origins=["*"]`. Para MVP de 1 gimnasio es aceptable. Restringir cuando haya múltiples tenants o frontend externo. |

## Descartados (No Implementar)

| Item | Motivo |
|------|--------|
| **CHECK Constraint `fecha_vencimiento >= fecha_inicio` en BD** | Validarlo en Pydantic (`model_validator`) es suficiente para MVP. La constraint en BD es nice-to-have. |
| **`.env.example`** | Útil para equipos/open-source. Para solopreneur con 1 sola máquina, innecesario. |
