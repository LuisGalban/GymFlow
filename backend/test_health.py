import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app


class TestHealthEndpoint(unittest.TestCase):

    def test_1_health_returns_200(self):
        client = TestClient(app)
        resp = client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)

    def test_2_health_returns_status_ok(self):
        client = TestClient(app)
        resp = client.get("/api/v1/health")
        data = resp.json()
        self.assertEqual(data["status"], "ok")

    def test_3_health_returns_database_connected(self):
        client = TestClient(app)
        resp = client.get("/api/v1/health")
        data = resp.json()
        self.assertEqual(data["database"], "connected")

    def test_4_health_has_timestamp(self):
        client = TestClient(app)
        resp = client.get("/api/v1/health")
        data = resp.json()
        self.assertIn("timestamp", data)
        self.assertIsNotNone(data["timestamp"])

    def test_5_health_no_auth_required(self):
        client = TestClient(app)
        resp = client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("access_token", resp.cookies)
        self.assertNotIn("gymflow_token", resp.cookies)


if __name__ == "__main__":
    unittest.main()
