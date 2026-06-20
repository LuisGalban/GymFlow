# Reglas de Negocio Estrictas (GymFlow Analytics)

Este documento detalla las reglas operativas y financieras que rigen la lógica de negocio del sistema GymFlow Analytics.

---

## 1. Período de Gracia y Estados de Membresía
- **Estado Activo (`activo`):** Si `fecha_vencimiento >= fecha_actual`. El acceso está permitido.
- **Estado En Gracia (`en_gracia`):** Si la membresía ha expirado pero está dentro de los **5 días calendario** siguientes a la fecha de vencimiento (`fecha_actual > fecha_vencimiento` Y `dias_transcurridos <= 5`).
  - *Acción:* Se permite el acceso al atleta pero la interfaz de recepción emite una advertencia visual que indica los días restantes de gracia.
- **Estado Vencido (`vencido`):** A partir del **6° día calendario** tras el vencimiento (`dias_transcurridos >= 6`), la membresía se bloquea.
  - *Acción:* Bloqueo de acceso físico inmediato y visualización de una alerta carmesí en recepción.

---

## 2. Gestión Financiera Multidivisa
- **Normalización contable a USD:** Todas las transacciones se deben registrar en la base de datos con su valor equivalente en dólares estadounidenses (USD) usando la tasa de cambio vigente en el segundo exacto de la operación.
- **Pagos al 100%:** No se permiten abonos ni saldos pendientes de pago en el módulo de caja para el MVP. Las membresías se registran liquidadas al 100% o no se procesan.

---

## 3. Semáforo de Control de Acceso (UI de Recepción)
El módulo de recepción de un solo clic se rige por un esquema visual estricto según el estado del atleta:
- 🟢 **Activo:** Color verde (`text-emerald-600 / bg-emerald-50`). Acceso aprobado.
- 🟡 **En Gracia / Por Vencer:** Color ámbar (`text-amber-500 / bg-amber-50`). Indica proximidad de vencimiento (últimos 3 días del plan) o período de gracia activo.
- 🔴 **Vencido / Bloqueado:** Color rojo (`text-rose-600 / bg-rose-50`). Bloqueo de acceso.

---

## 4. Control de Acceso Basado en Roles (RBAC)
- **Administrador (`admin`):** Acceso global a métricas de caja, reportes financieros y configuración de tarifas de planes.
- **Trabajador (`worker`):** Acceso puramente operativo (búsquedas de miembros, check-ins y registro inicial de pagos). Tiene deshabilitada la edición o eliminación de transacciones.

---

## 5. Integridad de Datos (Borrado Lógico)
- Queda prohibido el uso de la sentencia física `DELETE` en tablas críticas (usuarios, miembros, planes, pagos).
- La eliminación se realiza modificando la bandera `estado_logico = False` (o `is_active = False`). Las consultas del ORM deben filtrar automáticamente los registros desactivados.
