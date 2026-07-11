import os
import sys
import unittest
from datetime import datetime, timedelta
from jose import jwt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Gym, Usuario, UserRole, GymSubscriptionStatus, PaymentCurrency
from app.auth.auth import crear_token_acceso, JWT_SECRET, JWT_ALGORITHM, obtener_usuario_actual, obtener_usuario_por_token
from fastapi import HTTPException
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/gymflow_db",
)

from app.main import app

client = TestClient(app)


class TestF403JwtGymId(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_login_response_contains_gym_id(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"correo": "admin@gymflow.com", "password": "admin123"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("gym_id", data)
        self.assertIsInstance(data["gym_id"], int)
        self.assertEqual(data["gym_id"], 1)

    def test_jwt_payload_contains_gym_id(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"correo": "admin@gymflow.com", "password": "admin123"},
        )
        self.assertEqual(response.status_code, 200)
        token = response.json()["access_token"]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        self.assertIn("gym_id", payload)
        self.assertEqual(payload["gym_id"], 1)

    def test_authenticated_endpoint_exposes_gym_id(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"correo": "admin@gymflow.com", "password": "admin123"},
        )
        token = response.json()["access_token"]
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me_response.status_code, 200)
        user_data = me_response.json()
        self.assertIn("id", user_data)
        self.assertEqual(user_data["correo"], "admin@gymflow.com")

    def test_legacy_token_without_gym_id_is_rejected(self):
        legacy_token = jwt.encode(
            {"sub": "admin@gymflow.com", "rol": "admin", "exp": datetime.utcnow() + timedelta(minutes=30)},
            JWT_SECRET,
            algorithm=JWT_ALGORITHM,
        )
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {legacy_token}"},
        )
        self.assertEqual(response.status_code, 401)

    def test_obtener_usuario_por_token_rejects_legacy(self):
        legacy_token = jwt.encode(
            {"sub": "admin@gymflow.com", "rol": "admin", "exp": datetime.utcnow() + timedelta(minutes=30)},
            JWT_SECRET,
            algorithm=JWT_ALGORITHM,
        )
        with self.assertRaises(HTTPException) as ctx:
            obtener_usuario_por_token(legacy_token, self.session)
        self.assertEqual(ctx.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
