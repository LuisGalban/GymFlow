import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import (
    Gym, Usuario, UserRole, PaymentCurrency, GymSubscriptionStatus,
)
from app.auth.auth import crear_token_acceso, obtener_password_hash
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/gymflow_db",
)

from app.main import app

client = TestClient(app)

CRON_URL = "/api/v1/cron/update-statuses"


class TestH03CronRBAC(unittest.TestCase):
    """H-03: Only super_admin may invoke the daily cron endpoint."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        cls.Session = sessionmaker(bind=cls.engine)
        session = cls.Session()
        try:
            # Ensure a test gym exists
            gym = session.query(Gym).filter(Gym.nombre == "GymFlow Sede Prueba H03").first()
            if not gym:
                gym = Gym(
                    nombre="GymFlow Sede Prueba H03",
                    direccion="Direccion H03",
                    dias_gracia_default=5,
                    moneda_base=PaymentCurrency.USD,
                    estado_suscripcion=GymSubscriptionStatus.activo,
                    estado_logico=True,
                )
                session.add(gym)
                session.commit()
                session.refresh(gym)
            cls.gym_id = gym.id

            # Create a worker user
            worker = session.query(Usuario).filter(Usuario.correo == "worker_h03@gymflow.com").first()
            if not worker:
                worker = Usuario(
                    gym_id=cls.gym_id,
                    cedula="V-10101010",
                    nombre="Worker H03",
                    correo="worker_h03@gymflow.com",
                    password_hash=obtener_password_hash("worker123"),
                    rol=UserRole.worker,
                    estado_logico=True,
                )
                session.add(worker)
                session.commit()
                session.refresh(worker)
            cls.worker_id = worker.id

            # Create an admin user
            admin = session.query(Usuario).filter(Usuario.correo == "admin_h03@gymflow.com").first()
            if not admin:
                admin = Usuario(
                    gym_id=cls.gym_id,
                    cedula="V-20202020",
                    nombre="Admin H03",
                    correo="admin_h03@gymflow.com",
                    password_hash=obtener_password_hash("admin123"),
                    rol=UserRole.admin,
                    estado_logico=True,
                )
                session.add(admin)
                session.commit()
                session.refresh(admin)
            cls.admin_id = admin.id

            # Create a super_admin user
            sa = session.query(Usuario).filter(Usuario.correo == "superadmin_h03@gymflow.com").first()
            if not sa:
                sa = Usuario(
                    gym_id=cls.gym_id,
                    cedula="V-40404040",
                    nombre="Super Admin H03",
                    correo="superadmin_h03@gymflow.com",
                    password_hash=obtener_password_hash("superadmin123"),
                    rol="super_admin",
                    estado_logico=True,
                )
                session.add(sa)
                session.commit()
                session.refresh(sa)
            cls.super_admin_id = sa.id
        finally:
            session.close()

    def _login(self, correo, password):
        resp = client.post(
            "/api/v1/auth/login",
            json={"correo": correo, "password": password},
        )
        self.assertEqual(resp.status_code, 200, f"Login failed for {correo}")
        return resp.json()["access_token"]

    def test_worker_gets_403_on_cron(self):
        """Worker role must receive 403 on the cron endpoint."""
        token = self._login("worker_h03@gymflow.com", "worker123")
        resp = client.post(
            CRON_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 403, f"Worker got {resp.status_code}, expected 403")

    def test_admin_gets_403_on_cron(self):
        """Admin role must receive 403 on the cron endpoint."""
        token = self._login("admin_h03@gymflow.com", "admin123")
        resp = client.post(
            CRON_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 403, f"Admin got {resp.status_code}, expected 403")

    def test_super_admin_can_access_cron(self):
        """Super admin must be allowed to invoke the cron endpoint."""
        token = self._login("superadmin_h03@gymflow.com", "superadmin123")
        resp = client.post(
            CRON_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertIn(resp.status_code, [200, 201], f"Super admin got {resp.status_code}, expected 200")

    def test_unauthenticated_gets_401_on_cron(self):
        """Unauthenticated request must receive 401."""
        resp = client.post(CRON_URL)
        self.assertIn(resp.status_code, [401, 403])


if __name__ == "__main__":
    unittest.main()
