
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


class TestLearningAPI(unittest.TestCase):
    @patch("backend.app.api.routes.learning.generate_exercises")
    def test_generate_exercises_returns_200(self, mock_generate):
        mock_generate.return_value = {
            "exercises": [
                {
                    "title": "Define a variable",
                    "concept": "Variable definition",
                    "difficulty": "beginner",
                    "instructions": "Define x and print it.",
                    "starter_code": "",
                    "expected_skills": ["Variable assignment"],
                }
            ]
        }

        response = client.post(
            "/api/v1/generate-exercises",
            json={
                "language": "python",
                "code": "print(x)",
                "count": 1,
                "analysis": {
                    "summary": "x is undefined.",
                    "issues": [
                        {
                            "type": "Runtime Error",
                            "severity": "High",
                            "explanation": "x is used before it is defined.",
                        }
                    ],
                    "suggestions": ["Define x first."],
                },
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["exercises"]), 1)

    def test_blank_code_is_rejected(self):
        response = client.post(
            "/api/v1/generate-exercises",
            json={
                "language": "python",
                "code": "   ",
                "count": 1,
                "analysis": {
                    "summary": "No issues.",
                    "issues": [],
                    "suggestions": [],
                },
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
