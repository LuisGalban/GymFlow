GymFlow Analytics
Documento de Especificación Técnica y Requerimientos de Software (PRD Avanzado)
1. Visión y Definición Estratégica
1.1. Análisis del Contexto Regional (Maracaibo, Zulia)En el mercado fitness de Maracaibo y la región zuliana, predomina una gestión operativa obsoleta basada en registros físicos (cuadernos) o, en escenarios optimistas, hojas de cálculo locales aisladas. Dada la realidad socioeconómica de la región, marcada por fluctuaciones constantes, cortes eléctricos y dinámicas transaccionales complejas, esta desconexión tecnológica genera una "ceguera financiera" crítica. Los propietarios de gimnasios carecen de visibilidad en tiempo real sobre los ingresos netos reales, sufren fugas constantes de capital debido a membresías vencidas que no se detectan en el punto de acceso, y pierden trazabilidad histórica. GymFlow Analytics surge como la respuesta técnica de nivel de producción a esta ineficiencia, transformando la opacidad operativa en un flujo de datos auditable, transparente, rápido y centralizado.
1.2. Propuesta de Valor y Factor DiferenciadorGymFlow Analytics no es solo un software de administración estándar; es una herramienta de optimización de ingresos diseñada específicamente para adaptarse a la idiosincrasia económica local. Sus pilares estratégicos y técnicos son:
Accesibilidad Económica Nacional: Eliminación completa de las barreras de entrada impuestas por plataformas extranjeras cuyas licencias en divisas resultan prohibitivas y difíciles de costear localmente.
Interfaz de Baja Carga Cognitiva: Diseño UX/UI concebido para sustituir de forma natural el cuaderno físico, mitigando la resistencia al cambio por parte del personal de recepción mediante flujos visuales intuitivos.
Adaptación Transaccional Nativa: Soporte arquitectónico de primera clase para los métodos de pago dominantes en la zona (Pago Móvil, transferencias bancarias en Bolívares y efectivo multidivisa USD/Bs).
Blindaje Operativo Inmediato: Automatización estricta de alertas y control de accesos en puerta para asegurar que ningún usuario ingrese al recinto sin una membresía vigente, eliminando pérdidas por morosidad.
1.3. Modelo de Negocio (SaaS Escalable)
La plataforma se distribuye bajo un esquema de Software as a Service (SaaS) basado en niveles de suscripción, permitiendo a los centros de entrenamiento escalar su inversión tecnológica alineada con su crecimiento de usuarios activos:
Nivel de Suscripción
Umbral de Clientes Activos
Alcance Estratégico
Básico
Hasta 100 clientes activos
Centros de entrenamiento boutique, boxes de crossfit y estudios especializados.
Intermedio
Hasta 350 clientes activos
Gimnasios de escala media con requerimientos de flujo de caja constante.
Premium
Ilimitado
Centros deportivos de alto tráfico con múltiples sucursales y puntos de control masivos.

