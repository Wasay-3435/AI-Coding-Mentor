
import unittest
from unittest.mock import patch

from backend.app.models.code import CodeAnalysisResponse
from backend.app.models.learning import (
    ExerciseGenerationRequest,
    ExerciseGenerationResponse,
    PracticeExercise,
)
from backend.app.services.learning_service import generate_exercises
from backend.app.utils.exceptions import AIResponseError


class TestGenerateExercises(unittest.TestCase):
    def setUp(self):
        self.request = ExerciseGenerationRequest(
            language="python",
            code="print(x)",
            analysis=CodeAnalysisResponse(
                summary="The variable x is undefined.",
                issues=[
                    {
                        "type": "Runtime Error",
                        "severity": "High",
                        "explanation": "x is used without being defined.",
                    }
                ],
                suggestions=["Define x before using it."],
            ),
            count=1,
        )

        self.exercise = PracticeExercise(
            title="Define a variable",
            concept="Variable definition",
            difficulty="beginner",
            instructions="Define a variable named x and print its value.",
            starter_code="",
            expected_skills=["Variable assignment", "Printing values"],
        )

    @patch("backend.app.services.learning_service.exercise_chain")
    def test_successful_generation(self, mock_chain):
        expected = ExerciseGenerationResponse(
            exercises=[self.exercise],
        )
        mock_chain.invoke.return_value = expected

        result = generate_exercises(self.request)

        self.assertEqual(result, expected)
        mock_chain.invoke.assert_called_once()

    @patch("backend.app.services.learning_service.exercise_chain")
    def test_wrong_exercise_count_raises_response_error(self, mock_chain):
        mock_chain.invoke.return_value = ExerciseGenerationResponse(
            exercises=[self.exercise, self.exercise],
        )

        with self.assertRaises(AIResponseError):
            generate_exercises(self.request)


if __name__ == "__main__":
    unittest.main()
