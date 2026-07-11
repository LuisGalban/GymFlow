from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date
from enum import Enum

# Reutilizamos los Enums definidos en los modelos
class RoleEnum(str, Enum):
    admin = "admin"
    worker = "worker"
    super_admin = "super_admin"

class PaymentCurrencyEnum(str, Enum):
    USD = "USD"
    VES = "VES"

class PaymentMethodEnum(str, Enum):
    pago_movil = "pago_movil"
    transferencia = "transferencia"
    efectivo_usd = "efectivo_usd"
    efectivo_bs = "efectivo_bs"
    zelle = "zelle"
    binance = "binance"

class MembershipStatusEnum(str, Enum):
    activo = "activo"
    por_vencer = "por_vencer"
    vencido = "vencido"


# --- ESQUEMAS DE USUARIO (Personal) ---
class UserBase(BaseModel):
    cedula: str = Field(..., max_length=20, description="Cédula de identidad")
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre completo")
    correo: EmailStr
    rol: RoleEnum = RoleEnum.worker

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña en texto plano")

class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    rol: Optional[RoleEnum] = None
    password: Optional[str] = None
    estado_logico: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    estado_logico: bool

    class Config:
        from_attributes = True


# --- ESQUEMAS DE AUTENTICACIÓN ---
class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    gym_id: int

class TokenData(BaseModel):
    correo: Optional[str] = None
    rol: Optional[str] = None
    gym_id: Optional[int] = None


# --- ESQUEMAS DE PLANES ---
class PlanBase(BaseModel):
    nombre: str = Field(..., max_length=50)
    duracion_dias: int = Field(..., gt=0)
    precio_usd: Decimal = Field(..., ge=0, decimal_places=2)

class PlanCreate(PlanBase):
    pass

class PlanResponse(PlanBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={Decimal: lambda v: float(v)}
    )
    id: int
    estado_logico: bool


# --- ESQUEMAS DE MIEMBROS ---
class MiembroBase(BaseModel):
    cedula: str = Field(..., max_length=20)
    nombre: str = Field(..., min_length=3, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)

class MiembroCreate(MiembroBase):
    plan_id: int = Field(..., description="ID del plan seleccionado inicialmente")

class MiembroResponse(MiembroBase):
    id: int
    estado_logico: bool
    estatus_actual: Optional[str] = None  # Calculado dinámicamente: activo, en_gracia, vencido
    plan_nombre: Optional[str] = None  # Nombre del plan asociado
    plan_id: Optional[int] = None  # ID del plan asociado

    class Config:
        from_attributes = True


# --- ESQUEMAS DE MEMBRESÍAS ---
class MembresiaBase(BaseModel):
    miembro_id: int
    plan_id: int
    fecha_inicio: date

class MembresiaCreate(MembresiaBase):
    pass

class MembresiaResponse(MembresiaBase):
    id: int
    fecha_vencimiento: date
    estatus_pago: str

    class Config:
        from_attributes = True


# --- ESQUEMAS DE PAGOS ---
class PagoCreate(BaseModel):
    membresia_miembro_id: int
    monto_original: Decimal = Field(..., gt=0, decimal_places=2)
    moneda: PaymentCurrencyEnum
    tasa_cambio: Optional[Decimal] = Field(None, description="Tasa de cambio (requerida si la moneda es VES)")
    metodo_pago: PaymentMethodEnum
    referencia: Optional[str] = Field(None, max_length=50, description="Referencia de pago")
    observaciones: Optional[str] = Field(None, max_length=255)

class PagoCedulaCreate(BaseModel):
    cedula: str = Field(..., max_length=20, description="Cédula del miembro")
    planSeleccionado_id: int = Field(..., description="ID del plan que se está pagando")
    monto_original: Decimal = Field(..., gt=0, decimal_places=2)
    moneda: PaymentCurrencyEnum = Field(default=PaymentCurrencyEnum.USD, description="Moneda del pago (USD por defecto)")
    tasa_cambio: Optional[Decimal] = Field(None, description="Tasa de cambio (requerida si la moneda es VES)")
    metodo_pago: PaymentMethodEnum = Field(default=PaymentMethodEnum.pago_movil, description="Método de pago (pago_movil por defecto)")
    referencia: Optional[str] = Field(None, max_length=50, description="Referencia de pago")

class PagoResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={Decimal: lambda v: float(v)}
    )
    id: int
    membresia_miembro_id: int
    registrado_por: int
    monto_original: Decimal
    moneda: PaymentCurrencyEnum
    tasa_cambio: Decimal
    monto_usd: Decimal
    metodo_pago: PaymentMethodEnum
    referencia: Optional[str] = None
    observaciones: Optional[str] = None
    fecha_pago: datetime


class PagoDetalleResponse(PagoResponse):
    miembro_nombre: str
    miembro_cedula: str
    plan_nombre: str
    registrador_nombre: str


# --- ESQUEMAS DE ASISTENCIAS ---
class AsistenciaCreate(BaseModel):
    miembro_id: int

class AsistenciaResponse(BaseModel):
    id: int
    miembro_id: int
    fecha_entrada: datetime

    class Config:
        from_attributes = True


# --- ESQUEMAS DE KPIS Y REPORTES ---
class KpiSummary(BaseModel):
    model_config = ConfigDict(
        json_encoders={Decimal: lambda v: float(v)}
    )
    ingresos_netos_usd: Decimal
    atletas_activos: int
    alertas_vencidos: int

class CashFlowReport(BaseModel):
    model_config = ConfigDict(
        json_encoders={Decimal: lambda v: float(v)}
    )
    pagos: List[PagoResponse]
    ingresos_totales_usd: Decimal


# --- ESQUEMAS DE SUPER ADMIN ---
class SuperAdminGymCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    direccion: str = Field(..., min_length=2, max_length=255)

class SuperAdminGymResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    direccion: str
    telefono: Optional[str] = None
    estado_suscripcion: str
    token_sede: Optional[str] = None
    estado_logico: bool
    miembros_activos: int = 0
    ingresos_mensuales_usd: float = 0.0

class SuscripcionUpdate(BaseModel):
    estado_suscripcion: str = Field(..., pattern="^(activo|pausado|suspendido)$")

class RegisterGymAdminRequest(BaseModel):
    token_sede: str
    nombre: str = Field(..., min_length=3, max_length=100)
    correo: EmailStr
    password: str = Field(..., min_length=6)
