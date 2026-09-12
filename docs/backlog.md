# Backlog — Memoria de Aplazables y Descartados

> Archivo de memoria externa para tareas identificadas como no críticas para el MVP de un solo gimnasio (solopreneur). Se re-evaluarán post-producción.
>
> **Nota técnica (Fase 3):** Los ítems de optimización de queries (OPT-01, OPT-02) y parametrización de base de datos (OPT-03, OPT-04) se mantienen congelados en el backlog hasta el inicio de la Fase 4, donde se rediseñará la arquitectura para soportar Multi-Tenancy (SaaS).

## Aplazables (Post-MVP)

> **Nota (Fase 4 Extensión):** Los ítems "Período de gracia hardcodeado" y "Visualización de días restantes en Recepción" fueron promovidos a `feature_list.json` como F4-09 y F4-08 respectivamente. Ya no están en backlog.

| Item | Motivo de Aplazamiento |
|------|------------------------|
| **Soft-Delete Global Middleware** | Actualmente el filtro `estado_logico == True` se hace manual endpoint por endpoint. Bajo riesgo si se mantiene disciplina. Implementar como `@property` del modelo o middleware cuando el código crezca. |

| **Passlib vs Raw bcrypt** | El código usa `bcrypt` directamente en vez de `passlib[bcrypt]`. Funcionalmente idéntico. Refactor cosmético, no urgente. |
| **CORS Restrictivo (`allow_origins` fijo)** | Ya no aplica. Migrado a `allow_origins=["http://localhost:3000"]` con `allow_credentials=True` en F-20. |
| **Enum `MembershipStatus` incompleto** | P3 — El enum en `models.py` solo incluye `por_vencer` y `vencido`. Faltan `activo` y `en_gracia`. El cálculo dinámico funciona, pero es incoherente con la documentación y el frontend. |
| **Semáforo duplicado inline** | P4 — La lógica del semáforo (colores, iconos, etiquetas) está copiada en `reception/page.tsx` y `members/list/page.tsx`. Extraer a componente compartido `SemaforoBadge`. |
| **Sin endpoint dedicado de cambio de contraseña** | P4 — `PUT /api/v1/users/{id}` permite actualizar datos, pero no hay un endpoint `/change-password` con validación de contraseña anterior. |

## Recomendaciones Futuras / Icebox (Post-Auditoría Técnica)

| ID | Item | Prioridad | Motivo |
|----|------|-----------|--------|
| OPT-01 | **Optimizar N+1 en `get_payment_detail`** (F2-02) | P2 | El endpoint carga 4 relaciones lazy (miembro, plan, registrador) en consultas separadas. Agregar `joinedload()` en el query ORM. Correcto funcionalmente, mejora rendimiento en paneles con muchos clics. |
| OPT-02 | **Optimizar N+1 en `get_miembros_vencidos`** (F2-03) | P2 | El bucle Python accede a `m.membresias` por cada miembro vencido. Usar `selectinload(Miembro.membresias)`. Escala mal con 50+ vencidos. |
| OPT-03 | **Índice en `pagos.fecha_pago`** | P3 | F2-01 filtra por rango de fechas en `Pago.fecha_pago` sin índice. Añadir `Index("idx_pagos_fecha_pago", Pago.fecha_pago)` + migración Alembic. Aceptable mientras la tabla sea pequeña (<10k registros). |
| OPT-04 | **Migrar fechas a timezone-aware** | P4 | `_calcular_rango_fechas` retorna naive datetimes. Internamente consistente porque todo usa `utcnow()`, pero frágil si el servidor cambia de huso. Migrar a `timezone.utc`. Muy baja probabilidad de impacto. |
| OPT-05 | **Búsqueda Server-Side/Debounce en Lista de Miembros** | P2 | `members/list/page.tsx:75-79` hace filtrado en cliente sin debounce. Solución: migrar a búsqueda server-side con debounce de 300ms (reutilizar patrón F2-04) para evitar degradación con cientos de registros. |
| OPT-09 | **Flexibilidad de Ancho en Skeletons de Tablas** | P3 | `TableSkeleton.tsx:11` usa un array cíclico fijo que desalinea las columnas si son mayores a 5. Solución: calcular el ancho proporcional dinámicamente (`width: ${100 / columns}%`) o recibir `widths` como prop array. |
| OPT-10 | **Accesibilidad (A11y) en Skeletons** | P3 | `TableSkeleton` carece de soporte para lectores de pantalla. Solución: añadir `role="status"`, `aria-label="Cargando contenido"` y heredar `className` en el contenedor raíz. |
| OPT-11 | **Accesibilidad por Teclado en Overlay Sidebar** | P3 | El overlay mobile de la sidebar no se puede cerrar usando métodos estándar en tablets. Solución: añadir un listener `useEffect` para escuchar la tecla "Escape" y gatillar el cierre. |
| OPT-12 | **Soporte de color-scheme en Selectores de Dropdowns** | P3 | `globals.css` no cubre `<select>` nativos dentro de dropdowns con clase `kinetic-glass`, lo que podría causar discontinuidad visual de fondo en ciertos motores de renderizado. Solución: añadir `color-scheme: dark;` al selector del `select` en `globals.css` para forzar la paleta oscura nativa. |
| OPT-13 | **Preservación de Estado de Scroll en Sidebar Mobile** | P2 | El renderizado condicional `{mobileOpen && (...)}` en `Sidebar.tsx:110` desmonta el componente y pierde la posición de scroll al cerrarse. No es crítico actualmente por el bajo número de ítems (~7). Solución Post-MVP: si el menú crece, extraer el estado de scroll a un `useRef` o usar CSS `overscroll-behavior`. |
| OPT-14 | **Atributos de Accesibilidad ARIA en Sidebar Mobile** | P2 | El botón hamburguesa y el botón de cierre en `Sidebar.tsx` carecen de propiedades ARIA completas para lectores de pantalla (WCAG 2.1). Solución: agregar `aria-controls="mobile-sidebar"` y `aria-expanded={mobileOpen}` al hamburguesa; `id` y `role` al `<aside>`; y `aria-label="Cerrar menú"` al botón X. |

