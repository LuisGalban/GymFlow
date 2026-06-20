🗺️ 1. Estructura del Diagrama Entidad-Relación (ERD)
El sistema se compone de 5 entidades principales interconectadas de manera limpia:
usuarios (1) ---- (N) pagos: Para saber qué trabajador o administrador registró cada flujo de dinero (Auditoría).
miembros (1) ---- (N) membresias_miembros: Un miembro puede tener un histórico de muchas membresías a lo largo del tiempo (pero solo una activa a la vez).
planes (1) ---- (N) membresias_miembros: Un plan (ej: "Mensual VIP") puede ser asignado a muchos miembros.
membresias_miembros (1) ---- (N) pagos: Un registro de membresía puede requerir uno o varios pagos (en caso de abonos o cuotas).
miembros (1) ---- (N) asistencias: Registro histórico de cada vez que el cliente hace Check-in en la recepción.
📖 2. Diccionario de Datos Técnico
Tabla: usuarios (Personal del Gimnasio)
Guarda las credenciales del personal con seguridad criptográfica y asignación de roles para el control de acceso (RBAC).
id (SERIAL, PRIMARY KEY): Identificador único del usuario.
nombre (VARCHAR(100), NOT NULL): Nombre completo del trabajador o administrador.
correo (VARCHAR(150), UNIQUE, NOT NULL): Correo electrónico (utilizado para el login).
password_hash (VARCHAR(255), NOT NULL): Contraseña cifrada con algoritmo bcrypt.
rol (VARCHAR(20), NOT NULL): Restringido por software a valores: 'admin', 'worker'.
estado_logico (BOOLEAN, DEFAULT TRUE): Bandera de borrado lógico (true = activo, false = deshabilitado).
Tabla: miembros (Clientes del Gimnasio)
Almacena la información de los atletas. Cuenta con un índice optimizado en la cédula para búsquedas en recepción en menos de 1.5 segundos.
id (SERIAL, PRIMARY KEY): Identificador único interno.
cedula (VARCHAR(20), UNIQUE, NOT NULL): Documento de identidad (clave de búsqueda rápida).
nombre (VARCHAR(100), NOT NULL): Nombre completo del cliente.
telefono (VARCHAR(20), NULL): Número de contacto.
estado_logico (BOOLEAN, DEFAULT TRUE): Bandera de borrado lógico.
Tabla: planes (Configuración Estratégica)
Catálogo de los servicios y tarifas que ofrece el gimnasio, modificable únicamente por el Administrador.
id (SERIAL, PRIMARY KEY): Identificador del plan.
nombre (VARCHAR(50), NOT NULL): Ej: "Mensualidad", "Inscripción", "Semana", "Anualidad".
duracion_dias (INTEGER, NOT NULL): Cantidad de días que otorga el plan (ej: 30 para el mes).
precio_usd (NUMERIC(10,2), NOT NULL): Precio base internacional normalizado en dólares.
estado_logico (BOOLEAN, DEFAULT TRUE): Bandera de borrado lógico.
Tabla: membresias_miembros (El Corazón Operativo)
Es la tabla intermedia que asocia un cliente con un plan. Aquí es donde el Cron Job diario evalúa el estado del semáforo.
id (SERIAL, PRIMARY KEY): Identificador único de la membresía contratada.
miembro_id (INTEGER, FOREIGN KEY REFERENCES miembros(id)): Cliente asociado.
plan_id (INTEGER, FOREIGN KEY REFERENCES planes(id)): Plan adquirido.
fecha_inicio (DATE, NOT NULL): Fecha en la que inicia la vigencia.
fecha_vencimiento (DATE, NOT NULL): Calculada automáticamente en el backend sumando los duracion_dias del plan.
estatus_pago (VARCHAR(20), DEFAULT 'vencido'): Estado del semáforo: 'activo', 'por_vencer', 'vencido'.
Tabla: pagos (Control de Caja Multidivisa)
Registra las transacciones financieras. Almacena obligatoriamente la conversión limpia a dólares para evitar distorsiones inflacionarias.
id (SERIAL, PRIMARY KEY): Identificador único de la transacción.
membresia_miembro_id (INTEGER, FOREIGN KEY REFERENCES membresias_miembros(id)): La membresía que se está pagando.
registrado_por (INTEGER, FOREIGN KEY REFERENCES usuarios(id)): El empleado que recibió el dinero.
monto_original (NUMERIC(12,2), NOT NULL): El monto exacto que entregó el cliente (ej: 1400.00).
moneda (VARCHAR(10), NOT NULL): La divisa física utilizada: 'USD', 'VES' (Bolívares).
tasa_cambio (NUMERIC(10,4), NOT NULL): La tasa oficial en el segundo exacto de la transacción (ej: 36.50). Si se pagó en USD, este valor es 1.0000.
monto_usd (NUMERIC(10,2), NOT NULL): Campo crítico normalizado. Calculado matemáticamente como monto_original / tasa_cambio. Es el valor real auditable para el Dashboard Administrativo.
metodo_pago (VARCHAR(30), NOT NULL): 'pago_movil', 'transferencia', 'efectivo_usd', 'efectivo_bs'.
fecha_pago (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Fecha y hora exacta con zona horaria del servidor.
Tabla: asistencias (Módulo de Recepción)
Registra las entradas físicas diarias mediante el One-Click Check-in.
id (BIGSERIAL, PRIMARY KEY): Identificador único.
miembro_id (INTEGER, FOREIGN KEY REFERENCES miembros(id)): Quién ingresó.
fecha_entrada (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Estampa de tiempo exacta de la entrada.
💻 3. Script SQL de Producción (PostgreSQL)
Este script incluye restricciones de integridad (CHECK), claves foráneas en cascada controlada e índices de rendimiento de base de datos senior:
-- 1. Crear ENUMs para limitar errores de inserción por strings inválidos
CREATE TYPE user_role AS ENUM ('admin', 'worker');
CREATE TYPE payment_currency AS ENUM ('USD', 'VES');
CREATE TYPE payment_method AS ENUM ('pago_movil', 'transferencia', 'efectivo_usd', 'efectivo_bs');
CREATE TYPE membership_status AS ENUM ('activo', 'por_vencer', 'vencido');

-- 2. Tabla de Usuarios (Personal)
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol user_role NOT NULL DEFAULT 'worker',
    estado_logico BOOLEAN NOT NULL DEFAULT TRUE
);

-- 3. Tabla de Miembros (Clientes)
CREATE TABLE miembros (
    id SERIAL PRIMARY KEY,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    estado_logico BOOLEAN NOT NULL DEFAULT TRUE
);

-- OPTIMIZACIÓN SENIOR: Índice B-Tree para búsquedas One-Click en recepción por Cédula (< 1.5s)
CREATE INDEX idx_miembros_cedula ON miembros(cedula) WHERE estado_logico = TRUE;

-- 4. Tabla de Planes
CREATE TABLE planes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    duracion_dias INTEGER NOT NULL CHECK (duracion_dias > 0),
    precio_usd NUMERIC(10, 2) NOT NULL CHECK (precio_usd >= 0),
    estado_logico BOOLEAN NOT NULL DEFAULT TRUE
);

