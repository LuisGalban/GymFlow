import os
import sys
import unittest
from datetime import datetime, date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Usuario, Miembro, Plan, MembresiaMiembro, Asistencia, UserRole
from app.auth.auth import obtener_password_hash
from app.main import app

from fastapi.testclient import TestClient

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/gymflow_db")
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestF14OfflineTolerance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = TestingSessionLocal()
        cls.clean_up_test_data(cls.db)

        pwd = obtener_password_hash("test123")
        cls.worker = Usuario(
            cedula="V-99111111", nombre="Worker F14",
            correo="workerf14@gymflow.com",
            password_hash=pwd, rol=UserRole.worker.value, estado_logico=True
        )
        cls.db.add(cls.worker)

        cls.plan = Plan(
            nombre="Plan F14 Test", duracion_dias=30,
            precio_usd=Decimal("35.00"), estado_logico=True
        )
        cls.db.add(cls.plan)
        cls.db.commit()

        cls.miembro = Miembro(
            cedula="V-88111111", nombre="Atleta F14",
            telefono="04121111111", estado_logico=True
        )
        cls.db.add(cls.miembro)
        cls.db.commit()

        cls.membresia = MembresiaMiembro(
            miembro_id=cls.miembro.id, plan_id=cls.plan.id,
            fecha_inicio=date.today() - timedelta(days=10),
            fecha_vencimiento=date.today() + timedelta(days=20),
            estatus_pago="activo"
        )
        cls.db.add(cls.membresia)
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.clean_up_test_data(cls.db)
        cls.db.close()

    @classmethod
    def clean_up_test_data(cls, session):
        session.query(Asistencia).filter(Asistencia.miembro_id.in_(
            session.query(Miembro.id).filter(Miembro.cedula == "V-88111111")
        )).delete(synchronize_session=False)
        session.query(MembresiaMiembro).filter(MembresiaMiembro.miembro_id.in_(
            session.query(Miembro.id).filter(Miembro.cedula == "V-88111111")
        )).delete(synchronize_session=False)
        session.query(Miembro).filter(Miembro.cedula == "V-88111111").delete(synchronize_session=False)
        session.query(Plan).filter(Plan.nombre == "Plan F14 Test").delete(synchronize_session=False)
        session.query(Usuario).filter(Usuario.cedula == "V-99111111").delete(synchronize_session=False)
        session.commit()

    def _get_worker_token(self, client: TestClient) -> str:
        resp = client.post("/api/v1/auth/login", json={
            "correo": "workerf14@gymflow.com",
            "password": "test123"
        })
        self.assertEqual(resp.status_code, 200)
        return resp.json()["access_token"]

    def test_batch_accepts_plain_array_via_http(self):
        """RED→GREEN: /api/v1/asistencias/batch accepts a JSON array directly (not wrapped)"""
        client = TestClient(app)
        token = self._get_worker_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        payload = [
            {"miembro_id": self.miembro.id, "fecha_entrada": datetime.utcnow().isoformat() + "Z"},
            {"miembro_id": self.miembro.id, "fecha_entrada": (datetime.utcnow() - timedelta(minutes=15)).isoformat() + "Z"},
        ]

        resp = client.post("/api/v1/asistencias/batch", json=payload, headers=headers)
        self.assertEqual(resp.status_code, 200, f"Expected 200, got {resp.status_code}: {resp.text}")

        data = resp.json()
        self.assertEqual(data["registrados"], 2)
        self.assertEqual(data["rechazados"], 0)

    def test_batch_rejects_invalid_member(self):
        """Batch correctly reports rejected entries for invalid members"""
        client = TestClient(app)
        token = self._get_worker_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        payload = [
            {"miembro_id": 999999, "fecha_entrada": datetime.utcnow().isoformat() + "Z"},
        ]

        resp = client.post("/api/v1/asistencias/batch", json=payload, headers=headers)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data["registrados"], 0)
        self.assertEqual(data["rechazados"], 1)


if __name__ == "__main__":
    unittest.main()
