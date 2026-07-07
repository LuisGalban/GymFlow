import os
import sys
import uuid
import unittest
from datetime import datetime, date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import Usuario, Miembro, Plan, MembresiaMiembro, Pago, UserRole
from app.auth.auth import obtener_password_hash
from app.main import app, get_kpis, get_cashflow_report
from app.schemas import KpiSummary, CashFlowReport, PagoResponse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/gymflow_db")
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestAdminPanelFix(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = TestingSessionLocal()
        cls.clean_up_test_data(cls.db)

        pwd = obtener_password_hash("test123")
        cls.admin = Usuario(
            cedula="V-99999999", nombre="Admin Test", correo="admintestfix@gymflow.com",
            password_hash=pwd, rol=UserRole.admin.value, estado_logico=True
        )
        cls.db.add(cls.admin)

        cls.plan = Plan(
            nombre="Plan Test", duracion_dias=30, precio_usd=Decimal("35.00"), estado_logico=True
        )
        cls.db.add(cls.plan)
        cls.db.commit()

        cls.miembro = Miembro(
            cedula="V-88888888", nombre="Test Member", telefono="04120000000", estado_logico=True
        )
        cls.db.add(cls.miembro)
        cls.db.commit()

        cls.membresia = MembresiaMiembro(
            miembro_id=cls.miembro.id, plan_id=cls.plan.id,
            fecha_inicio=date.today() - timedelta(days=5),
            fecha_vencimiento=date.today() + timedelta(days=25),
            estatus_pago="activo"
        )
        cls.db.add(cls.membresia)
        cls.db.commit()

        cls.pago = Pago(
            membresia_miembro_id=cls.membresia.id,
            registrado_por=cls.admin.id,
            monto_original=Decimal("35.00"),
            moneda="USD", tasa_cambio=Decimal("1.0000"),
            monto_usd=Decimal("35.00"),
            metodo_pago="pago_movil",
            fecha_pago=datetime.utcnow()
        )
        cls.db.add(cls.pago)
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.clean_up_test_data(cls.db)
        cls.db.close()

    @classmethod
    def clean_up_test_data(cls, session):
        session.query(Pago).filter(Pago.registrado_por == cls.admin.id if hasattr(cls, 'admin') else -1).delete(synchronize_session=False) if hasattr(cls, 'admin') else None
        session.query(Pago).filter(Pago.membresia_miembro_id.in_(
            session.query(MembresiaMiembro.id).join(Miembro).filter(Miembro.cedula == "V-88888888")
        )).delete(synchronize_session=False)
        session.query(MembresiaMiembro).filter(MembresiaMiembro.miembro_id.in_(
            session.query(Miembro.id).filter(Miembro.cedula == "V-88888888")
        )).delete(synchronize_session=False)
        session.query(Miembro).filter(Miembro.cedula == "V-88888888").delete(synchronize_session=False)
        session.query(Plan).filter(Plan.nombre == "Plan Test").delete(synchronize_session=False)
        session.query(Usuario).filter(Usuario.cedula == "V-99999999").delete(synchronize_session=False)
        session.commit()

    # ---- RED PHASE TESTS (should FAIL) ----

    def test_1_admin_kpis_returns_number_not_string(self):
        """REPRODUCE: toFixed error — ingresos_netos_usd must be a number, not str"""
        kpis: KpiSummary = get_kpis(db=self.db)
        raw = kpis.model_dump(mode='json')
        self.assertIsInstance(raw["ingresos_netos_usd"], (int, float),
                              f"ingresos_netos_usd is {type(raw['ingresos_netos_usd'])} — causes .toFixed() crash")

    def test_2_cashflow_pagos_monto_usd_is_number(self):
        """REPRODUCE: toFixed error on cashflow table rows"""
        report = get_cashflow_report(db=self.db)
        raw = report.model_dump(mode='json')
        for p in raw["pagos"]:
            self.assertIsInstance(p["monto_usd"], (int, float),
                                  f"monto_usd is {type(p['monto_usd'])} — causes .toFixed() crash")

    def test_3_admin_endpoints_http_200_not_422(self):
        """REPRODUCE: 422 Unprocessable Entity via HTTP"""
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        self.assertEqual(resp.status_code, 200)
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_kpis = client.get("/api/v1/admin/kpis", headers=headers)
        self.assertEqual(resp_kpis.status_code, 200,
                         f"KPIs returned {resp_kpis.status_code}: {resp_kpis.text[:200]}")

        resp_cash = client.get("/api/v1/admin/cashflow", headers=headers)
        self.assertEqual(resp_cash.status_code, 200,
                         f"Cashflow returned {resp_cash.status_code}: {resp_cash.text[:200]}")


    def test_4_staff_flow_register_then_appears_in_list(self):
        """GREEN: full flow — login → register worker → list includes that worker"""
        suffix = uuid.uuid4().hex[:8]
        client = TestClient(app)
        # Login as admin
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        self.assertEqual(resp.status_code, 200)
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Register a new worker with unique credentials
        resp_register = client.post("/api/v1/users/register", json={
            "cedula": f"V-UUID{suffix}",
            "nombre": f"Test Worker {suffix}",
            "correo": f"workerflow_{suffix}@gymflow.com",
            "password": "test123",
            "rol": "worker"
        }, headers=headers)
        self.assertEqual(resp_register.status_code, 200,
                         f"Register returned {resp_register.status_code}: {resp_register.text[:200]}")

        # List users and verify the new worker appears
        resp_list = client.get("/api/v1/users", headers=headers)
        self.assertEqual(resp_list.status_code, 200,
                         f"List returned {resp_list.status_code}: {resp_list.text[:200]}")
        uids = [u["id"] for u in resp_list.json()]
        self.assertIn(resp_register.json()["id"], uids,
                      "Newly registered worker not found in user list")

        # Verify the worker has role 'worker'
        new_worker = next(u for u in resp_list.json() if u["id"] == resp_register.json()["id"])
        self.assertEqual(new_worker["rol"], "worker",
                         f"Expected rol=worker, got {new_worker['rol']}")

        # Clean up: mark the new worker inactive (borrado lógico) via API
        resp_delete = client.delete(f"/api/v1/users/{resp_register.json()['id']}", headers=headers)
        self.assertEqual(resp_delete.status_code, 200,
                         f"Delete returned {resp_delete.status_code}: {resp_delete.text[:200]}")


if __name__ == "__main__":
    unittest.main()
