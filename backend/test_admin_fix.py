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
        # Clean any orphaned data from test_13 (disabled member)
        for cedula in ["V-88888888", "V-DISABLED99", "V-VENCIDO01", "V-VENCIDO02"]:
            session.query(Pago).filter(Pago.membresia_miembro_id.in_(
                session.query(MembresiaMiembro.id).join(Miembro).filter(Miembro.cedula == cedula)
            )).delete(synchronize_session=False)
            session.query(MembresiaMiembro).filter(MembresiaMiembro.miembro_id.in_(
                session.query(Miembro.id).filter(Miembro.cedula == cedula)
            )).delete(synchronize_session=False)
            session.query(Miembro).filter(Miembro.cedula == cedula).delete(synchronize_session=False)
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


    # ---- FILTER TESTS ----

    def test_5_kpis_filtro_dia_returns_200(self):
        """F2-01: KPIs with rango=dia returns 200"""
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_kpis = client.get("/api/v1/admin/kpis?rango=dia", headers=headers)
        self.assertEqual(resp_kpis.status_code, 200,
                         f"KPIs dia returned {resp_kpis.status_code}: {resp_kpis.text[:200]}")
        data = resp_kpis.json()
        self.assertIn("ingresos_netos_usd", data)

        resp_cash = client.get("/api/v1/admin/cashflow?rango=dia", headers=headers)
        self.assertEqual(resp_cash.status_code, 200,
                         f"Cashflow dia returned {resp_cash.status_code}: {resp_cash.text[:200]}")

    def test_6_kpis_filtro_semana_returns_200(self):
        """F2-01: KPIs with rango=semana returns 200"""
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_kpis = client.get("/api/v1/admin/kpis?rango=semana", headers=headers)
        self.assertEqual(resp_kpis.status_code, 200)
        self.assertIn("ingresos_netos_usd", resp_kpis.json())

    def test_7_kpis_filtro_mes_returns_200(self):
        """F2-01: KPIs with rango=mes returns 200 (default behavior)"""
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_kpis = client.get("/api/v1/admin/kpis?rango=mes", headers=headers)
        self.assertEqual(resp_kpis.status_code, 200)
        self.assertIn("ingresos_netos_usd", resp_kpis.json())

    def test_8_kpis_filtro_ano_returns_200(self):
        """F2-01: KPIs with rango=ano returns 200"""
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_kpis = client.get("/api/v1/admin/kpis?rango=ano", headers=headers)
        self.assertEqual(resp_kpis.status_code, 200)
        self.assertIn("ingresos_netos_usd", resp_kpis.json())

    def test_9_kpis_filtro_personalizado_incluye_pago(self):
        """F2-01: rango=personalizado with desde/hasta includes pago de hoy"""
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        hoy_str = date.today().isoformat()
        resp_kpis = client.get(
            f"/api/v1/admin/kpis?rango=personalizado&desde={hoy_str}&hasta={hoy_str}",
            headers=headers
        )
        self.assertEqual(resp_kpis.status_code, 200)
        data = resp_kpis.json()
        self.assertGreater(data["ingresos_netos_usd"], 0,
                           "Pago de prueba debería aparecer en el rango personalizado de hoy")

    def test_10_kpis_filtro_personalizado_excluye_fuera_rango(self):
        """F2-01: rango=personalizado con fecha pasada excluye pago de hoy"""
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_kpis = client.get(
            "/api/v1/admin/kpis?rango=personalizado&desde=2020-01-01&hasta=2020-01-31",
            headers=headers
        )
        self.assertEqual(resp_kpis.status_code, 200)
        data = resp_kpis.json()
        self.assertEqual(data["ingresos_netos_usd"], 0,
                         "Pago de hoy NO debe aparecer en rango 2020")

    def test_11_endpoint_funciona_sin_parametros(self):
        """F2-01: Sin filtros, conserva comportamiento por defecto"""
        kpis = get_kpis(db=self.db)
        raw = kpis.model_dump(mode="json")
        self.assertIsInstance(raw["ingresos_netos_usd"], (int, float))

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


    # ---- F2-03: TRANSPARENCIA DE ALERTAS — LISTA DE VENCIDOS ----

    def test_15_vencidos_endpoint_returns_200(self):
        """F2-03: GET /api/v1/admin/vencidos returns 200"""
        # Create a vencido member for this test
        db = TestingSessionLocal()
        try:
            vencido_member = Miembro(
                cedula="V-VENCIDO01", nombre="Vencido Member", telefono="04120000001", estado_logico=True
            )
            db.add(vencido_member)
            db.commit()
            member_id = vencido_member.id

            memb = MembresiaMiembro(
                miembro_id=member_id, plan_id=self.plan.id,
                fecha_inicio=date.today() - timedelta(days=40),
                fecha_vencimiento=date.today() - timedelta(days=10),
                estatus_pago="vencido"
            )
            db.add(memb)
            db.commit()
            memb_id = memb.id
        finally:
            db.close()

        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        self.assertEqual(resp.status_code, 200)
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_vencidos = client.get("/api/v1/admin/vencidos", headers=headers)
        self.assertEqual(resp_vencidos.status_code, 200,
                         f"Vencidos returned {resp_vencidos.status_code}: {resp_vencidos.text[:200]}")
        data = resp_vencidos.json()
        vencido_entry = next((v for v in data if v["cedula"] == "V-VENCIDO01"), None)
        self.assertIsNotNone(vencido_entry, "Vencido member not found in list")
        self.assertEqual(vencido_entry["nombre"], "Vencido Member")
        self.assertEqual(vencido_entry["dias_vencido"], 10)
        self.assertIn("id", vencido_entry)
        self.assertIn("cedula", vencido_entry)
        self.assertIn("telefono", vencido_entry)

        # Clean up
        db2 = TestingSessionLocal()
        try:
            db2.query(MembresiaMiembro).filter(MembresiaMiembro.id == memb_id).delete(synchronize_session=False)
            db2.query(Miembro).filter(Miembro.id == member_id).delete(synchronize_session=False)
            db2.commit()
        finally:
            db2.close()

    def test_16_vencidos_excludes_logically_deleted_members(self):
        """F2-03: Members with estado_logico=False are excluded"""
        db = TestingSessionLocal()
        try:
            disabled_member = Miembro(
                cedula="V-VENCIDO02", nombre="Disabled Vencido", telefono="04120000002", estado_logico=False
            )
            db.add(disabled_member)
            db.commit()
            member_id = disabled_member.id

            memb = MembresiaMiembro(
                miembro_id=member_id, plan_id=self.plan.id,
                fecha_inicio=date.today() - timedelta(days=40),
                fecha_vencimiento=date.today() - timedelta(days=10),
                estatus_pago="vencido"
            )
            db.add(memb)
            db.commit()
            memb_id = memb.id
        finally:
            db.close()

        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_vencidos = client.get("/api/v1/admin/vencidos", headers=headers)
        data = resp_vencidos.json()
        found = any(v["cedula"] == "V-VENCIDO02" for v in data)
        self.assertFalse(found, "Disabled member should not appear in vencidos list")

        # Clean up
        db2 = TestingSessionLocal()
        try:
            db2.query(MembresiaMiembro).filter(MembresiaMiembro.id == memb_id).delete(synchronize_session=False)
            db2.query(Miembro).filter(Miembro.id == member_id).delete(synchronize_session=False)
            db2.commit()
        finally:
            db2.close()

    # ---- F2-02: DETALLE TRANSACCIONAL ----

    def test_12_payment_detail_returns_200_with_correct_data(self):
        """F2-02: GET /api/v1/admin/payments/{id} returns 200 with full detail"""
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_detail = client.get(f"/api/v1/admin/payments/{self.pago.id}", headers=headers)
        self.assertEqual(resp_detail.status_code, 200,
                         f"Payment detail returned {resp_detail.status_code}: {resp_detail.text[:200]}")
        data = resp_detail.json()
        self.assertEqual(data["id"], self.pago.id)
        self.assertEqual(data["miembro_nombre"], "Test Member")
        self.assertEqual(data["miembro_cedula"], "V-88888888")
        self.assertEqual(data["plan_nombre"], "Plan Test")
        self.assertEqual(data["registrador_nombre"], "Admin Test")
        self.assertIn("monto_original", data)
        self.assertIn("monto_usd", data)
        self.assertIn("metodo_pago", data)
        self.assertIn("fecha_pago", data)

    def test_13_payment_detail_with_disabled_member_shows_desactivado(self):
        """F2-02: Payment where member was soft-deleted shows '[Registro desactivado]'"""
        # Create a disabled member + payment for this test
        db = TestingSessionLocal()
        try:
            disabled_member = Miembro(
                cedula="V-DISABLED99", nombre="Disabled Member", telefono="04120000000", estado_logico=False
            )
            db.add(disabled_member)
            db.commit()
            member_id = disabled_member.id

            memb = MembresiaMiembro(
                miembro_id=member_id, plan_id=self.plan.id,
                fecha_inicio=date.today() - timedelta(days=5),
                fecha_vencimiento=date.today() + timedelta(days=25),
                estatus_pago="activo"
            )
            db.add(memb)
            db.commit()
            memb_id = memb.id

            pago_disabled = Pago(
                membresia_miembro_id=memb_id,
                registrado_por=self.admin.id,
                monto_original=Decimal("35.00"),
                moneda="USD", tasa_cambio=Decimal("1.0000"),
                monto_usd=Decimal("35.00"),
                metodo_pago="pago_movil",
                fecha_pago=datetime.utcnow()
            )
            db.add(pago_disabled)
            db.commit()
            pago_id = pago_disabled.id
        finally:
            db.close()

        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_detail = client.get(f"/api/v1/admin/payments/{pago_id}", headers=headers)
        self.assertEqual(resp_detail.status_code, 200)
        data = resp_detail.json()
        self.assertEqual(data["miembro_nombre"], "[Registro desactivado]")
        self.assertEqual(data["miembro_cedula"], "[Registro desactivado]")
        self.assertEqual(data["registrador_nombre"], "Admin Test")

        # Clean up
        db2 = TestingSessionLocal()
        try:
            db2.query(Pago).filter(Pago.id == pago_id).delete(synchronize_session=False)
            db2.query(MembresiaMiembro).filter(MembresiaMiembro.id == memb_id).delete(synchronize_session=False)
            db2.query(Miembro).filter(Miembro.id == member_id).delete(synchronize_session=False)
            db2.commit()
        finally:
            db2.close()

    def test_14_payment_detail_404_for_non_existent(self):
        """F2-02: GET /api/v1/admin/payments/{non_existent_id} returns 404"""
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "admintestfix@gymflow.com",
            "password": "test123"
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_detail = client.get("/api/v1/admin/payments/999999", headers=headers)
        self.assertEqual(resp_detail.status_code, 404,
                         f"Expected 404, got {resp_detail.status_code}: {resp_detail.text[:200]}")


if __name__ == "__main__":
    unittest.main()
