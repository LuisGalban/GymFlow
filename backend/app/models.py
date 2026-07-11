import enum
from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy import (
    Column, Integer, String, Boolean, Numeric, Date, DateTime, ForeignKey, Index, BigInteger, text, CheckConstraint, UniqueConstraint
)
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from .database import Base

# Enums
class UserRole(str, enum.Enum):
    admin = "admin"
    worker = "worker"

class PaymentCurrency(str, enum.Enum):
    USD = "USD"
    VES = "VES"

class PaymentMethod(str, enum.Enum):
    pago_movil = "pago_movil"
    transferencia = "transferencia"
    efectivo_usd = "efectivo_usd"
    efectivo_bs = "efectivo_bs"
    zelle = "zelle"
    binance = "binance"

class MembershipStatus(str, enum.Enum):
    activo = "activo"
    por_vencer = "por_vencer"
    vencido = "vencido"


class GymSubscriptionStatus(str, enum.Enum):
    activo = "activo"
    pausado = "pausado"
    suspendido = "suspendido"


class Gym(Base):
    __tablename__ = "gyms"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    direccion = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    dias_gracia_default = Column(Integer, default=5, nullable=False)
    moneda_base = Column(String(10), default=PaymentCurrency.USD, nullable=False)
    fecha_alta = Column(DateTime, default=datetime.utcnow, nullable=False)
    estado_suscripcion = Column(String(20), default=GymSubscriptionStatus.activo, nullable=False)
    estado_logico = Column(Boolean, default=True, nullable=False)

    # Relaciones inversas (backrefs)
    usuarios = relationship("Usuario", back_populates="gym")
    miembros = relationship("Miembro", back_populates="gym")
    planes = relationship("Plan", back_populates="gym")
    pagos = relationship("Pago", back_populates="gym")
    asistencias = relationship("Asistencia", back_populates="gym")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id", ondelete="RESTRICT"), nullable=False)
    cedula = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), default=UserRole.worker, nullable=False)
    estado_logico = Column(Boolean, default=True, nullable=False)

    # Relaciones
    gym = relationship("Gym", back_populates="usuarios")
    pagos_registrados = relationship("Pago", back_populates="registrador")


class Miembro(Base):
    __tablename__ = "miembros"

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id", ondelete="RESTRICT"), nullable=False)
    cedula = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    estado_logico = Column(Boolean, default=True, nullable=False)

    # Relaciones
    gym = relationship("Gym", back_populates="miembros")
    membresias = relationship("MembresiaMiembro", back_populates="miembro")
    asistencias = relationship("Asistencia", back_populates="miembro", cascade="all, delete-orphan")


class Plan(Base):
    __tablename__ = "planes"
    __table_args__ = (
        CheckConstraint('precio_usd >= 0', name='ck_plan_precio_usd_no_negativo'),
        UniqueConstraint('nombre', 'gym_id', name='uq_plan_nombre_gym'),
    )

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id", ondelete="RESTRICT"), nullable=False)
    nombre = Column(String(50), nullable=False)
    duracion_dias = Column(Integer, nullable=False)
    precio_usd = Column(Numeric(10, 2), nullable=False)
    estado_logico = Column(Boolean, default=True, nullable=False)

    # Relaciones
    gym = relationship("Gym", back_populates="planes")
    membresias = relationship("MembresiaMiembro", back_populates="plan")


class MembresiaMiembro(Base):
    __tablename__ = "membresias_miembros"

    id = Column(Integer, primary_key=True, index=True)
    miembro_id = Column(Integer, ForeignKey("miembros.id", ondelete="RESTRICT"), nullable=False)
    plan_id = Column(Integer, ForeignKey("planes.id", ondelete="RESTRICT"), nullable=False)
    fecha_inicio = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    fecha_vencimiento = Column(Date, nullable=False)
    estatus_pago = Column(String(20), default=MembershipStatus.vencido, nullable=False)

    # Relaciones
    miembro = relationship("Miembro", back_populates="membresias")
    plan = relationship("Plan", back_populates="membresias")
    pagos = relationship("Pago", back_populates="membresia_miembro")


class Pago(Base):
    __tablename__ = "pagos"
    __table_args__ = (
        CheckConstraint('monto_original > 0', name='ck_pago_monto_original_positivo'),
        CheckConstraint('tasa_cambio > 0', name='ck_pago_tasa_cambio_positivo'),
    )

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id", ondelete="RESTRICT"), nullable=False)
    membresia_miembro_id = Column(Integer, ForeignKey("membresias_miembros.id", ondelete="RESTRICT"), nullable=False)
    registrado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    monto_original = Column(Numeric(12, 2), nullable=False)
    moneda = Column(String(10), nullable=False)
    tasa_cambio = Column(Numeric(10, 4), nullable=False)
    monto_usd = Column(Numeric(10, 2), nullable=False)  # Normalizado: monto_original / tasa_cambio
    metodo_pago = Column(String(30), nullable=False)
    referencia = Column(String(50), nullable=True)
    fecha_pago = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    gym = relationship("Gym", back_populates="pagos")
    membresia_miembro = relationship("MembresiaMiembro", back_populates="pagos")
    registrador = relationship("Usuario", back_populates="pagos_registrados")


class Asistencia(Base):
    __tablename__ = "asistencias"

    id = Column(BigInteger, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id", ondelete="RESTRICT"), nullable=False)
    miembro_id = Column(Integer, ForeignKey("miembros.id", ondelete="CASCADE"), nullable=False)
    fecha_entrada = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    gym = relationship("Gym", back_populates="asistencias")
    miembro = relationship("Miembro", back_populates="asistencias")


# Índices de optimización de Base de Datos
# B-Tree index para búsquedas por cédula para registros activos
Index("idx_miembros_cedula_activa", Miembro.cedula, postgresql_where=(Miembro.estado_logico == True))

# Índice para optimizar búsquedas diarias por fecha de vencimiento y estado
Index("idx_membresias_vencimiento_status", MembresiaMiembro.fecha_vencimiento, MembresiaMiembro.estatus_pago)

# Índice para reportes de asistencias en horas pico
Index("idx_asistencias_fecha_entrada", Asistencia.fecha_entrada)
