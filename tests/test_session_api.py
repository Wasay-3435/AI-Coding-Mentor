
import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


class TestSessionAPI(unittest.TestCase):
    def test_create_session_returns_session_id(self):
        response = client.post("/api/v1/sessions")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["session_id"])

    def test_new_session_has_empty_report(self):
        create_response = client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]

        report_response = client.get(
            f"/api/v1/sessions/{session_id}/report"
        )

        self.assertEqual(report_response.status_code, 200)

        report = report_response.json()
        self.assertEqual(report["session_id"], session_id)
        self.assertEqual(report["total_analyses"], 0)
        self.assertEqual(report["total_exercises_generated"], 0)
        self.assertEqual(report["total_exercises_attempted"], 0)
        self.assertEqual(report["average_score"], 0)

    def test_unknown_session_returns_404(self):
        response = client.get(
            "/api/v1/sessions/unknown-session-id/report"
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