## Recomendaciones Fase 4 — Auditoría Técnica (Post-Auditoría)

> Hallazgos clasificados como P2-P3 durante la auditoría de F4-01→F4-05. No bloquean producción pero mejoran seguridad y coherencia.

| ID | Item | Prioridad | Motivo de Aplazamiento |
|----|------|-----------|------------------------|
| H-08 | **register-gym-admin: cédula collision → error 500** | P2 | El endpoint genera cédula `G-{id}` sin verificar unicidad. Si colisiona, el COMMIT falla con IntegrityError que se propaga como 500 genérico. Riesgo bajo porque `id` es secuencial. Fix: try/except IntegrityError con 400 descriptivo. |
| H-09 | **/auth/session retorna JWT en body** | P2 | El endpoint retorna el access_token completo en el body. La cookie httponly ya maneja la autenticación. Exposición teórica a XSS si un script malicioso se ejecuta en el dominio. Fix: remover `access_token` de la respuesta. |
| H-10 | **POST /members accesible por worker** | P2 | El endpoint usa `requerir_trabajador`. Un worker puede crear miembros sin justificación clara según business_rules.md §4. Puede ser intencional para recepción. Fix: cambiar a `requerir_admin` o documentar en business_rules.md. |
| H-11 | **Campo observaciones en schema pero no en modelo** | P2 | El schema PagoCreate incluye `observaciones` pero el modelo Pago no tiene la columna. El frontend envía datos que se descartan silenciosamente. Fix: agregar columna al modelo + migración, o remover del schema. |
| H-12 | **requerir_super_admin usa string vs Enum** | P3 | La función auth.py:94 compara `"super_admin"` como string literal en vez de `UserRole.super_admin`. Funciona correctamente pero es inconsistente con `requerir_admin`. Fix: cambio cosmético. |
| H-13 | **membresias_miembros sin gym_id FK** | P3 | La tabla membresias_miembros no tiene columna gym_id. Requiere JOIN con miembros para filtrar por sede. Diseño defensivo: si en futuro se agrega un endpoint directo de membresías, podría filtrarse incorrectamente. Fix: agregar FK + migración. |
| H-14 | **token_sede visible en URL sin validación frontend** | P3 | La página /register-gym/{token_sede} no valida formato UUID antes de enviar al backend. El backend valida correctamente, pero es buena práctica validar en frontend. Fix: regex `/^[0-9a-f-]{36}$/i` antes del submit. |

## Descartados (No Implementar)

| Item | Motivo |
|------|--------|
| **CHECK Constraint `fecha_vencimiento >= fecha_inicio` en BD** | Validarlo en Pydantic (`model_validator`) es suficiente para MVP. La constraint en BD es nice-to-have. |
| **`.env.example`** | Útil para equipos/open-source. Para solopreneur con 1 sola máquina, innecesario. |
