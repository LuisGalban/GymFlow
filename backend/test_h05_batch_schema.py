import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import (
    Gym, Usuario, Miembro, Plan, MembresiaMiembro, Asistencia,
    UserRole, PaymentCurrency, GymSubscriptionStatus,
)
from app.auth.auth import obtener_password_hash
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/gymflow_db",
)

from app.main import app

client = TestClient(app)

BATCH_URL = "/api/v1/asistencias/batch"


class TestH05BatchSchema(unittest.TestCase):
    """H-05: Batch check-in must use Pydantic schema and enforce 500-item limit."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
        session = cls.Session()
        try:
            gym = session.query(Gym).filter(Gym.nombre == "GymFlow Sede Prueba H05").first()
            if not gym:
                gym = Gym(
                    nombre="GymFlow Sede Prueba H05",
                    direccion="Direccion H05",
                    dias_gracia_default=5,
                    moneda_base=PaymentCurrency.USD,
                    estado_suscripcion=GymSubscriptionStatus.activo,
                    estado_logico=True,
                )
                session.add(gym)
                session.commit()
                session.refresh(gym)
            cls.gym_id = gym.id

            worker = session.query(Usuario).filter(Usuario.correo == "worker_h05@gymflow.com").first()
            if not worker:
                worker = Usuario(
                    gym_id=cls.gym_id,
                    cedula="V-50505050",
                    nombre="Worker H05",
                    correo="worker_h05@gymflow.com",
                    password_hash=obtener_password_hash("worker123"),
                    rol=UserRole.worker,
                    estado_logico=True,
                )
                session.add(worker)
                session.commit()
                session.refresh(worker)
            cls.worker_id = worker.id
        finally:
            session.close()

    def _login(self):
        resp = client.post(
            "/api/v1/auth/login",
            json={"correo": "worker_h05@gymflow.com", "password": "worker123"},
        )
        self.assertEqual(resp.status_code, 200)
        return resp.json()["access_token"]

    def test_empty_batch_succeeds(self):
        """An empty batch should return 200 with 0 registered and 0 rejected."""
        token = self._login()
        resp = client.post(
            BATCH_URL,
            json={"items": []},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["registrados"], 0)
        self.assertEqual(data["rechazados"], 0)

    def test_valid_batch_with_nonexistent_member(self):
        """A batch with valid schema but nonexistent member is parsed and counted as rejected."""
        token = self._login()
        resp = client.post(
            BATCH_URL,
            json={"items": [{"miembro_id": 99999999}]},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["registrados"], 0)
        self.assertEqual(data["rechazados"], 1)

    def test_valid_batch_multiple_items(self):
        """A batch with multiple valid-schema items is parsed correctly."""
        token = self._login()
        resp = client.post(
            BATCH_URL,
            json={"items": [
                {"miembro_id": 99999998},
                {"miembro_id": 99999997},
                {"miembro_id": 99999996},
            ]},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["registrados"], 0)
        self.assertEqual(data["rechazados"], 3)

    def test_batch_with_optional_fecha_entrada(self):
        """Items with optional fecha_entrada field are accepted."""
        token = self._login()
        resp = client.post(
            BATCH_URL,
            json={"items": [
                {"miembro_id": 99999999, "fecha_entrada": "2026-07-11T10:00:00"},
                {"miembro_id": 99999998},
            ]},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["rechazados"], 2)

    def test_batch_exceeding_limit_returns_422(self):
        """A batch with more than 500 items must return 422 Validation Error (Pydantic max_length)."""
        token = self._login()
        items = [{"miembro_id": 1} for _ in range(501)]
        resp = client.post(
            BATCH_URL,
            json={"items": items},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 422)

    def test_batch_of_exactly_500_passes_limit_check(self):
        """A batch with exactly 500 items should NOT be rejected by the limit."""
        token = self._login()
        items = [{"miembro_id": 9999999} for _ in range(500)]
        resp = client.post(
            BATCH_URL,
            json={"items": items},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["rechazados"], 500)

    def test_invalid_missing_items_key_returns_422(self):
        """Sending body without 'items' key should return 422."""
        token = self._login()
        resp = client.post(
            BATCH_URL,
            json={},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 422)

    def test_invalid_items_not_list_returns_422(self):
        """Sending non-list 'items' should return 422."""
        token = self._login()
        resp = client.post(
            BATCH_URL,
            json={"items": "not_a_list"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 422)

    def test_invalid_item_missing_miembro_id_returns_422(self):
        """An item without miembro_id should return 422."""
        token = self._login()
        resp = client.post(
            BATCH_URL,
            json={"items": [{"fecha_entrada": "2026-07-11"}]},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 422)

    def test_unauthenticated_gets_401_or_403(self):
        """Unauthenticated request must receive 401 or 403."""
        resp = client.post(BATCH_URL, json={"items": []})
        self.assertIn(resp.status_code, [401, 403])


if __name__ == "__main__":
    unittest.main()
