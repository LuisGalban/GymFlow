import os
import sys
import unittest
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.models import Gym, Plan, Pago, MembresiaMiembro, Miembro, Usuario, UserRole, GymSubscriptionStatus, PaymentCurrency
from app.database import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/gymflow_db")
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TEST_CEDULA_PREFIX = "V-F22TEST"


class TestCheckConstraints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = TestingSessionLocal()
        cls._clean_test_data(cls.db)

        cls.gym = Gym(
            nombre="Gym Test F22",
            direccion="Dir Test F22",
            dias_gracia_default=5,
            moneda_base=PaymentCurrency.USD,
            fecha_alta=datetime.utcnow(),
            estado_suscripcion=GymSubscriptionStatus.activo,
            estado_logico=True,
        )
        cls.db.add(cls.gym)
        cls.db.commit()
        cls.db.refresh(cls.gym)

        cls.miembro = Miembro(
            gym_id=cls.gym.id,
            cedula=f"{TEST_CEDULA_PREFIX}-MIEMBRO",
            nombre="Test Miembro F22",
            estado_logico=True
        )
        cls.plan_valido = Plan(
            gym_id=cls.gym.id,
            nombre="Plan Test F22",
            duracion_dias=30,
            precio_usd=10.00,
            estado_logico=True
        )
        cls.usuario = Usuario(
            gym_id=cls.gym.id,
            cedula=f"{TEST_CEDULA_PREFIX}-USER",
            nombre="Test User F22",
            correo="testuserf22@gymflow.com",
            password_hash="dummy_hash",
            rol=UserRole.worker.value,
            estado_logico=True
        )
        cls.db.add_all([cls.miembro, cls.plan_valido, cls.usuario])
        cls.db.commit()

        cls.membresia = MembresiaMiembro(
            miembro_id=cls.miembro.id,
            plan_id=cls.plan_valido.id,
            fecha_inicio=date.today(),
            fecha_vencimiento=date(2099, 12, 31),
            estatus_pago="activo"
        )
        cls.db.add(cls.membresia)
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls._clean_test_data(cls.db)
        cls.db.close()
        Base.metadata.drop_all(bind=engine)

    @classmethod
    def _clean_test_data(cls, session):
        session.query(Pago).filter(
            Pago.membresia_miembro_id.in_(
                session.query(MembresiaMiembro.id).join(Miembro).filter(
                    Miembro.cedula.like(f"{TEST_CEDULA_PREFIX}%")
                )
            )
        ).delete(synchronize_session=False)

        session.query(MembresiaMiembro).filter(
            MembresiaMiembro.miembro_id.in_(
                session.query(Miembro.id).filter(
                    Miembro.cedula.like(f"{TEST_CEDULA_PREFIX}%")
                )
            )
        ).delete(synchronize_session=False)

        session.query(Plan).filter(
            Plan.nombre.like("Plan Test F22%")
        ).delete(synchronize_session=False)

        session.query(Miembro).filter(
            Miembro.cedula.like(f"{TEST_CEDULA_PREFIX}%")
        ).delete(synchronize_session=False)

        session.query(Usuario).filter(
            Usuario.correo.like("testuserf22%")
        ).delete(synchronize_session=False)

        session.query(Gym).filter(
            Gym.nombre.like("Gym Test F22%")
        ).delete(synchronize_session=False)
        session.commit()

    def test_1_plan_precio_negativo_rechazado(self):
        """RED->GREEN: Plan con precio_usd=-10 debe ser rechazado por CHECK constraint"""
        plan_malo = Plan(
            gym_id=self.gym.id,
            nombre="Plan Malo F22",
            duracion_dias=30,
            precio_usd=-10.00,
            estado_logico=True
        )
        self.db.add(plan_malo)
        with self.assertRaises(IntegrityError) as ctx:
            self.db.flush()
        self.db.rollback()
        error_msg = str(ctx.exception)
        self.assertIn("ck_plan_precio_usd_no_negativo", error_msg)

    def test_2_pago_monto_original_cero_rechazado(self):
        """RED->GREEN: Pago con monto_original=0 debe ser rechazado por CHECK constraint"""
        pago_malo = Pago(
            gym_id=self.gym.id,
            membresia_miembro_id=self.membresia.id,
            registrado_por=self.usuario.id,
            monto_original=0,
            moneda="USD",
            tasa_cambio=1.0,
            monto_usd=0,
            metodo_pago="efectivo_usd",
            fecha_pago=datetime.utcnow()
        )
        self.db.add(pago_malo)
        with self.assertRaises(IntegrityError) as ctx:
            self.db.flush()
        self.db.rollback()
        error_msg = str(ctx.exception)
        self.assertIn("ck_pago_monto_original_positivo", error_msg)

    def test_3_pago_tasa_cambio_negativa_rechazado(self):
        """RED->GREEN: Pago con tasa_cambio=-1 debe ser rechazado por CHECK constraint"""
        pago_malo = Pago(
            gym_id=self.gym.id,
            membresia_miembro_id=self.membresia.id,
            registrado_por=self.usuario.id,
            monto_original=100,
            moneda="VES",
            tasa_cambio=-1,
            monto_usd=-100,
            metodo_pago="efectivo_bs",
            fecha_pago=datetime.utcnow()
        )
        self.db.add(pago_malo)
        with self.assertRaises(IntegrityError) as ctx:
            self.db.flush()
        self.db.rollback()
        error_msg = str(ctx.exception)
        self.assertIn("ck_pago_tasa_cambio_positivo", error_msg)


if __name__ == "__main__":
    unittest.main()
