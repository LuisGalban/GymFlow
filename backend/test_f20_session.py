import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import Usuario, UserRole
from app.auth.auth import obtener_password_hash
from app.main import app

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/gymflow_db")
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestF20SessionRestore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = TestingSessionLocal()
        cls.clean_up_test_data(cls.db)

        pwd = obtener_password_hash("test123")
        cls.worker = Usuario(
            cedula="V-F2000001", nombre="Worker F20",
            correo="workerf20@gymflow.com",
            password_hash=pwd, rol=UserRole.worker.value, estado_logico=True
        )
        cls.db.add(cls.worker)
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.clean_up_test_data(cls.db)
        cls.db.close()

    @classmethod
    def clean_up_test_data(cls, session):
        session.query(Usuario).filter(Usuario.cedula == "V-F2000001").delete(synchronize_session=False)
        session.commit()

    def _login_and_get_cookie(self, client: TestClient) -> str:
        resp = client.post("/api/v1/auth/login", json={
            "correo": "workerf20@gymflow.com",
            "password": "test123"
        })
        self.assertEqual(resp.status_code, 200)
        return resp.cookies.get("gymflow_token")

    def test_1_login_sets_httponly_cookie(self):
        """RED->GREEN: Login response must include gymflow_token cookie"""
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "correo": "workerf20@gymflow.com",
            "password": "test123"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn("gymflow_token", resp.cookies,
                      "HttpOnly cookie 'gymflow_token' not set in response")

    def test_2_session_restore_with_valid_cookie(self):
        """RED->GREEN: GET /api/v1/auth/session with valid cookie returns user + access_token"""
        client = TestClient(app)
        gymflow_cookie = self._login_and_get_cookie(client)
        self.assertIsNotNone(gymflow_cookie)

        resp = client.get("/api/v1/auth/session")
        self.assertEqual(resp.status_code, 200,
                         f"Session returned {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        self.assertIn("user", data)
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["correo"], "workerf20@gymflow.com")

    def test_3_session_without_cookie_returns_401(self):
        """RED->GREEN: GET /api/v1/auth/session without cookie returns 401"""
        client = TestClient(app)
        resp = client.get("/api/v1/auth/session")
        self.assertEqual(resp.status_code, 401,
                         f"Expected 401, got {resp.status_code}")

    def test_4_session_with_invalid_cookie_returns_401(self):
        """RED->GREEN: GET /api/v1/auth/session with invalid cookie returns 401"""
        client = TestClient(app)
        client.cookies.set("gymflow_token", "invalid_token_abc123")
        resp = client.get("/api/v1/auth/session")
        self.assertEqual(resp.status_code, 401,
                         f"Expected 401, got {resp.status_code}")

    def test_5_login_flow_no_infinite_loop(self):
        """GREEN: Full login flow does not cause redirect loop (regression test for F-20)"""
        client = TestClient(app)
        # Step 1: Session without cookie -> 401 (simulates restoreSession with no session)
        no_session_resp = client.get("/api/v1/auth/session")
        self.assertEqual(no_session_resp.status_code, 401)

        # Step 2: Login succeeds
        login_resp = client.post("/api/v1/auth/login", json={
            "correo": "workerf20@gymflow.com",
            "password": "test123"
        })
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn("gymflow_token", login_resp.cookies)

        # Step 3: Session restore with the cookie -> 200 (simulates restoreSession after login)
        session_resp = client.get("/api/v1/auth/session")
        self.assertEqual(session_resp.status_code, 200,
                         "Session restore should succeed with valid cookie")
        data = session_resp.json()
        self.assertIn("user", data)
        self.assertIn("access_token", data)

        # Step 4: GET /me with the access_token from session -> 200
        token = data["access_token"]
        me_resp = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        self.assertEqual(me_resp.status_code, 200,
                         "GET /me should succeed with token from session restore")


if __name__ == "__main__":
    unittest.main()
