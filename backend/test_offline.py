import os
import sys
import unittest
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add backend directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import register_batch_checkin, get_kpis, search_member_by_cedula
from app.models import Usuario, Miembro, Plan, MembresiaMiembro, Pago, Asistencia, UserRole, PaymentMethod
from app.schemas import KpiSummary

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/gymflow_db")
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestGymFlowOfflineAndQADirect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = TestingSessionLocal()
        cls.clean_up_test_data(cls.db)

        # Setup test objects
        # 1. Test Admin
        cls.test_admin = Usuario(
            cedula="V-99000001",
            nombre="Admin Test QA",
            correo="admintestqa@gymflow.com",
            password_hash="dummyhash",
            rol=UserRole.admin.value,
            estado_logico=True
        )
        cls.db.add(cls.test_admin)

        # 2. Test Worker
        cls.test_worker = Usuario(
            cedula="V-99000002",
            nombre="Worker Test QA",
            correo="workertestqa@gymflow.com",
            password_hash="dummyhash",
            rol=UserRole.worker.value,
            estado_logico=True
        )
        cls.db.add(cls.test_worker)

        # 3. Test Plan
        cls.test_plan = Plan(
            nombre="Plan QA Offline Test",
            duracion_dias=30,
            precio_usd=Decimal("35.00"),
            estado_logico=True
        )
        cls.db.add(cls.test_plan)
        cls.db.commit()

        # 4. Test Miembro
        cls.test_miembro = Miembro(
            cedula="V-88000001",
            nombre="Atleta QA Test",
            telefono="04125555555",
            estado_logico=True
        )
        cls.db.add(cls.test_miembro)
        cls.db.commit()

        # 5. Create Membresia
        cls.test_membresia = MembresiaMiembro(
            miembro_id=cls.test_miembro.id,
            plan_id=cls.test_plan.id,
            fecha_inicio=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            estatus_pago="activo"
        )
        cls.db.add(cls.test_membresia)
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.clean_up_test_data(cls.db)
        cls.db.close()

    @classmethod
    def clean_up_test_data(cls, session):
        session.query(Asistencia).filter(Asistencia.miembro_id.in_(
            session.query(Miembro.id).filter(Miembro.cedula.like("V-8800%"))
        )).delete(synchronize_session=False)

        session.query(Pago).filter(Pago.registrado_por.in_(
            session.query(Usuario.id).filter(Usuario.cedula.like("V-9900%"))
        )).delete(synchronize_session=False)

        session.query(MembresiaMiembro).filter(MembresiaMiembro.miembro_id.in_(
            session.query(Miembro.id).filter(Miembro.cedula.like("V-8800%"))
        )).delete(synchronize_session=False)

        session.query(Miembro).filter(Miembro.cedula.like("V-8800%")).delete(synchronize_session=False)
        session.query(Plan).filter(Plan.nombre == "Plan QA Offline Test").delete(synchronize_session=False)
        session.query(Usuario).filter(Usuario.cedula.like("V-9900%")).delete(synchronize_session=False)
        session.commit()

    def test_batch_offline_checkins_sync_direct(self):
        # Directly invoke the batch sync endpoint logic
        payload = [
            {
                "miembro_id": self.test_miembro.id,
                "fecha_entrada": (datetime.utcnow() - timedelta(minutes=30)).isoformat() + "Z"
            },
            {
                "miembro_id": self.test_miembro.id,
                "fecha_entrada": datetime.utcnow().isoformat() + "Z"
            }
        ]

        result = register_batch_checkin(checkins=payload, db=self.db)
        self.assertEqual(result["registrados"], 2)
        self.assertEqual(result["rechazados"], 0)

        # Verify in DB
        asistencias = self.db.query(Asistencia).filter(Asistencia.miembro_id == self.test_miembro.id).all()
        self.assertEqual(len(asistencias), 2)

    def test_admin_kpis_calculation(self):
        # Call admin KPI function directly
        kpis: KpiSummary = get_kpis(db=self.db)
        self.assertGreaterEqual(kpis.atletas_activos, 1)

    def test_btree_index_performance(self):
        # Querying by cedula directly using backend function
        import time
        start_time = time.perf_counter()
        miembro_res = search_member_by_cedula(cedula=self.test_miembro.cedula, db=self.db)
        duration = time.perf_counter() - start_time
        
        self.assertEqual(miembro_res.nombre, "Atleta QA Test")
        self.assertLess(duration, 0.05, "B-Tree index query should take less than 50ms")

if __name__ == "__main__":
    unittest.main()
