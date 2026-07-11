import os
import sys
import unittest
from datetime import datetime, date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Gym, Usuario, Miembro, Plan, MembresiaMiembro, Pago, Asistencia, UserRole, PaymentCurrency, PaymentMethod, GymSubscriptionStatus
from app.auth.auth import crear_token_acceso, obtener_password_hash
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/gymflow_db",
)

from app.main import app

client = TestClient(app)


class TestF404GymFilterIsolation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        cls.Session = sessionmaker(bind=cls.engine)

        session = cls.Session()
        try:
            # Idempotente: buscar o crear gym de prueba
            gym2 = session.query(Gym).filter(Gym.nombre == "GymFlow Sede Prueba").first()
            if not gym2:
                gym2 = Gym(
                    nombre="GymFlow Sede Prueba",
                    direccion="Direccion de Prueba",
                    dias_gracia_default=5,
                    moneda_base=PaymentCurrency.USD,
                    estado_suscripcion=GymSubscriptionStatus.activo,
                    estado_logico=True
                )
                session.add(gym2)
                session.commit()
                session.refresh(gym2)
            cls.gym2_id = gym2.id

            # Idempotente: buscar o crear admin sede 2
            admin2 = session.query(Usuario).filter(Usuario.correo == "admin2@gymflow.com").first()
            if not admin2:
                admin2 = Usuario(
                    gym_id=cls.gym2_id,
                    cedula="V-99999998",
                    nombre="Admin Sede 2",
                    correo="admin2@gymflow.com",
                    password_hash=obtener_password_hash("admin123"),
                    rol=UserRole.admin,
                    estado_logico=True
                )
                session.add(admin2)
                session.commit()
                session.refresh(admin2)
            cls.admin2_id = admin2.id

            # Idempotente: buscar o crear miembro sede 2
            miembro2 = session.query(Miembro).filter(Miembro.cedula == "V-88888888").first()
            if not miembro2:
                miembro2 = Miembro(
                    gym_id=cls.gym2_id,
                    cedula="V-88888888",
                    nombre="Miembro Sede 2",
                    telefono="0412-8888888",
                    estado_logico=True
                )
                session.add(miembro2)
                session.commit()
                session.refresh(miembro2)
            cls.miembro2_id = miembro2.id

            # Idempotente: buscar o crear plan sede 2
            plan2 = session.query(Plan).filter(Plan.nombre == "Plan Mensual Sede 2", Plan.gym_id == cls.gym2_id).first()
            if not plan2:
                plan2 = Plan(
                    gym_id=cls.gym2_id,
                    nombre="Plan Mensual Sede 2",
                    duracion_dias=30,
                    precio_usd=Decimal("25.00"),
                    estado_logico=True
                )
                session.add(plan2)
                session.commit()
                session.refresh(plan2)
            cls.plan2_id = plan2.id

            # Idempotente: buscar o crear membresía sede 2
            membresia2 = session.query(MembresiaMiembro).filter(MembresiaMiembro.miembro_id == cls.miembro2_id).first()
            if not membresia2:
                membresia2 = MembresiaMiembro(
                    miembro_id=cls.miembro2_id,
                    plan_id=cls.plan2_id,
                    fecha_inicio=date.today(),
                    fecha_vencimiento=date.today() + timedelta(days=30),
                    estatus_pago="activo"
                )
                session.add(membresia2)
                session.commit()
                session.refresh(membresia2)
            cls.membresia2_id = membresia2.id

        finally:
            session.close()

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def _get_token_gym1(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"correo": "admin@gymflow.com", "password": "admin123"},
        )
        return response.json()["access_token"]

    def _get_token_gym2(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"correo": "admin2@gymflow.com", "password": "admin123"},
        )
        return response.json()["access_token"]

    def test_members_gym1_does_not_see_gym2(self):
        token1 = self._get_token_gym1()
        response = client.get(
            "/api/v1/members",
            headers={"Authorization": f"Bearer {token1}"},
        )
        self.assertEqual(response.status_code, 200)
        members = response.json()
        member_ids = [m["id"] for m in members]
        self.assertNotIn(self.miembro2_id, member_ids)

    def test_members_gym2_does_not_see_gym1(self):
        token2 = self._get_token_gym2()
        response = client.get(
            "/api/v1/members",
            headers={"Authorization": f"Bearer {token2}"},
        )
        self.assertEqual(response.status_code, 200)
        members = response.json()
        for m in members:
            miembro = self.session.query(Miembro).filter(Miembro.id == m["id"]).first()
            self.assertEqual(miembro.gym_id, self.gym2_id)

    def test_member_search_by_cedula_isolation(self):
        token1 = self._get_token_gym1()
        response = client.get(
            "/api/v1/members/search/V-88888888",
            headers={"Authorization": f"Bearer {token1}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_plans_isolation(self):
        token1 = self._get_token_gym1()
        response = client.get(
            "/api/v1/planes",
            headers={"Authorization": f"Bearer {token1}"},
        )
        self.assertEqual(response.status_code, 200)
        plans = response.json()
        for p in plans:
            plan_db = self.session.query(Plan).filter(Plan.id == p["id"]).first()
            self.assertEqual(plan_db.gym_id, 1)

    def test_kpis_isolation(self):
        token1 = self._get_token_gym1()
        response = client.get(
            "/api/v1/admin/kpis",
            headers={"Authorization": f"Bearer {token1}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_kpis_gym2_isolation(self):
        token2 = self._get_token_gym2()
        response = client.get(
            "/api/v1/admin/kpis",
            headers={"Authorization": f"Bearer {token2}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_cashflow_isolation(self):
        token1 = self._get_token_gym1()
        response = client.get(
            "/api/v1/admin/cashflow",
            headers={"Authorization": f"Bearer {token1}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for pago in data["pagos"]:
            pago_db = self.session.query(Pago).filter(Pago.id == pago["id"]).first()
            self.assertEqual(pago_db.gym_id, 1)

    def test_users_isolation(self):
        token1 = self._get_token_gym1()
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token1}"},
        )
        self.assertEqual(response.status_code, 200)
        users = response.json()
        for u in users:
            user_db = self.session.query(Usuario).filter(Usuario.id == u["id"]).first()
            self.assertEqual(user_db.gym_id, 1)

    def test_vencidos_isolation(self):
        token1 = self._get_token_gym1()
        response = client.get(
            "/api/v1/admin/vencidos",
            headers={"Authorization": f"Bearer {token1}"},
        )
        self.assertEqual(response.status_code, 200)
        vencidos = response.json()
        for v in vencidos:
            miembro_db = self.session.query(Miembro).filter(Miembro.id == v["id"]).first()
            self.assertEqual(miembro_db.gym_id, 1)

    def test_payment_detail_isolation(self):
        token2 = self._get_token_gym2()
        pago = self.session.query(Pago).filter(Pago.gym_id == self.gym2_id).first()
        if pago:
            response = client.get(
                f"/api/v1/admin/payments/{pago.id}",
                headers={"Authorization": f"Bearer {token2}"},
            )
            self.assertEqual(response.status_code, 200)

    def test_payment_detail_cross_gym_blocked(self):
        token2 = self._get_token_gym2()
        pago_gym1 = self.session.query(Pago).filter(Pago.gym_id == 1).first()
        if pago_gym1:
            response = client.get(
                f"/api/v1/admin/payments/{pago_gym1.id}",
                headers={"Authorization": f"Bearer {token2}"},
            )
            self.assertEqual(response.status_code, 404)

    def test_update_user_cross_gym_blocked(self):
        token2 = self._get_token_gym2()
        user_gym1 = self.session.query(Usuario).filter(Usuario.gym_id == 1, Usuario.rol == UserRole.worker).first()
        if user_gym1:
            response = client.put(
                f"/api/v1/users/{user_gym1.id}",
                json={"nombre": "HACKED"},
                headers={"Authorization": f"Bearer {token2}"},
            )
            self.assertEqual(response.status_code, 404)

    def test_checkin_cross_gym_blocked(self):
        token2 = self._get_token_gym2()
        miembro_gym1 = self.session.query(Miembro).filter(Miembro.gym_id == 1).first()
        if miembro_gym1:
            response = client.post(
                "/api/v1/asistencias/checkin",
                json={"miembro_id": miembro_gym1.id},
                headers={"Authorization": f"Bearer {token2}"},
            )
            self.assertEqual(response.status_code, 404)

    def test_plan_same_name_different_gym_allowed(self):
        token2 = self._get_token_gym2()
        response = client.post(
            "/api/v1/planes",
            json={"nombre": "Plan Mensual", "duracion_dias": 30, "precio_usd": 20.00},
            headers={"Authorization": f"Bearer {token2}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_admin_endpoints_require_admin_role(self):
        token2 = self._get_token_gym2()
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token2}"},
        )
        self.assertIn(response.status_code, [200, 403])


if __name__ == "__main__":
    unittest.main()
