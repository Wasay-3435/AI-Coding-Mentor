
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.utils.exceptions import AIServiceError, AIResponseError


client = TestClient(app)


class TestCodeAnalysisAPI(unittest.TestCase):
    @patch("backend.app.api.routes.code.analyze_code")
    def test_successful_analysis_returns_200(self, mock_analyze):
        mock_analyze.return_value = {
            "summary": "The code prints 2.",
            "issues": [],
            "suggestions": [],
        }

        response = client.post(
            "/api/v1/analyze-code",
            json={
                "language": "python",
                "code": "print(1 + 1)",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"], "The code prints 2.")

    @patch("backend.app.api.routes.code.analyze_code")
    def test_invalid_ai_response_returns_502(self, mock_analyze):
        mock_analyze.side_effect = AIResponseError(
            "The AI returned an invalid response. Please try again."
        )

        response = client.post(
            "/api/v1/analyze-code",
            json={
                "language": "python",
                "code": "print(1 + 1)",
            },
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["error"], "Invalid AI response")

    @patch("backend.app.api.routes.code.analyze_code")
    def test_ai_service_error_returns_503(self, mock_analyze):
        mock_analyze.side_effect = AIServiceError(
            "The AI service is temporarily unavailable."
        )

        response = client.post(
            "/api/v1/analyze-code",
            json={
                "language": "python",
                "code": "print(1 + 1)",
            },
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"], "AI service unavailable")


if __name__ == "__main__":
    unittest.main()
