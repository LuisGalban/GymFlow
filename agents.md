# 🤖 GymFlow Analytics: Mapa de Navegación de Agentes

Este archivo es el **punto de entrada obligatorio** para cualquier agente de IA que trabaje en este repositorio. Su propósito es guiarte a través del contexto del proyecto sin saturar tu ventana de tokens.

## 1. Protocolo de Inicio (Obligatorio)
Antes de realizar cualquier acción o escribir código, debes seguir estos pasos en orden:
1. **Ejecutar `init.md`**: Verifica que el entorno (Python 3.9+, FastAPI, PostgreSQL) esté estable.
2. **Consultar Estado**: Lee `progress/current.md` para entender el sprint actual.
3. **Elegir Tarea**: Lee `feature_list.json` y selecciona la siguiente tarea con estado `"pending"`.

## 2. Mapa del Repositorio (Contexto por Demanda)
Usa este mapa para saber qué archivos leer según tu tarea actual:

| Carpeta / Archivo | Contenido | Cuándo leerlo |
| :--- | :--- | :--- |
| `agents/` | Protocolos de Líder, Implementador y Revisor. | Al inicio de la sesión. |
| `docs/PRD.md` | Visión general y alcance del SaaS. | Para entender el "qué" hacemos. |
| `docs/business_rules.md` | Leyes financieras y de acceso (USD, Gracia, Semáforo). | Antes de tocar lógica de negocio. |
| `docs/design_system.md` | Tokens de Tailwind, colores y espaciado de 8px. | Antes de tocar el Frontend. |
| `progress/` | Memoria de corto (`current.md`) y largo plazo (`history.md`). | Siempre al empezar y terminar. |
| `src/` | Código fuente de la aplicación (FastAPI/Next.js). | Durante la implementación. |

## 3. Reglas Duras e Invariantes (Innegociables)
Como agente de GymFlow, debes respetar estas leyes para evitar "alucinaciones" críticas:
*   **Prohibido DELETE Físico**: Toda eliminación debe ser **Borrado Lógico** usando `is_active = False` o `estado_logico = False`.
*   **Normalización USD**: Todas las transacciones deben registrarse con su equivalente en dólares según la tasa del momento.
*   **Seguridad Estricta**: No confíes en los inputs; usa **Pydantic (Backend)** y **Zod (Frontend)** para validaciones.
*   **Test-First**: No marques una tarea como `done` sin antes escribir y pasar un test de validación (Ciclo Rojo-Verde-Refactor).
*   **One Feature at a time**: Prohibido trabajar en múltiples tareas simultáneamente.

## 4. Estándar de Comunicación y Ahorro de Tokens
*   **Respuestas Quirúrgicas**: Responde solo con una línea de estado (Ej: `DONE: [ID]`) a menos que se pida una explicación técnica.
*   **Uso del Disco**: No devuelvas bloques de código gigantes en el chat si ya han sido escritos en los archivos correspondientes.
*   **Bloqueos**: Si algo falla o la documentación es ambigua, detente, anota el error en `progress/current.md` con el estado `BLOCKER` y espera instrucciones.

---