2. Reglas de Negocio Estrictas (Business Rules)
2.1. Gestión Financiera Multidivisa y Normalización de Datos HistóricosPara mitigar de raíz el riesgo cambiario derivado del entorno inflacionario local, el backend impone una regla matemática de normalización: toda transacción financiera (ingreso o egreso) debe registrarse obligatoriamente con su valor equivalente en dólares estadounidenses (USD) utilizando la tasa de cambio oficial o de referencia del mercado vigente en el milisegundo exacto de la operación. Esta tasa debe pasarse desde el cliente o capturarse mediante una API confiable. Esto garantiza que la contabilidad histórica, los reportes analíticos y las proyecciones mantengan una estabilidad real y comparable a lo largo de los meses, sin distorsiones por devaluación.
2.2. Integridad de Datos Cohesiva y Auditoría (Borrado Lógico Obligatorio)Queda explícitamente prohibido el uso de sentencias físicas SQL 'DELETE' sobre los registros de clientes, membresías, pagos o personal. La integridad referencial y la trazabilidad financiera son absolutas. La baja de cualquier entidad en el sistema se ejecutará de forma exclusiva mediante un patrón de Borrado Lógico estableciendo una bandera booleana 'estado_logico = False' (u 'is_active'). Las consultas normales del ORM filtrarán automáticamente estos registros, pero los datos permanecerán intactos en la base de datos para auditorías forenses, contables o fiscales.
2.3. Segregación de Funciones y Jerarquía de Seguridad en Flujo de CajaPara evitar fraudes internos y manipulaciones de caja, el sistema de control de acceso basado en roles (RBAC) impone restricciones rígidas:
Administrador (Propietario): Posee privilegios globales de superusuario. Es el único rol autorizado para visualizar balances consolidados, ganancias netas, modificar precios de planes, configurar el sistema y realizar ajustes manuales sobre el flujo de caja histórico.
Trabajador (Recepcionista): Rol estrictamente operativo limitado a la captura de datos: búsqueda de miembros, registro ágil de asistencias y captura inicial de formularios de pago. El sistema bloquea e inhabilita por completo cualquier capacidad de modificación, edición o eliminación de transacciones una vez procesadas.
2.4. Automatización de Accesos, Bloqueos y Motor de Reglas DiariasEl núcleo del backend ejecutará de forma automatizada un proceso programado (Cron Job / Tarea Celery) exactamente a las 00:00:00 horas de cada día. Este motor evalúa la tabla de membresías y actualiza de manera masiva el estado de pago a 'vencido' para todo usuario cuya fecha de vencimiento sea estrictamente menor a la fecha actual. Esta mutación de estado desencadena instantáneamente el bloqueo en el módulo de control de accesos de la recepción, inyectando la alerta visual Carmesí en la interfaz de pantalla.
2.5: Motor de Período de Gracia (5 Días Autónomos): El sistema elimina la posibilidad de pagos parciales o saldos deudores; los planes se pagan al 100% o no se procesan. Sin embargo, al expirar la membresía, el backend activa automáticamente un "Período de Gracia" de 5 días calendario. Durante estos 5 días, el estatus visual del atleta pasa a ser "en_gracia" (permitiendo el acceso a la recepción pero emitiendo una advertencia). A las 00:00:00 del sexto día, si no hay un pago registrado, el sistema bloquea el acceso mutando el estatus a "vencido".
2.7: Escalabilidad del Portal del Atleta (Post-MVP): Se descartan las integraciones con mensajería externa (Meta API). La arquitectura queda preparada para que, en fases posteriores, los clientes se autentiquen en su propio portal web/móvil para consultar dietas, rutinas, historial de medidas y pasarela de pago directa.
2.6: Resiliencia de Recepción ante Fallas de Conectividad (Modo Offline Local): Debido a las fluctuaciones de conectividad e infraestructura eléctrica comunes en Maracaibo, el módulo de recepción no puede quedar inoperativo si se cae el acceso a internet. El frontend debe cachear localmente en el navegador un snapshot optimizado (ID, Cédula, Nombre, Estatus) de los miembros activos. Las asistencias marcadas en estado de desconexión se guardarán en una cola local indexada y se sincronizarán mediante peticiones masivas (batch operations) de forma transparente en el momento en que se restablezca el puente con la API de FastAPI.
3. Arquitectura de Software y Stack Tecnológico Backend (Python)
En lugar de arquitecturas basadas en TypeScript, se adopta un stack de alto rendimiento fundamentado en el ecosistema científico y corporativo de Python. Esto permite acelerar los tiempos de cómputo, garantizar tipado estricto en el backend y facilitar un despliegue limpio.
🧠 Capa del Backend (El Cerebro Lógico)
Lenguaje: Python
Framework: FastAPI
Justificación: Python permite un manejo de datos limpio y estructurado. Se selecciona FastAPI sobre otras alternativas (como Django o Flask) debido a su ejecución asíncrona nativa, su velocidad de procesamiento equiparable a Node.js y su validación automática de datos mediante esquemas de Pydantic. Además, genera documentación interactiva automática (Swagger UI), lo que agiliza las pruebas de endpoints.
🎨 Capa del Frontend (La Interfaz de Usuario)
Lenguajes Base: HTML5, CSS3 y JavaScript (TypeScript)
Framework de Componentes: React / Next.js (App Router)
Framework de Estilos: Tailwind CSS
Justificación: El uso de HTML, JS y Tailwind CSS garantiza una interfaz fluida, interactiva y de baja carga cognitiva para el usuario. Next.js proporciona la estructura de enrutamiento necesaria para gestionar las 6 pantallas del MVP de forma óptima, mientras que Tailwind CSS permite compilar estilos utilitarios directos, reduciendo el tamaño del código y asegurando que el "Semáforo Visual" de la recepción cambie de estado instantáneamente sin retrasos en el renderizado.
🗄️ Capa de Persistencia (Base de Datos)
Motor: PostgreSQL
Justificación: Al procesar información transaccional crítica (pagos únicos, vencimientos estrictos y asistencias), se requiere un motor de base de datos relacional robusto que garantice el cumplimiento de las propiedades ACID. PostgreSQL ofrece soporte óptimo para índices B-Tree, permitiendo resolver la búsqueda por cédula en microsegundos.
3.1. Código de Producción: Esquemas de Validación con Pydantic
A continuación se documentan los esquemas de validación estructurales que garantizan que las reglas de negocio de GymFlow Analytics se ejecuten de manera inquebrantable:
from pydantic import BaseModel, Field, EmailStrfrom typing import Optionalfrom decimal import Decimalfrom datetime import datetime, datefrom enum import Enumclass RoleEnum(str, Enum):    admin = "admin"    worker = "worker"    client = "client"class PaymentMethodEnum(str, Enum):    pago_movil = "pago_movil"    transferencia = "transferencia"    efectivo_usd = "efectivo_usd"    efectivo_bs = "efectivo_bs"# Esquema de Control de Usuarios con Borrado Lógicoclass UserSchema(BaseModel):    id: Optional[int] = None    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre completo")    correo: EmailStr    rol: RoleEnum = RoleEnum.client    estado_logico: bool = Field(True, description="True = Activo, False = Eliminado Lógicamente")# Esquema Transaccional Multidivisa Normalizadoclass TransactionSchema(BaseModel):    id: Optional[int] = None    membership_id: int    registrado_por: int  # ID del Trabajador o Admin    monto_usd: Decimal = Field(..., gt=0, decimal_places=2, description="Monto guardado estrictamente en USD")    metodo_pago: PaymentMethodEnum    fecha_pago: datetime = Field(default_factory=datetime.utcnow)    class Config:        from_attributes = True
4. Requerimientos del Sistema
4.1. Requerimientos Funcionales (RF)
ID
Requerimiento
Descripción Detallada y Regla Asociada
RF-1
Autenticación y RBAC
Control de acceso diferenciado mediante tokens JWT para Administradores, Trabajadores y Clientes. Bloqueo de rutas de configuración según el rol asignado.
RF-2
Gestión de Planes de Membresía
Configuración dinámica de planes definiendo el costo de inscripción, tarifa base y ciclos parametrizables (semanal, quincenal, mensual, anual).
RF-3
Registro Transaccional Multidivisa
Módulo de captura de pagos con conversión forzada a dólares basada en la tasa ingresada, método de pago e impresión de recibo digital en PDF.
RF-4
Motor Automatizado de Alertas
Script diario síncrono/asíncrono que evalúa vigencias, muta el estatus a 'vencido' y envía señales inmediatas al frontend de la recepción.
RF-5
Flujo de Caja Integral
Consolidación en tiempo real de ingresos y egresos operativos, generando reportes analíticos de balances netos visibles únicamente por el Administrador.

  RF-6: Motor de Sincronización de Cola de Asistencia Local: El sistema debe rastrear el estado de la conexión de red (online/offline). En modo offline, debe permitir la lectura del caché y almacenar los check-ins locales con fecha y hora exacta del dispositivo físico.
  RF-7: Módulo de Gestión y Amortización de Deudas: La interfaz administrativa debe proveer un reporte de cuentas por cobrar, listando atletas con saldos pendientes y permitiendo la imputación directa de pagos específicos para liquidar deudas acumuladas.