-- 5. Tabla de Membresías de Miembros (Asignaciones de planes)
CREATE TABLE membresias_miembros (
    id SERIAL PRIMARY KEY,
    miembro_id INTEGER NOT NULL REFERENCES miembros(id) ON DELETE RESTRICT,
    plan_id INTEGER NOT NULL REFERENCES planes(id) ON DELETE RESTRICT,
    fecha_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE NOT NULL,
    estatus_pago membership_status NOT NULL DEFAULT 'vencido',
    CONSTRAINT chk_fechas CHECK (fecha_vencimiento >= fecha_inicio)
);

-- Índices para optimizar el Cron Job diario que corre a las 00:00
CREATE INDEX idx_membresias_vencimiento ON membresias_miembros(fecha_vencimiento, estatus_pago);

-- 6. Tabla de Pagos (Auditoría Financiera)
CREATE TABLE pagos (
    id SERIAL PRIMARY KEY,
    membresia_miembro_id INTEGER NOT NULL REFERENCES membresias_miembros(id) ON DELETE RESTRICT,
    registrado_por INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    monto_original NUMERIC(12, 2) NOT NULL CHECK (monto_original > 0),
    moneda payment_currency NOT NULL,
    tasa_cambio NUMERIC(10, 4) NOT NULL CHECK (tasa_cambio > 0),
    monto_usd NUMERIC(10, 2) NOT NULL CHECK (monto_usd > 0),
    metodo_pago payment_method NOT NULL,
    fecha_pago TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7. Tabla de Asistencias (Check-in)
CREATE TABLE asistencias (
    id BIGSERIAL PRIMARY KEY,
    miembro_id INTEGER NOT NULL REFERENCES miembros(id) ON DELETE CASCADE,
    fecha_entrada TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índice para acelerar los reportes de flujo de asistencia en las horas pico
CREATE INDEX idx_asistencias_fecha ON asistencias(fecha_entrada);