
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


class TestExerciseEvaluationAPI(unittest.TestCase):
    @patch("backend.app.api.routes.learning.evaluate_exercise")
    def test_evaluate_exercise_returns_200(self, mock_evaluate):
        mock_evaluate.return_value = {
            "is_correct": True,
            "score": 100,
            "feedback": "Correct solution.",
            "explanation": "The variable is defined before use.",
            "hint": "Try changing the value of x.",
            "strengths": ["Correct variable assignment"],
            "improvements": [],
        }

        response = client.post(
            "/api/v1/evaluate-exercise",
            json={
                "exercise": {
                    "title": "Define a variable",
                    "concept": "Variable assignment",
                    "difficulty": "beginner",
                    "instructions": "Define x and print it.",
                    "starter_code": "",
                    "expected_skills": ["Variable assignment"],
                },
                "language": "python",
                "answer": "x = 5\nprint(x)",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["score"], 100)
        self.assertTrue(response.json()["is_correct"])

    def test_blank_answer_is_rejected(self):
        response = client.post(
            "/api/v1/evaluate-exercise",
            json={
                "exercise": {
                    "title": "Define a variable",
                    "concept": "Variable assignment",
                    "difficulty": "beginner",
                    "instructions": "Define x and print it.",
                    "starter_code": "",
                    "expected_skills": ["Variable assignment"],
                },
                "language": "python",
                "answer": "   ",
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
