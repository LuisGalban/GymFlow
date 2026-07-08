import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.database import engine, Base, get_db
from app.models import Usuario, Miembro, Plan, MembresiaMiembro, Pago, Asistencia, UserRole, PaymentCurrency, PaymentMethod, MembershipStatus
from app.schemas import (
    UserCreate, UserUpdate, UserResponse, LoginRequest, Token,
    MiembroCreate, MiembroResponse, PlanCreate, PlanResponse,
    MembresiaCreate, MembresiaResponse, PagoCreate, PagoCedulaCreate, PagoResponse, PaymentCurrencyEnum, PaymentMethodEnum, AsistenciaCreate, AsistenciaResponse, KpiSummary, CashFlowReport
)
from app.auth.auth import (
    obtener_password_hash, verificar_password, crear_token_acceso,
    obtener_usuario_actual, requerir_admin, requerir_trabajador
)

app = FastAPI(
    title="GymFlow Analytics API",
    description="Backend de producción para la gestión y analítica de gimnasios",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper para calcular estados dinámicos del Semáforo ---
def calcular_estado_miembro(membresia: Optional[MembresiaMiembro]) -> tuple[str, Optional[int]]:
    if not membresia:
        return "vencido", None
    
    hoy = date.today()
    if membresia.estatus_pago == "vencido":
        return "vencido", None
        
    if membresia.fecha_vencimiento >= hoy:
        # Faltan 3 días o menos para vencer (Por Vencer - Ámbar)
        dias_restantes = (membresia.fecha_vencimiento - hoy).days
        if dias_restantes <= 3:
            return "por_vencer", None
        return "activo", None
    else:
        # Período de gracia (5 días)
        dias_transcurridos = (hoy - membresia.fecha_vencimiento).days
        if dias_transcurridos <= 5:
            dias_restantes_gracia = 5 - dias_transcurridos
            return "en_gracia", dias_restantes_gracia
        else:
            return "vencido", None

# --- RUTA DE INICIO / MONITOREO DE SALUD ---
@app.get("/")
def read_root():
    return {"status": "ok", "app": "GymFlow Analytics API", "version": "1.0.0"}

# --- ENDPOINTS DE AUTENTICACIÓN ---
@app.post("/api/v1/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo == payload.correo, Usuario.estado_logico == True).first()
    if not usuario or not verificar_password(payload.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = crear_token_acceso(data={"sub": usuario.correo, "rol": usuario.rol})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/auth/me", response_model=UserResponse)
def get_me(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual

# --- ENDPOINTS DE USUARIOS (Solo Admin) ---
@app.post("/api/v1/users/register", response_model=UserResponse, dependencies=[Depends(requerir_admin)])
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el correo ya existe
    existe_correo = db.query(Usuario).filter(Usuario.correo == payload.correo).first()
    if existe_correo:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # Verificar si la cédula ya existe
    existe_cedula = db.query(Usuario).filter(Usuario.cedula == payload.cedula).first()
    if existe_cedula:
        raise HTTPException(status_code=400, detail="La cédula ya está registrada")
        
    nuevo_usuario = Usuario(
        cedula=payload.cedula,
        nombre=payload.nombre,
        correo=payload.correo,
        password_hash=obtener_password_hash(payload.password),
        rol=payload.rol.value,
        estado_logico=True
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.get("/api/v1/users", response_model=List[UserResponse], dependencies=[Depends(requerir_admin)])
def list_users(db: Session = Depends(get_db)):
    return db.query(Usuario).filter(Usuario.estado_logico == True).order_by(Usuario.id).all()

@app.get("/api/v1/users/{id}", response_model=UserResponse, dependencies=[Depends(requerir_admin)])
def get_user(id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id, Usuario.estado_logico == True).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@app.put("/api/v1/users/{id}", response_model=UserResponse, dependencies=[Depends(requerir_admin)])
def update_user(id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not usuario.estado_logico:
        raise HTTPException(status_code=400, detail="No se puede modificar un usuario inactivo")
    if payload.nombre is not None:
        usuario.nombre = payload.nombre
    if payload.correo is not None:
        existe_correo = db.query(Usuario).filter(Usuario.correo == payload.correo, Usuario.id != id).first()
        if existe_correo:
            raise HTTPException(status_code=400, detail="El correo ya está en uso")
        usuario.correo = payload.correo
    if payload.rol is not None:
        usuario.rol = payload.rol.value
    if payload.password is not None:
        usuario.password_hash = obtener_password_hash(payload.password)
    if payload.estado_logico is not None:
        usuario.estado_logico = payload.estado_logico
    db.commit()
    db.refresh(usuario)
    return usuario

@app.delete("/api/v1/users/{id}", dependencies=[Depends(requerir_admin)])
def logical_delete_user(id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.estado_logico = False
    db.commit()
    return {"message": f"Usuario {usuario.nombre} desactivado lógicamente"}

# --- ENDPOINTS DE PLANES (Lectura: Trabajador, Escritura: Admin) ---
@app.get("/api/v1/planes", response_model=List[PlanResponse], dependencies=[Depends(requerir_trabajador)])
def list_plans(db: Session = Depends(get_db)):
    return db.query(Plan).filter(Plan.estado_logico == True).all()

@app.post("/api/v1/planes", response_model=PlanResponse, dependencies=[Depends(requerir_admin)])
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)):
    nuevo_plan = Plan(
        nombre=payload.nombre,
        duracion_dias=payload.duracion_dias,
        precio_usd=payload.precio_usd,
        estado_logico=True
    )
    db.add(nuevo_plan)
    db.commit()
    db.refresh(nuevo_plan)
    return nuevo_plan

# --- ENDPOINTS DE MIEMBROS ---
@app.get("/api/v1/members", response_model=List[MiembroResponse], dependencies=[Depends(requerir_trabajador)])
def list_members(db: Session = Depends(get_db)):
    miembros = db.query(Miembro).filter(Miembro.estado_logico == True).all()
    response_data = []
    for m in miembros:
        # Buscar su membresía más reciente y su plan
        membresia = db.query(MembresiaMiembro).filter(MembresiaMiembro.miembro_id == m.id).order_by(MembresiaMiembro.id.desc()).first()
        estatus, dias_gracia = calcular_estado_miembro(membresia)
        plan_nombre = None
        plan_id = None
        if membresia:
            plan_obj = db.query(Plan).filter(Plan.id == membresia.plan_id).first()
            if plan_obj:
                plan_nombre = plan_obj.nombre
                plan_id = plan_obj.id
        response_data.append(MiembroResponse(
            id=m.id,
            cedula=m.cedula,
            nombre=m.nombre,
            telefono=m.telefono,
            estado_logico=m.estado_logico,
            estatus_actual=estatus,
            dias_restantes_gracia=dias_gracia,
            plan_nombre=plan_nombre,
            plan_id=plan_id,
        ))
    return response_data

@app.get("/api/v1/members/search/{cedula}", response_model=MiembroResponse, dependencies=[Depends(requerir_trabajador)])
def search_member_by_cedula(cedula: str, db: Session = Depends(get_db)):
    # Búsqueda optimizada por Cédula (índice B-tree)
    miembro = db.query(Miembro).filter(Miembro.cedula == cedula, Miembro.estado_logico == True).first()
    if not miembro:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
        
    membresia = db.query(MembresiaMiembro).filter(MembresiaMiembro.miembro_id == miembro.id).order_by(MembresiaMiembro.id.desc()).first()
    estatus, dias_gracia = calcular_estado_miembro(membresia)
    plan_nombre = None
    plan_id = None
    if membresia:
        plan_obj = db.query(Plan).filter(Plan.id == membresia.plan_id).first()
        if plan_obj:
            plan_nombre = plan_obj.nombre
            plan_id = plan_obj.id
    return MiembroResponse(
        id=miembro.id,
        cedula=miembro.cedula,
        nombre=miembro.nombre,
        telefono=miembro.telefono,
        estado_logico=miembro.estado_logico,
        estatus_actual=estatus,
        dias_restantes_gracia=dias_gracia,
        plan_nombre=plan_nombre,
        plan_id=plan_id,
    )

@app.post("/api/v1/members", response_model=MiembroResponse, dependencies=[Depends(requerir_trabajador)])
def register_member(payload: MiembroCreate, db: Session = Depends(get_db)):
    # Verificar si el plan existe
    plan = db.query(Plan).filter(Plan.id == payload.plan_id, Plan.estado_logico == True).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    # Verificar si ya existe la cédula
    existe = db.query(Miembro).filter(Miembro.cedula == payload.cedula).first()
    if existe:
        if not existe.estado_logico:
            # Restaurar borrado lógico
            existe.estado_logico = True
            existe.nombre = payload.nombre
            existe.telefono = payload.telefono
            db.commit()
            db.refresh(existe)
            
            # Crear nueva membresía vencida con el plan escogido
            nueva_membresia = MembresiaMiembro(
                miembro_id=existe.id,
                plan_id=plan.id,
                fecha_inicio=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=plan.duracion_dias),
                estatus_pago="vencido",
            )
            db.add(nueva_membresia)
            db.commit()
            
            return MiembroResponse(
                id=existe.id,
                cedula=existe.cedula,
                nombre=existe.nombre,
                telefono=existe.telefono,
                estado_logico=existe.estado_logico,
                estatus_actual="vencido",
                dias_restantes_gracia=None,
                plan_nombre=plan.nombre,
                plan_id=plan.id
            )
        raise HTTPException(status_code=400, detail="Ya existe un miembro activo con esta cédula")
        
    nuevo_miembro = Miembro(
        cedula=payload.cedula,
        nombre=payload.nombre,
        telefono=payload.telefono,
        estado_logico=True
    )
    db.add(nuevo_miembro)
    db.commit()
    db.refresh(nuevo_miembro)
    
    # Crear membresía inicial
    nueva_membresia = MembresiaMiembro(
        miembro_id=nuevo_miembro.id,
        plan_id=plan.id,
        fecha_inicio=date.today(),
        fecha_vencimiento=date.today() + timedelta(days=plan.duracion_dias),
        estatus_pago="vencido",
    )
    db.add(nueva_membresia)
    db.commit()
    
    return MiembroResponse(
        id=nuevo_miembro.id,
        cedula=nuevo_miembro.cedula,
        nombre=nuevo_miembro.nombre,
        telefono=nuevo_miembro.telefono,
        estado_logico=nuevo_miembro.estado_logico,
        estatus_actual="vencido",
        dias_restantes_gracia=None,
        plan_nombre=plan.nombre,
        plan_id=plan.id
    )

@app.delete("/api/v1/members/{id}", dependencies=[Depends(requerir_admin)])
def logical_delete_member(id: int, db: Session = Depends(get_db)):
    miembro = db.query(Miembro).filter(Miembro.id == id).first()
    if not miembro:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    
    # Aplicar borrado lógico obligatorio
    miembro.estado_logico = False
    db.commit()
    return {"message": f"Miembro {miembro.nombre} eliminado lógicamente de forma exitosa"}

# --- ENDPOINTS DE PAGOS (Registro de Caja) ---
@app.post("/api/v1/payments/register", response_model=PagoResponse, dependencies=[Depends(requerir_trabajador)])
def register_payment(payload: PagoCreate, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    # Buscar membresía
    membresia = db.query(MembresiaMiembro).filter(MembresiaMiembro.id == payload.membresia_miembro_id).first()
    if not membresia:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
        
    # Obtener el plan para conocer la duración y costo
    plan = db.query(Plan).filter(Plan.id == membresia.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
        
    # Validaciones según moneda
    if payload.moneda == PaymentCurrencyEnum.USD:
        tasa_usd_final = Decimal("1.0000")
        monto_usd_calculado = payload.monto_original
        if payload.monto_original < plan.precio_usd:
            raise HTTPException(status_code=400, detail="Pago insuficiente, será revisado por el gerente")
    else:
        if not payload.tasa_cambio or payload.tasa_cambio <= 0:
            raise HTTPException(status_code=400, detail="La tasa de cambio es requerida y debe ser mayor a cero para pagos en bolívares (VES)")
        tasa_usd_final = payload.tasa_cambio
        precio_local = plan.precio_usd * tasa_usd_final
        if payload.monto_original < precio_local:
            raise HTTPException(status_code=400, detail="Pago insuficiente, será revisado por el gerente")
        monto_usd_calculado = Decimal(payload.monto_original) / Decimal(tasa_usd_final)
    
    # Registrar el Pago al 100% (No se permiten abonos, se registra completo)
    nuevo_pago = Pago(
        membresia_miembro_id=payload.membresia_miembro_id,
        registrado_por=usuario_actual.id,
        monto_original=payload.monto_original,
        moneda=payload.moneda.value,
        tasa_cambio=tasa_usd_final,
        monto_usd=round(monto_usd_calculado, 2),
        metodo_pago=payload.metodo_pago.value,
        referencia=payload.referencia,
        fecha_pago=datetime.utcnow()
    )
    
    # Actualizar fechas de vigencia y estatus de la membresía contratada
    hoy = date.today()
    # Si la membresía actual estaba activa o en gracia, extender desde la fecha de vencimiento previa
    # Si ya estaba vencida, arranca hoy
    if membresia.fecha_vencimiento and membresia.fecha_vencimiento >= hoy:
        fecha_inicio_nueva = membresia.fecha_vencimiento
    else:
        fecha_inicio_nueva = hoy
        
    membresia.fecha_inicio = fecha_inicio_nueva
    membresia.fecha_vencimiento = fecha_inicio_nueva + timedelta(days=plan.duracion_dias)
    membresia.estatus_pago = "activo"
    
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago

@app.post("/api/v1/payments/by-cedula", response_model=PagoResponse, dependencies=[Depends(requerir_trabajador)])
def register_payment_by_cedula(payload: PagoCedulaCreate, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    # Buscar miembro por cédula
    miembro = db.query(Miembro).filter(Miembro.cedula == payload.cedula, Miembro.estado_logico == True).first()
    if not miembro:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    # Obtener última membresía del miembro
    membresia = db.query(MembresiaMiembro).filter(MembresiaMiembro.miembro_id == miembro.id).order_by(MembresiaMiembro.id.desc()).first()
    # Si no hay membresía, crear una automáticamente usando el plan seleccionado por el usuario
    if not membresia:
        plan = db.query(Plan).filter(Plan.id == payload.planSeleccionado_id, Plan.estado_logico == True).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        # crear nueva membresía con estatus vencido (pendiente de pago)
        nueva_membresia = MembresiaMiembro(
            miembro_id=miembro.id,
            plan_id=plan.id,
            fecha_inicio=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=plan.duracion_dias),
            estatus_pago="vencido",
        )
        db.add(nueva_membresia)
        db.commit()
        db.refresh(nueva_membresia)
        membresia = nueva_membresia
    else:
        # Cambiar la membresía al plan seleccionado (permitir cambio de plan)
        plan = db.query(Plan).filter(Plan.id == payload.planSeleccionado_id, Plan.estado_logico == True).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        # actualizar plan de la membresía
        membresia.plan_id = plan.id
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    # Validaciones según moneda
    if payload.moneda == PaymentCurrencyEnum.USD:
        tasa_usd_final = Decimal("1.0000")
        monto_usd_calculado = payload.monto_original
        if payload.monto_original < plan.precio_usd:
            raise HTTPException(status_code=400, detail="Pago insuficiente, será revisado por el gerente")
    else:
        if not payload.tasa_cambio or payload.tasa_cambio <= 0:
            raise HTTPException(status_code=400, detail="La tasa de cambio es requerida y debe ser mayor a cero para pagos en bolívares (VES)")
        tasa_usd_final = payload.tasa_cambio
        precio_local = plan.precio_usd * tasa_usd_final
        if payload.monto_original < precio_local:
            raise HTTPException(status_code=400, detail="Pago insuficiente, será revisado por el gerente")
        monto_usd_calculado = Decimal(payload.monto_original) / Decimal(tasa_usd_final)

    nuevo_pago = Pago(
        membresia_miembro_id=membresia.id,
        registrado_por=usuario_actual.id,
        monto_original=payload.monto_original,
        moneda=payload.moneda.value,
        tasa_cambio=tasa_usd_final,
        monto_usd=round(monto_usd_calculado, 2),
        metodo_pago=payload.metodo_pago.value,
        referencia=payload.referencia,
        fecha_pago=datetime.utcnow()
    )
    # Actualizar fechas de vigencia y estatus de la membresía contratada
    hoy = date.today()
    if membresia.fecha_vencimiento and membresia.fecha_vencimiento >= hoy:
        fecha_inicio_nueva = membresia.fecha_vencimiento
    else:
        fecha_inicio_nueva = hoy
    membresia.fecha_inicio = fecha_inicio_nueva
    membresia.fecha_vencimiento = fecha_inicio_nueva + timedelta(days=plan.duracion_dias)
    membresia.estatus_pago = "activo"
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago

# --- ENDPOINTS DE MEMBRESÍAS ---
@app.post("/api/v1/memberships", response_model=MembresiaResponse, dependencies=[Depends(requerir_trabajador)])
def assign_membership(payload: MembresiaCreate, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == payload.plan_id, Plan.estado_logico == True).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado o inactivo")
        
    # Crear la membresía con estatus vencido por defecto hasta que se registre el pago al 100%
    fecha_vencimiento_calc = payload.fecha_inicio + timedelta(days=plan.duracion_dias)
    
    nueva_membresia = MembresiaMiembro(
        miembro_id=payload.miembro_id,
        plan_id=payload.plan_id,
        fecha_inicio=payload.fecha_inicio,
        fecha_vencimiento=fecha_vencimiento_calc,
        estatus_pago="vencido"  # Requiere pago para activarse
    )
    db.add(nueva_membresia)
    db.commit()
    db.refresh(nueva_membresia)
    return nueva_membresia

# --- ENDPOINTS DE CONTROL DE ACCESO (Check-in) ---
@app.post("/api/v1/asistencias/checkin", response_model=AsistenciaResponse, dependencies=[Depends(requerir_trabajador)])
def register_checkin(payload: AsistenciaCreate, db: Session = Depends(get_db)):
    # Buscar el miembro
    miembro = db.query(Miembro).filter(Miembro.id == payload.miembro_id, Miembro.estado_logico == True).first()
    if not miembro:
        raise HTTPException(status_code=404, detail="Miembro no encontrado o inactivo")
        
    # Verificar estatus del semáforo
    membresia = db.query(MembresiaMiembro).filter(MembresiaMiembro.miembro_id == miembro.id).order_by(MembresiaMiembro.id.desc()).first()
    estatus, _ = calcular_estado_miembro(membresia)
    
    if estatus == "vencido":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso Bloqueado: La membresía está vencida. Requiere pago inmediato."
        )
        
    nueva_asistencia = Asistencia(
        miembro_id=payload.miembro_id,
        fecha_entrada=datetime.utcnow()
    )
    db.add(nueva_asistencia)
    db.commit()
    db.refresh(nueva_asistencia)
    return nueva_asistencia

# --- BATCH / COLA DE ASISTENCIA OFFLINE ---
@app.post("/api/v1/asistencias/batch", dependencies=[Depends(requerir_trabajador)])
def register_batch_checkin(checkins: List[dict], db: Session = Depends(get_db)):
    registrados = 0
    rechazados = 0
    for chk in checkins:
        miembro_id = chk.get("miembro_id")
        fecha_str = chk.get("fecha_entrada")
        
        # Validar miembro
        miembro = db.query(Miembro).filter(Miembro.id == miembro_id, Miembro.estado_logico == True).first()
        if not miembro:
            rechazados += 1
            continue
            
        try:
            fecha_entrada_dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        except Exception:
            fecha_entrada_dt = datetime.utcnow()
            
        nueva_asistencia = Asistencia(
            miembro_id=miembro_id,
            fecha_entrada=fecha_entrada_dt
        )
        db.add(nueva_asistencia)
        registrados += 1
        
    db.commit()
    return {"message": "Sincronización masiva de asistencias completada", "registrados": registrados, "rechazados": rechazados}

# --- ENDPOINT DEL CRON JOB DIARIO (Llamada externa protegida) ---
@app.post("/api/v1/cron/update-statuses", dependencies=[Depends(requerir_trabajador)])
def daily_cron_update_statuses(db: Session = Depends(get_db)):
    hoy = date.today()
    # 1. Mutar a vencido todas las membresías activas/por_vencer cuya fecha_vencimiento sea estrictamente menor a hoy en 6 días o más
    # Es decir: hoy - fecha_vencimiento >= 6 -> fecha_vencimiento <= hoy - 6
    limite_gracia = hoy - timedelta(days=6)
    
    query = text("""
        UPDATE membresias_miembros 
        SET estatus_pago = 'vencido' 
        WHERE fecha_vencimiento <= :limite_gracia 
        AND estatus_pago != 'vencido'
    """)
    
    result = db.execute(query, {"limite_gracia": limite_gracia})
    db.commit()
    
    return {
        "message": "Cron Job ejecutado con éxito a las 00:00:00 simuladas",
        "membresias_bloqueadas_al_dia_6": result.rowcount
    }

# --- ENDPOINTS DE ADMINISTRADOR (Reportes Financieros y KPIs) ---
@app.get("/api/v1/admin/kpis", response_model=KpiSummary, dependencies=[Depends(requerir_admin)])
def get_kpis(db: Session = Depends(get_db)):
    hoy = date.today()
    
    # 1. Ingresos Netos del Mes en USD (suma de monto_usd de todos los pagos del mes en curso)
    primer_dia_mes = hoy.replace(day=1)
    primer_dia_mes_dt = datetime(primer_dia_mes.year, primer_dia_mes.month, primer_dia_mes.day, 0, 0, 0)
    
    ingresos = db.query(func.sum(Pago.monto_usd)).filter(Pago.fecha_pago >= primer_dia_mes_dt).scalar() or Decimal(0)
    
    # 2. Atletas Activos (miembros activos o en gracia en su última membresía)
    # Buscamos miembros cuya última membresía no esté vencida ni en la base de datos ni calculada como tal
    todos_miembros = db.query(Miembro).filter(Miembro.estado_logico == True).all()
    activos = 0
    alertas_vencidos = 0
    
    for m in todos_miembros:
        membresia = db.query(MembresiaMiembro).filter(MembresiaMiembro.miembro_id == m.id).order_by(MembresiaMiembro.id.desc()).first()
        estatus, _ = calcular_estado_miembro(membresia)
        if estatus in ["activo", "en_gracia", "por_vencer"]:
            activos += 1
        elif estatus == "vencido":
            alertas_vencidos += 1
            
    return KpiSummary(
        ingresos_netos_usd=ingresos,
        atletas_activos=activos,
        alertas_vencidos=alertas_vencidos
    )

@app.get("/api/v1/admin/cashflow", response_model=CashFlowReport, dependencies=[Depends(requerir_admin)])
def get_cashflow_report(db: Session = Depends(get_db)):
    # Obtener todos los pagos registrados de forma cronológica descendente
    pagos = db.query(Pago).order_by(Pago.fecha_pago.desc()).all()
    ingresos_totales = sum(p.monto_usd for p in pagos)
    
    return CashFlowReport(
        pagos=pagos,
        ingresos_totales_usd=Decimal(ingresos_totales)
    )
