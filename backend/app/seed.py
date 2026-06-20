import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal

# Aseguramos que la raíz del backend esté en el sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.database import SessionLocal, Base
from app.models import Usuario, Miembro, Plan, MembresiaMiembro, Pago, Asistencia, UserRole
from app.auth.auth import obtener_password_hash

def seed_database():
    db = SessionLocal()
    try:
        print("Limpiando tablas para la siembra limpia...")
        # Limpiar en orden inverso de dependencias
        db.query(Asistencia).delete()
        db.query(Pago).delete()
        db.query(MembresiaMiembro).delete()
        db.query(Plan).delete()
        db.query(Miembro).delete()
        db.query(Usuario).delete()
        db.commit()

        print("Creando planes base...")
        plan_basico = Plan(
            nombre="Plan Básico",
            duracion_dias=30,
            precio_usd=Decimal("15.00"),
            estado_logico=True
        )
        plan_intermedio = Plan(
            nombre="Plan Intermedio",
            duracion_dias=30,
            precio_usd=Decimal("30.00"),
            estado_logico=True
        )
        plan_premium = Plan(
            nombre="Plan Premium",
            duracion_dias=30,
            precio_usd=Decimal("45.00"),
            estado_logico=True
        )
        db.add_all([plan_basico, plan_intermedio, plan_premium])
        db.commit()

        print("Creando usuarios del personal (Admin y Trabajador)...")
        # Contraseñas cifradas con bcrypt
        pwd_admin = obtener_password_hash("admin123")
        pwd_recep = obtener_password_hash("worker123")

        admin = Usuario(
            cedula="V-12345678",
            nombre="Luis Galbán (Admin)",
            correo="admin@gymflow.com",
            password_hash=pwd_admin,
            rol=UserRole.admin.value,
            estado_logico=True
        )
        worker = Usuario(
            cedula="V-87654321",
            nombre="María Recepcionista",
            correo="recepcion@gymflow.com",
            password_hash=pwd_recep,
            rol=UserRole.worker.value,
            estado_logico=True
        )
        db.add_all([admin, worker])
        db.commit()

        print("Creando atletas (Miembros)...")
        m_activo = Miembro(cedula="V-25111222", nombre="Carlos Atleta Activo", telefono="0412-1111111", estado_logico=True)
        m_gracia = Miembro(cedula="V-26222333", nombre="Ana En Periodo Gracia", telefono="0414-2222222", estado_logico=True)
        m_vencido = Miembro(cedula="V-27333444", nombre="José Bloqueado Vencido", telefono="0424-3333333", estado_logico=True)
        m_borrado = Miembro(cedula="V-28444555", nombre="Pedro Eliminado Lógico", telefono="0416-4444444", estado_logico=False)
        db.add_all([m_activo, m_gracia, m_vencido, m_borrado])
        db.commit()

        print("Asignando membresías e insertando pagos...")
        hoy = date.today()

        # 1. Miembro Activo: Membresía vence en 20 días
        membresia_activa = MembresiaMiembro(
            miembro_id=m_activo.id,
            plan_id=plan_intermedio.id,
            fecha_inicio=hoy - timedelta(days=10),
            fecha_vencimiento=hoy + timedelta(days=20),
            estatus_pago="activo"
        )
        db.add(membresia_activa)
        db.commit()

        pago_activo = Pago(
            membresia_miembro_id=membresia_activa.id,
            registrado_por=worker.id,
            monto_original=Decimal("30.00"),
            moneda="USD",
            tasa_cambio=Decimal("1.0000"),
            monto_usd=Decimal("30.00"),
            metodo_pago="efectivo_usd",
            fecha_pago=datetime.utcnow() - timedelta(days=10)
        )
        db.add(pago_activo)

        # 2. Miembro En Gracia: Venció hace 2 días (dentro del umbral de 5 días)
        membresia_gracia = MembresiaMiembro(
            miembro_id=m_gracia.id,
            plan_id=plan_basico.id,
            fecha_inicio=hoy - timedelta(days=32),
            fecha_vencimiento=hoy - timedelta(days=2),
            estatus_pago="activo" # Sigue activo en BD pero el algoritmo calculará 'en_gracia'
        )
        db.add(membresia_gracia)
        db.commit()

        # Pago realizado en Bolívares normalizado a tasa de 36.50
        pago_gracia = Pago(
            membresia_miembro_id=membresia_gracia.id,
            registrado_por=worker.id,
            monto_original=Decimal("547.50"), # 547.50 Bs / 36.50 = 15 USD
            moneda="VES",
            tasa_cambio=Decimal("36.5000"),
            monto_usd=Decimal("15.00"),
            metodo_pago="pago_movil",
            referencia="123456",
            fecha_pago=datetime.utcnow() - timedelta(days=32)
        )
        db.add(pago_gracia)

        # 3. Miembro Vencido: Venció hace 15 días (supera el límite de gracia y está marcado como vencido)
        membresia_vencida = MembresiaMiembro(
            miembro_id=m_vencido.id,
            plan_id=plan_premium.id,
            fecha_inicio=hoy - timedelta(days=45),
            fecha_vencimiento=hoy - timedelta(days=15),
            estatus_pago="vencido"
        )
        db.add(membresia_vencida)
        db.commit()

        pago_vencido = Pago(
            membresia_miembro_id=membresia_vencida.id,
            registrado_por=admin.id,
            monto_original=Decimal("45.00"),
            moneda="USD",
            tasa_cambio=Decimal("1.0000"),
            monto_usd=Decimal("45.00"),
            metodo_pago="efectivo_usd",
            fecha_pago=datetime.utcnow() - timedelta(days=45)
        )
        db.add(pago_vencido)
        
        # Guardar todo
        db.commit()
        print(">>> ¡Siembra de datos (Seed) completada con éxito en PostgreSQL! <<<")
        print("\n=== Credenciales de Acceso Creadas ===")
        print("1. Administrador:")
        print("   Correo: admin@gymflow.com")
        print("   Contraseña: admin123")
        print("2. Recepcionista:")
        print("   Correo: recepcion@gymflow.com")
        print("   Contraseña: worker123")
        print("======================================")

    except Exception as e:
        db.rollback()
        print(f"Error al sembrar la base de datos: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
