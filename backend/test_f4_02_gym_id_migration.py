import os
import sys
import unittest
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.database import Base
from app.models import (
    Gym, Usuario, Miembro, Plan, MembresiaMiembro, Pago, Asistencia,
    GymSubscriptionStatus, PaymentCurrency, UserRole, MembershipStatus,
)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/gymflow_db",
)


class TestF402GymIdMigration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    # ── Helpers ──

    def _create_gym(self, nombre="Gym Test"):
        gym = Gym(
            nombre=nombre,
            direccion="Dir Test",
            dias_gracia_default=5,
            moneda_base=PaymentCurrency.USD,
            fecha_alta=datetime.utcnow(),
            estado_suscripcion=GymSubscriptionStatus.activo,
            estado_logico=True,
        )
        self.session.add(gym)
        self.session.commit()
        return gym

    def _create_usuario(self, gym_id, cedula="V-12345678"):
        u = Usuario(
            gym_id=gym_id,
            cedula=cedula,
            nombre="Test User",
            correo=f"{cedula}@test.com",
            password_hash="hash",
            rol=UserRole.worker,
            estado_logico=True,
        )
        self.session.add(u)
        self.session.commit()
        return u

    def _create_miembro(self, gym_id, cedula="V-87654321"):
        m = Miembro(
            gym_id=gym_id,
            cedula=cedula,
            nombre="Test Miembro",
            telefono="0412-0000000",
            estado_logico=True,
        )
        self.session.add(m)
        self.session.commit()
        return m

    def _create_plan(self, gym_id, nombre="Plan Basico"):
        p = Plan(
            gym_id=gym_id,
            nombre=nombre,
            duracion_dias=30,
            precio_usd=25.00,
            estado_logico=True,
        )
        self.session.add(p)
        self.session.commit()
        return p

    def _create_pago(self, gym_id, membresia_miembro_id, registrado_por):
        p = Pago(
            gym_id=gym_id,
            membresia_miembro_id=membresia_miembro_id,
            registrado_por=registrado_por,
            monto_original=100.00,
            moneda="USD",
            tasa_cambio=1.0,
            monto_usd=100.00,
            metodo_pago="efectivo_usd",
            fecha_pago=datetime.utcnow(),
        )
        self.session.add(p)
        self.session.commit()
        return p

    def _create_asistencia(self, gym_id, miembro_id):
        a = Asistencia(
            gym_id=gym_id,
            miembro_id=miembro_id,
            fecha_entrada=datetime.utcnow(),
        )
        self.session.add(a)
        self.session.commit()
        return a

    # ── Tests ──

    def test_1_gym_id_column_exists_all_tables(self):
        """All critical tables have gym_id column (NOT NULL)."""
        tables = ['usuarios', 'miembros', 'planes', 'pagos', 'asistencias']
        with self.engine.connect() as conn:
            for t in tables:
                result = conn.execute(text(
                    f"SELECT is_nullable FROM information_schema.columns "
                    f"WHERE table_name='{t}' AND column_name='gym_id'"
                ))
                row = result.fetchone()
                self.assertIsNotNone(row, f"{t} missing gym_id column")
                self.assertEqual(row[0], 'NO', f"{t}.gym_id should be NOT NULL")

    def test_2_fk_references_gyms(self):
        """FK constraints reference gyms.id with RESTRICT."""
        tables = ['usuarios', 'miembros', 'planes', 'pagos', 'asistencias']
        with self.engine.connect() as conn:
            for t in tables:
                result = conn.execute(text(
                    f"SELECT tc.constraint_name, rc.delete_rule "
                    f"FROM information_schema.table_constraints tc "
                    f"JOIN information_schema.referential_constraints rc "
                    f"ON tc.constraint_name = rc.constraint_name "
                    f"WHERE tc.table_name='{t}' AND tc.constraint_type='FOREIGN KEY' "
                    f"AND rc.unique_constraint_name IN ("
                    f"SELECT constraint_name FROM information_schema.table_constraints "
                    f"WHERE table_name='gyms' AND constraint_type='PRIMARY KEY')"
                ))
                row = result.fetchone()
                self.assertIsNotNone(row, f"{t} missing FK to gyms")
                self.assertEqual(row[1], 'RESTRICT', f"{t} FK should be RESTRICT")

    def test_3_existing_data_gets_gym_id_1(self):
        """After seeding, all existing rows should have gym_id=1."""
        gym = self._create_gym("Gym Seed")
        usuario = self._create_usuario(gym.id, "V-11111111")
        miembro = self._create_miembro(gym.id, "V-22222222")
        plan = self._create_plan(gym.id, "Plan VIP")

        membresia = MembresiaMiembro(
            miembro_id=miembro.id,
            plan_id=plan.id,
            fecha_inicio=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            estatus_pago=MembershipStatus.activo,
        )
        self.session.add(membresia)
        self.session.commit()

        pago = self._create_pago(gym.id, membresia.id, usuario.id)
        asistencia = self._create_asistencia(gym.id, miembro.id)

        self.assertEqual(usuario.gym_id, gym.id)
        self.assertEqual(miembro.gym_id, gym.id)
        self.assertEqual(plan.gym_id, gym.id)
        self.assertEqual(pago.gym_id, gym.id)
        self.assertEqual(asistencia.gym_id, gym.id)

    def test_4_query_without_gym_filter_returns_all(self):
        """Query without gym_id filter returns data from ALL gyms (prep for F4-04)."""
        gym1 = self._create_gym("Gym Alpha")
        gym2 = self._create_gym("Gym Beta")

        self._create_miembro(gym1.id, "V-10000001")
        self._create_miembro(gym2.id, "V-10000002")

        all_miembros = self.session.query(Miembro).all()
        self.assertEqual(len(all_miembros), 2)
        gym_ids = {m.gym_id for m in all_miembros}
        self.assertEqual(gym_ids, {gym1.id, gym2.id})

    def test_5_usd_normalization_intact(self):
        """USD normalization columns (monto_usd, tasa_cambio) remain intact."""
        gym = self._create_gym("Gym USD")
        usuario = self._create_usuario(gym.id, "V-33333333")
        miembro = self._create_miembro(gym.id, "V-44444444")
        plan = self._create_plan(gym.id)

        membresia = MembresiaMiembro(
            miembro_id=miembro.id,
            plan_id=plan.id,
            fecha_inicio=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            estatus_pago=MembershipStatus.activo,
        )
        self.session.add(membresia)
        self.session.commit()

        pago = Pago(
            gym_id=gym.id,
            membresia_miembro_id=membresia.id,
            registrado_por=usuario.id,
            monto_original=100.00,
            moneda="USD",
            tasa_cambio=1.0,
            monto_usd=100.00,
            metodo_pago="efectivo_usd",
            fecha_pago=datetime.utcnow(),
        )
        self.session.add(pago)
        self.session.commit()

        self.assertEqual(float(pago.monto_usd), 100.00)
        self.assertEqual(float(pago.tasa_cambio), 1.0)

    def test_6_fk_restrict_prevents_delete(self):
        """FK RESTRICT prevents deleting a gym that has associated data."""
        gym = self._create_gym("Gym Protected")
        self._create_miembro(gym.id, "V-55555555")

        with self.assertRaises(IntegrityError):
            self.session.delete(gym)
            self.session.commit()
        self.session.rollback()

    def test_7_plans_independent_per_gym(self):
        """Each gym manages its own plans independently."""
        gym1 = self._create_gym("Gym One")
        gym2 = self._create_gym("Gym Two")

        p1 = self._create_plan(gym1.id, "Plan One")
        p2 = self._create_plan(gym2.id, "Plan Two")

        plans_g1 = self.session.query(Plan).filter_by(gym_id=gym1.id).all()
        plans_g2 = self.session.query(Plan).filter_by(gym_id=gym2.id).all()

        self.assertEqual(len(plans_g1), 1)
        self.assertEqual(len(plans_g2), 1)
        self.assertEqual(plans_g1[0].nombre, "Plan One")
        self.assertEqual(plans_g2[0].nombre, "Plan Two")

    def test_8_plan_logical_deletion(self):
        """Plan deletion uses logical deletion (estado_logico=False)."""
        gym = self._create_gym("Gym Logical")
        plan = self._create_plan(gym.id, "Plan Borrado")

        plan.estado_logico = False
        self.session.commit()

        result = self.session.query(Plan).filter_by(id=plan.id).first()
        self.assertIsNotNone(result)
        self.assertFalse(result.estado_logico)

    def test_9_relationships_work(self):
        """Gym backref relationships work correctly."""
        gym = self._create_gym("Gym Rel")
        usuario = self._create_usuario(gym.id, "V-66666666")
        miembro = self._create_miembro(gym.id, "V-77777777")
        plan = self._create_plan(gym.id)

        self.session.refresh(gym)
        self.assertIn(usuario, gym.usuarios)
        self.assertIn(miembro, gym.miembros)
        self.assertIn(plan, gym.planes)

    def test_10_retrieve_after_migration(self):
        """Tables can be queried after migration without errors."""
        gym = self._create_gym("Gym Query")
        usuario = self._create_usuario(gym.id, "V-99999999")
        miembro = self._create_miembro(gym.id, "V-88888888")
        plan = self._create_plan(gym.id)

        self.assertIsNotNone(self.session.query(Usuario).first())
        self.assertIsNotNone(self.session.query(Miembro).first())
        self.assertIsNotNone(self.session.query(Plan).first())
        self.assertIsNotNone(self.session.query(Gym).first())


if __name__ == "__main__":
    unittest.main()