4.2. Requerimientos No Funcionales (RNF)
Seguridad Estructural Avanzada: Cifrado irreversible de contraseñas mediante hash bcrypt. Control estricto del tiempo de expiración de sesiones JWT (máximo 8 horas) para evitar secuestro de sesiones en computadores compartidos de recepción.
Rendimiento de Alta Concurrencia y Latencia Crítica: La búsqueda indexada de miembros en la recepción mediante número de Cédula o ID debe responder en un tiempo estrictamente inferior a 1.5 segundos, soportando ráfagas en horas pico.
Disponibilidad Diferenciada y Diseño Adaptativo: El módulo de control de accesos de la recepción adopta un diseño optimizado para monitores de escritorio (Desktop-First) para agilizar el One-Click Check-in. El Dashboard Administrativo cuenta con un diseño 100% responsivo (Mobile-Friendly) para supervisión móvil remota por parte del dueño.
5. Diseño del Sistema de Experiencia de Usuario (UX/UI)
Para garantizar que el sistema reemplace eficientemente al cuaderno físico sin generar fricción, la interfaz se rige por un esquema cromático intuitivo basado en estados operativos inmediatos (Sistema de Semáforo Visual):
Estatus Operativo
Lógica Visual / Clases Tailwind
Significado y Acción en Puerta
Activo
text-emerald-600 / bg-emerald-50
Solvencia confirmada. Membresía al día. Acceso totalmente permitido con un solo clic.
Por Vencer
text-amber-500 / bg-amber-50
Alerta preventiva en pantalla. Indica los últimos 3 días de vigencia del plan actual. Permite el acceso pero advierte de la renovación.
Vencido
text-rose-600 / bg-rose-50
Bloqueo automático del puente de acceso. Alerta visual Carmesí prominente en pantalla. Requiere pago y renovación inmediata.

