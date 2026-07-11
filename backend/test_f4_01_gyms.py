import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.database import Base
from app.models import Gym, GymSubscriptionStatus, PaymentCurrency


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/gymflow_db",
)


class TestGymsModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        Base.metadata.create_all(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_1_gym_creation(self):
        gym = Gym(
            nombre="Gym Centro",
            direccion="Calle Principal #123",
            telefono="0412-1234567",
            dias_gracia_default=5,
            moneda_base=PaymentCurrency.USD,
            fecha_alta=datetime.utcnow(),
            estado_suscripcion=GymSubscriptionStatus.activo,
            estado_logico=True,
        )
        self.session.add(gym)
        self.session.commit()

        result = self.session.query(Gym).filter_by(nombre="Gym Centro").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.nombre, "Gym Centro")
        self.assertEqual(result.direccion, "Calle Principal #123")
        self.assertEqual(result.telefono, "0412-1234567")
        self.assertEqual(result.dias_gracia_default, 5)
        self.assertEqual(result.moneda_base, PaymentCurrency.USD)
        self.assertEqual(result.estado_suscripcion, GymSubscriptionStatus.activo)
        self.assertTrue(result.estado_logico)
        self.assertIsNotNone(result.fecha_alta)

    def test_2_gym_defaults(self):
        gym = Gym(
            nombre="Gym Default",
            direccion="Av. Libertador",
        )
        self.session.add(gym)
        self.session.commit()

        result = self.session.query(Gym).filter_by(nombre="Gym Default").first()
        self.assertEqual(result.dias_gracia_default, 5)
        self.assertEqual(result.moneda_base, PaymentCurrency.USD)
        self.assertEqual(result.estado_suscripcion, GymSubscriptionStatus.activo)
        self.assertTrue(result.estado_logico)
        self.assertIsNotNone(result.fecha_alta)

    def test_3_nombre_uniqueness(self):
        gym1 = Gym(nombre="Gym Único", direccion="Dir 1")
        self.session.add(gym1)
        self.session.commit()

        gym2 = Gym(nombre="Gym Único", direccion="Dir 2")
        self.session.add(gym2)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_4_logical_deletion_preserves_integrity(self):
        gym = Gym(
            nombre="Gym Borrado Lógico",
            direccion="Dir Test",
            estado_logico=True,
        )
        self.session.add(gym)
        self.session.commit()
        gym_id = gym.id

        gym.estado_logico = False
        self.session.commit()

        result = self.session.query(Gym).filter_by(id=gym_id).first()
        self.assertIsNotNone(result)
        self.assertFalse(result.estado_logico)
        self.assertEqual(result.nombre, "Gym Borrado Lógico")

    def test_5_gym_subscription_status_enum(self):
        gym = Gym(
            nombre="Gym Pausado",
            direccion="Dir P",
            estado_suscripcion=GymSubscriptionStatus.pausado,
        )
        self.session.add(gym)
        self.session.commit()

        result = self.session.query(Gym).filter_by(nombre="Gym Pausado").first()
        self.assertEqual(result.estado_suscripcion, GymSubscriptionStatus.pausado)

    def test_6_telefono_nullable(self):
        gym = Gym(nombre="Gym Sin Tel", direccion="Dir T")
        self.session.add(gym)
        self.session.commit()

        result = self.session.query(Gym).filter_by(nombre="Gym Sin Tel").first()
        self.assertIsNone(result.telefono)


if __name__ == "__main__":
    unittest.main()
