import os
import sys
import uuid
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Gym, Usuario, PaymentCurrency, GymSubscriptionStatus
from app.schemas import RegisterGymAdminRequest
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/gymflow_db",
)

from app.main import app

client = TestClient(app)


class TestH06RaceCondition(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        cls.Session = sessionmaker(bind=cls.engine)
        session = cls.Session()

        token = uuid.uuid4()
        gym = Gym(
            nombre="GymFlow H06 Race Test",
            direccion="Direccion H06",
            dias_gracia_default=5,
            moneda_base=PaymentCurrency.USD,
            estado_suscripcion=GymSubscriptionStatus.activo,
            estado_logico=True,
            token_sede=token,
        )
        session.add(gym)
        session.commit()
        session.refresh(gym)
        cls.gym_id = gym.id
        cls.token_sede = str(token)
        session.close()

    def setUp(self):
        db = self.Session()
        # Clean any existing admin for this gym
        db.query(Usuario).filter(
            Usuario.gym_id == self.gym_id,
            Usuario.rol == "admin",
        ).delete()
        # Reset token_sede
        db.query(Gym).filter(Gym.id == self.gym_id).update(
            {"token_sede": uuid.UUID(self.token_sede)}
        )
        db.commit()
        db.close()

    @classmethod
    def tearDownClass(cls):
        session = cls.Session()
        session.query(Usuario).filter(Usuario.gym_id == cls.gym_id).delete()
        session.query(Gym).filter(Gym.id == cls.gym_id).delete()
        session.commit()
        session.close()
        cls.engine.dispose()

    def test_concurrent_requests_only_one_succeeds(self):
        results = [None, None]
        barrier = threading.Barrier(2)

        def make_request(idx):
            # Use a fresh client per thread
            thread_client = TestClient(app)
            payload = {
                "token_sede": self.token_sede,
                "nombre": f"Admin H06 Thread {idx}",
                "correo": f"h06admin{idx}@test.com",
                "password": "testpass123",
            }
            barrier.wait()
            resp = thread_client.post(
                "/api/v1/auth/register-gym-admin", json=payload
            )
            results[idx] = resp.status_code

        t1 = threading.Thread(target=make_request, args=(0,))
        t2 = threading.Thread(target=make_request, args=(1,))
        t1.start()
        t2.start()
        t1.join(timeout=10)
        t2.join(timeout=10)

        statuses = sorted(results)
        self.assertEqual(
            statuses,
            [200, 400],
            f"Expected [200, 400] but got {statuses}",
        )

        if results[0] == 400:
            loser_idx = 0
        else:
            loser_idx = 1

        loser_client = TestClient(app)
        payload_loser = {
            "token_sede": self.token_sede,
            "nombre": f"Admin H06 Loser",
            "correo": f"h06admin{loser_idx}@test.com",
            "password": "testpass123",
        }
        resp_loser = loser_client.post(
            "/api/v1/auth/register-gym-admin", json=payload_loser
        )
        # The loser request may have already been processed before the token
        # was nulled, so we check the response we captured in the thread

        db = self.Session()
        admin_count = db.query(Usuario).filter(
            Usuario.gym_id == self.gym_id,
            Usuario.rol == "admin",
            Usuario.estado_logico == True,
        ).count()
        db.close()
        self.assertEqual(admin_count, 1, "Only one admin should exist")


if __name__ == "__main__":
    unittest.main()
