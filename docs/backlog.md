# Backlog — Memoria de Aplazables y Descartados

> Archivo de memoria externa para tareas identificadas como no críticas para el MVP de un solo gimnasio (solopreneur). Se re-evaluarán post-producción.

## Aplazables (Post-MVP)

| Item | Motivo de Aplazamiento |
|------|------------------------|
| **Soft-Delete Global Middleware** | Actualmente el filtro `estado_logico == True` se hace manual endpoint por endpoint. Bajo riesgo si se mantiene disciplina. Implementar como `@property` del modelo o middleware cuando el código crezca. |

| **Passlib vs Raw bcrypt** | El código usa `bcrypt` directamente en vez de `passlib[bcrypt]`. Funcionalmente idéntico. Refactor cosmético, no urgente. |
| **CORS Restrictivo (`allow_origins` fijo)** | Ya no aplica. Migrado a `allow_origins=["http://localhost:3000"]` con `allow_credentials=True` en F-20. |
| **Enum `MembershipStatus` incompleto** | P3 — El enum en `models.py` solo incluye `por_vencer` y `vencido`. Faltan `activo` y `en_gracia`. El cálculo dinámico funciona, pero es incoherente con la documentación y el frontend. |
| **Período de gracia hardcodeado (5 días)** | P3 — `calcular_estado_miembro()` usa literal `5` para gracia y `6` para cron. No parametrizado en DB ni config. Aceptable para MVP, frágil si cambia la regla. |
| **Semáforo duplicado inline** | P4 — La lógica del semáforo (colores, iconos, etiquetas) está copiada en `reception/page.tsx` y `members/list/page.tsx`. Extraer a componente compartido `SemaforoBadge`. |
| **Sin endpoint dedicado de cambio de contraseña** | P4 — `PUT /api/v1/users/{id}` permite actualizar datos, pero no hay un endpoint `/change-password` con validación de contraseña anterior. |

## Descartados (No Implementar)

| Item | Motivo |
|------|--------|
| **CHECK Constraint `fecha_vencimiento >= fecha_inicio` en BD** | Validarlo en Pydantic (`model_validator`) es suficiente para MVP. La constraint en BD es nice-to-have. |
| **`.env.example`** | Útil para equipos/open-source. Para solopreneur con 1 sola máquina, innecesario. |
