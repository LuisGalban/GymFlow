import os
import sys
import uuid
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import (
    Gym, Usuario, Miembro, Plan, MembresiaMiembro,
    UserRole, PaymentCurrency, GymSubscriptionStatus,
)
from app.auth.auth import crear_token_acceso, obtener_password_hash
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/gymflow_db",
)

from app.main import app

client = TestClient(app)


class TestF405SuperAdmin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        cls.Session = sessionmaker(bind=cls.engine)
        session = cls.Session()
        try:
            gym = session.query(Gym).filter(Gym.nombre == "GymFlow Sede Prueba F405").first()
            if not gym:
                gym = Gym(
                    nombre="GymFlow Sede Prueba F405",
                    direccion="Direccion F405",
                    dias_gracia_default=5,
                    moneda_base=PaymentCurrency.USD,
                    estado_suscripcion=GymSubscriptionStatus.activo,
                    estado_logico=True,
                )
                session.add(gym)
                session.commit()
                session.refresh(gym)
            cls.gym_id = gym.id

            admin = session.query(Usuario).filter(Usuario.correo == "admin_f405@gymflow.com").first()
            if not admin:
                admin = Usuario(
                    gym_id=cls.gym_id,
                    cedula="V-30303030",
                    nombre="Admin F405",
                    correo="admin_f405@gymflow.com",
                    password_hash=obtener_password_hash("admin123"),
                    rol=UserRole.admin,
                    estado_logico=True,
                )
                session.add(admin)
                session.commit()
                session.refresh(admin)
            cls.admin_id = admin.id

            super_admin = session.query(Usuario).filter(Usuario.correo == "superadmin_f405@gymflow.com").first()
            if not super_admin:
                super_admin = Usuario(
                    gym_id=cls.gym_id,
                    cedula="V-50505050",
                    nombre="Super Admin F405",
                    correo="superadmin_f405@gymflow.com",
                    password_hash=obtener_password_hash("superadmin123"),
                    rol="super_admin",
                    estado_logico=True,
                )
                session.add(super_admin)
                session.commit()
                session.refresh(super_admin)
            cls.super_admin_id = super_admin.id
        finally:
            session.close()

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def _get_admin_token(self):
        resp = client.post(
            "/api/v1/auth/login",
            json={"correo": "admin_f405@gymflow.com", "password": "admin123"},
        )
        return resp.json()["access_token"]

    def _get_super_admin_token(self):
        resp = client.post(
            "/api/v1/auth/login",
            json={"correo": "superadmin_f405@gymflow.com", "password": "superadmin123"},
        )
        return resp.json()["access_token"]

    def test_admin_cannot_access_super_admin_endpoints(self):
        token = self._get_admin_token()
        for method, url in [
            ("GET", "/api/v1/super-admin/gyms"),
        ]:
            if method == "GET":
                resp = client.get(url, headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(resp.status_code, 403, f"Admin should get 403 on {url}")

    def test_admin_cannot_create_gym_via_super_admin(self):
        token = self._get_admin_token()
        resp = client.post(
            "/api/v1/super-admin/gyms",
            json={"nombre": "Should Fail", "direccion": "Nowhere"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 403)

    def test_unauthenticated_cannot_access_super_admin(self):
        resp = client.get("/api/v1/super-admin/gyms")
        self.assertIn(resp.status_code, [401, 403])

    def test_super_admin_can_create_gym(self):
        token = self._get_super_admin_token()
        resp = client.post(
            "/api/v1/super-admin/gyms",
            json={"nombre": f"Test Gym {uuid.uuid4().hex[:8]}", "direccion": "Calle Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("token_sede", data)
        self.assertIn("id", data)
        self.assertEqual(data["estado_suscripcion"], "activo")
        self._created_gym_id = data["id"]
        self._created_token_sede = data["token_sede"]

    def test_super_admin_can_list_gyms(self):
        token = self._get_super_admin_token()
        resp = client.get(
            "/api/v1/super-admin/gyms",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        gym_ids = [g["id"] for g in data]
        self.assertIn(self.gym_id, gym_ids)

    def test_super_admin_can_pause_gym(self):
        token = self._get_super_admin_token()
        resp = client.put(
            f"/api/v1/super-admin/gyms/{self.gym_id}/suscripcion",
            json={"estado_suscripcion": "pausado"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["estado_suscripcion"], "pausado")
        # Restore
        client.put(
            f"/api/v1/super-admin/gyms/{self.gym_id}/suscripcion",
            json={"estado_suscripcion": "activo"},
            headers={"Authorization": f"Bearer {token}"},
        )

    def test_super_admin_can_suspend_gym(self):
        token = self._get_super_admin_token()
        resp = client.put(
            f"/api/v1/super-admin/gyms/{self.gym_id}/suscripcion",
            json={"estado_suscripcion": "suspendido"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["estado_suscripcion"], "suspendido")
        # Restore
        client.put(
            f"/api/v1/super-admin/gyms/{self.gym_id}/suscripcion",
            json={"estado_suscripcion": "activo"},
            headers={"Authorization": f"Bearer {token}"},
        )

    def test_invalid_subscription_status_rejected(self):
        token = self._get_super_admin_token()
        resp = client.put(
            f"/api/v1/super-admin/gyms/{self.gym_id}/suscripcion",
            json={"estado_suscripcion": "invalido"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 422)

    def test_full_onboarding_flow(self):
        token = self._get_super_admin_token()
        gym_name = f"Onboarding Gym {uuid.uuid4().hex[:8]}"
        resp = client.post(
            "/api/v1/super-admin/gyms",
            json={"nombre": gym_name, "direccion": "Avenida Onboarding"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)
        token_sede = resp.json()["token_sede"]

        # Register admin with token
        resp = client.post(
            "/api/v1/auth/register-gym-admin",
            json={
                "token_sede": token_sede,
                "nombre": "Owner Onboarding",
                "correo": f"owner_{uuid.uuid4().hex[:8]}@test.com",
                "password": "owner123",
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

        # Verify the new user is linked to the correct gym
        admin_token = data["access_token"]
        me_resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(me_resp.status_code, 200)
        me_data = me_resp.json()
        self.assertEqual(me_data["rol"], "admin")

    def test_used_token_is_rejected(self):
        token = self._get_super_admin_token()
        gym_name = f"Used Token Gym {uuid.uuid4().hex[:8]}"
        resp = client.post(
            "/api/v1/super-admin/gyms",
            json={"nombre": gym_name, "direccion": "Somewhere"},
            headers={"Authorization": f"Bearer {token}"},
        )
        token_sede = resp.json()["token_sede"]

        # First registration succeeds
        resp = client.post(
            "/api/v1/auth/register-gym-admin",
            json={
                "token_sede": token_sede,
                "nombre": "First Owner",
                "correo": f"first_{uuid.uuid4().hex[:8]}@test.com",
                "password": "owner123",
            },
        )
        self.assertEqual(resp.status_code, 200)

        # Second registration with same token is rejected (token cleared = 404, or 400)
        resp = client.post(
            "/api/v1/auth/register-gym-admin",
            json={
                "token_sede": token_sede,
                "nombre": "Second Owner",
                "correo": f"second_{uuid.uuid4().hex[:8]}@test.com",
                "password": "owner123",
            },
        )
        self.assertIn(resp.status_code, [400, 404], "Used token must be rejected")

    def test_invalid_token_returns_error(self):
        resp = client.post(
            "/api/v1/auth/register-gym-admin",
            json={
                "token_sede": str(uuid.uuid4()),
                "nombre": "Nobody",
                "correo": f"nobody_{uuid.uuid4().hex[:8]}@test.com",
                "password": "owner123",
            },
        )
        self.assertEqual(resp.status_code, 404)

    def test_paused_gym_token_rejected(self):
        token = self._get_super_admin_token()
        gym_name = f"Paused Gym {uuid.uuid4().hex[:8]}"
        resp = client.post(
            "/api/v1/super-admin/gyms",
            json={"nombre": gym_name, "direccion": "Pause Ave"},
            headers={"Authorization": f"Bearer {token}"},
        )
        token_sede = resp.json()["token_sede"]
        gym_id = resp.json()["id"]

        # Pause the gym
        client.put(
            f"/api/v1/super-admin/gyms/{gym_id}/suscripcion",
            json={"estado_suscripcion": "pausado"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Try to register with token of paused gym
        resp = client.post(
            "/api/v1/auth/register-gym-admin",
            json={
                "token_sede": token_sede,
                "nombre": "Should Fail",
                "correo": f"fail_{uuid.uuid4().hex[:8]}@test.com",
                "password": "owner123",
            },
        )
        self.assertIn(resp.status_code, [400, 403])


if __name__ == "__main__":
    unittest.main()
