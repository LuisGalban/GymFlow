import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Gym, Plan, PaymentCurrency, GymSubscriptionStatus

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/gymflow_db",
)


class TestH07UniqueConstraintPlanes(unittest.TestCase):
    """H-07: UniqueConstraint on planes(nombre, gym_id) must be enforced in the DB."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

        session = cls.Session()
        try:
            gym = session.query(Gym).filter(Gym.nombre == "GymFlow H07 Constraint Test").first()
            if not gym:
                gym = Gym(
                    nombre="GymFlow H07 Constraint Test",
                    direccion="Direccion H07",
                    dias_gracia_default=5,
                    moneda_base=PaymentCurrency.USD,
                    estado_suscripcion=GymSubscriptionStatus.activo,
                    estado_logico=True,
                )
                session.add(gym)
                session.commit()
                session.refresh(gym)
            cls.gym1_id = gym.id

            gym2 = session.query(Gym).filter(Gym.nombre == "GymFlow H07 Constraint Test 2").first()
            if not gym2:
                gym2 = Gym(
                    nombre="GymFlow H07 Constraint Test 2",
                    direccion="Direccion H07-2",
                    dias_gracia_default=5,
                    moneda_base=PaymentCurrency.USD,
                    estado_suscripcion=GymSubscriptionStatus.activo,
                    estado_logico=True,
                )
                session.add(gym2)
                session.commit()
                session.refresh(gym2)
            cls.gym2_id = gym2.id
        finally:
            session.close()

    def setUp(self):
        session = self.Session()
        try:
            session.query(Plan).filter(
                Plan.gym_id.in_([self.gym1_id, self.gym2_id])
            ).delete(synchronize_session=False)
            session.commit()
        finally:
            session.close()

    def test_duplicate_plan_name_same_gym_raises_integrity_error(self):
        """Inserting two plans with the same name in the same gym must raise IntegrityError."""
        session = self.Session()
        try:
            plan1 = Plan(
                gym_id=self.gym1_id,
                nombre="Plan Premium",
                duracion_dias=30,
                precio_usd=29.99,
                estado_logico=True,
            )
            session.add(plan1)
            session.commit()

            plan2 = Plan(
                gym_id=self.gym1_id,
                nombre="Plan Premium",
                duracion_dias=60,
                precio_usd=49.99,
                estado_logico=True,
            )
            session.add(plan2)
            with self.assertRaises(exc.IntegrityError):
                session.commit()
            session.rollback()
        finally:
            session.close()

    def test_same_plan_name_different_gym_allowed(self):
        """Plans with the same name in DIFFERENT gyms must be allowed."""
        session = self.Session()
        try:
            plan1 = Plan(
                gym_id=self.gym1_id,
                nombre="Plan Básico",
                duracion_dias=30,
                precio_usd=19.99,
                estado_logico=True,
            )
            session.add(plan1)
            session.commit()

            plan2 = Plan(
                gym_id=self.gym2_id,
                nombre="Plan Básico",
                duracion_dias=30,
                precio_usd=19.99,
                estado_logico=True,
            )
            session.add(plan2)
            session.commit()

            count = session.query(Plan).filter(
                Plan.nombre == "Plan Básico",
                Plan.gym_id.in_([self.gym1_id, self.gym2_id]),
            ).count()
            self.assertEqual(count, 2)
        finally:
            session.close()

    def test_constraint_exists_in_database(self):
        """The uq_plan_nombre_gym constraint must exist in the database."""
        session = self.Session()
        try:
            result = session.execute(
                __import__("sqlalchemy").text(
                    "SELECT conname FROM pg_constraint "
                    "WHERE conname = 'uq_plan_nombre_gym'"
                )
            )
            row = result.fetchone()
            self.assertIsNotNone(row, "uq_plan_nombre_gym constraint not found in pg_constraint")
            self.assertEqual(row[0], "uq_plan_nombre_gym")
        finally:
            session.close()

    @classmethod
    def tearDownClass(cls):
        session = cls.Session()
        session.query(Plan).filter(
            Plan.gym_id.in_([cls.gym1_id, cls.gym2_id])
        ).delete(synchronize_session=False)
        session.query(Gym).filter(
            Gym.id.in_([cls.gym1_id, cls.gym2_id])
        ).delete(synchronize_session=False)
        session.commit()
        session.close()
        cls.engine.dispose()


if __name__ == "__main__":
    unittest.main()