6. Definición Estratégica de MVP por Fases del Proyecto
Para mitigar riesgos técnicos y asegurar entregas incrementales completamente funcionales para la tesis, el desarrollo de GymFlow Analytics se divide en tres fases estratégicas. Cada una cuenta con su propio MVP (Producto Mínimo Viable) atómico y autónomo:
ASE 1: Arquitectura y Persistencia de Datos (Capa de Base de Datos)
Objetivo: Establecer el almacén de datos relacional garantizando integridad referencial, velocidad de indexación y persistencia de históricos operativos.
1.1. Modelado en Tercera Forma Normal (3FN):
Diseño y despliegue del esquema en PostgreSQL.
Creación de las tablas base con restricciones (CONSTRAINTS) de no-negatividad en campos financieros:
usuarios (Credenciales del personal, contraseñas cifradas).
miembros (Datos maestros de los atletas).
planes (Definición de tarifas fijas y duraciones).
membresias_miembros (Relación transaccional de vigencia).
pagos (Auditoría de ingresos monetarios).
asistencias (Bitácora de accesos físicos).
1.2. Optimización de Consultas en Recepción:
Creación del índice B-Tree indexado: CREATE INDEX idx_miembros_cedula ON miembros(cedula) WHERE estado_logico = TRUE;. Objetivo: Mitigar la latencia de búsqueda por ID a menos de 50ms en la base de datos.
1.3. Implementación de la Capa de Borrado Lógico:
Inyección obligatoria de la columna estado_logico (Boolean, default TRUE) en las tablas miembros y usuarios.
Configuración de consultas adaptadas para omitir registros con banderas en FALSE, preservando el histórico financiero en cascada.
🧠 FASE 2: Cerebro Lógico y Reglas de Negocio (Capa de Backend API con FastAPI)
Objetivo: Construir los endpoints RESTful, asegurar el control de accesos mediante roles e implementar los motores matemáticos de control financiero y de estados.
2.1. Seguridad, Autenticación y RBAC:
Implementación de hashing de contraseñas mediante bcrypt.
Despliegue del flujo de autenticación basado en tokens JWT (JSON Web Tokens) con tiempo de expiración paramétrico.
Configuración de decoradores de seguridad basados en roles (RBAC): restricción de rutas críticas (Métricas y Finanzas) exclusivamente para el rol admin.
2.2. Motor Automático del Período de Gracia (Regla 2.5):
Desarrollo del algoritmo de evaluación cronológica en el endpoint de consulta del miembro:
Condición Activo: Si fecha_vencimiento >= fecha_actual $\rightarrow$ Estado: activo.
Condición Gracia: Si fecha_actual $>$ fecha_vencimiento Y dias_transcurridos <= 5 $\rightarrow$ Estado: en_gracia (Retorna entero dias_restantes).
Condición Vencido: Si dias_transcurridos >= 6 $\rightarrow$ Estado: vencido (Bloqueo inmediato).
2.3. Endpoint de Caja y Normalización Multidivisa:
Desarrollo de la ruta /api/v1/payments/register bajo esquema estricto de Pydantic.
Lógica de conversión: Evaluación del payload. Si la moneda es VES, divide el monto entre la tasa_cambio provista y formatea el resultado usando el tipo NUMERIC(10,2) en Postgres para truncar y evitar errores de redondeo de punto flotante. El pago debe registrarse por el 100% de la tarifa del plan; no se computan saldos pendientes.
🎨 FASE 3: Interfaz de Baja Carga Cognitiva (Capa de Frontend con Next.js)
Objetivo: Desarrollar una interfaz de usuario limpia, intuitiva y fluida que elimine el uso de bitácoras físicas y distribuya las responsabilidades operativas según el rol del usuario.
3.1. Arquitectura de Layout y Elementos Globales:
Diseño del Sidebar Lateral fijo (bg-indigo-900) con enrutamiento dinámico y control de visualización adaptativa según el rol inyectado por el JWT.
Diseño del Navbar Superior con widget integrado del estado de red (window.navigator.onLine) para control visual de contingencia eléctrica/conectividad.
3.2. Implementación de las Seis (6) Vistas Obligatorias:
src/app/login/page.tsx: Formulario de acceso limpio con manejo de excepciones de credenciales inválidas.
src/app/dashboard/reception/page.tsx: Barra de búsqueda de cédula sobredimensionada vinculada al evento onSubmit. Tarjeta dinámica mapeada con el Semáforo UI de 3 Estados (Verde para activo, Ámbar con animación pulse para en_gracia, Rojo sólido para vencido).
src/app/members/list/page.tsx: Tabla de control de atletas. Implementa el efecto visual de borrado lógico (opacidad reducida al 40% y deshabilitación de eventos en fila tras confirmar baja).
src/app/members/register/page.tsx: Formulario limpio de captura de datos maestros para primeras inscripciones.
src/app/payments/register/page.tsx: Formulario de caja simplificado con un panel estático bg-slate-100 que renderiza en tiempo real el cálculo calculado del monto_usd normalizado antes de enviar el formulario.
src/app/dashboard/admin/page.tsx: Vista optimizada para móviles que expone tarjetas KPI rápidas (Ingresos Netos del Mes, Atletas Activos, Alertas) y una lista ordenada del flujo de caja.
⚡ FASE 4: Resiliencia Offline, Sincronización Local y Pruebas de Calidad (QA)
Objetivo: Dotar a la aplicación de tolerancia a fallas críticas de conectividad eléctrica o de red y asegurar que los criterios de aceptación técnicos se cumplan al 100%.
4.1. Configuración de Base de Datos Local (IndexedDB):
Implementación de almacenamiento local en el navegador del cliente mediante la creación de dos almacenes: members_cache (catálogo local optimizado para lecturas offline en recepción) y offline_checkins_queue (cola de registros acumulados durante la desconexión).
4.2. Motor de Sincronización Asíncrona (Flush Engine):
Programación del listener de eventos de red del navegador. Al detectar la transición de offline a online, se bloquea temporalmente la interfaz de recepción para leer la cola de IndexedDB, empaquetar los registros en un arreglo JSON unificado y despacharlos mediante una operación en lote (batch operation) al endpoint del backend. Al recibir 200 OK, se purga la cola local.
4.3. Protocolo de Pruebas y Aseguramiento de Calidad (QA):
Prueba de Latencia: Simulación en entorno local con una carga masiva simulada de 5,000 registros de miembros para certificar que la búsqueda en la UI de recepción se ejecute en menos de 1.5 segundos.
Prueba de Stress Offline: Desconexión forzada de la red en la vista de recepción, registro secuencial de múltiples check-ins, reconexión y auditoría del log en PostgreSQL para certificar la consistencia del campo de fecha y hora original capturado en el cliente.
Prueba de Regresión de Roles: Intentos de consumo forzado de rutas administrativas utilizando tokens JWT con rol worker para verificar el bloqueo sistemático con error 403 Forbidden.
