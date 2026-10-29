
import unittest
from unittest.mock import patch

from backend.app.models.learning import (
    ExerciseEvaluationResponse,
    ExerciseSubmissionRequest,
    PracticeExercise,
)
from backend.app.services.evaluation_service import evaluate_exercise
from backend.app.utils.exceptions import AIResponseError


class TestEvaluateExercise(unittest.TestCase):
    def setUp(self):
        self.request = ExerciseSubmissionRequest(
            exercise=PracticeExercise(
                title="Define a variable",
                concept="Variable assignment",
                difficulty="beginner",
                instructions="Define x and print it.",
                starter_code="",
                expected_skills=["Variable assignment"],
            ),
            language="python",
            answer='x = 5\nprint(x)',
        )

    @patch("backend.app.services.evaluation_service.evaluation_chain")
    def test_successful_evaluation(self, mock_chain):
        expected = ExerciseEvaluationResponse(
            is_correct=True,
            score=100,
            feedback="Correct solution.",
            explanation="The variable is defined before use.",
            hint="Try changing the value of x.",
            strengths=["Correct assignment", "Correct output"],
            improvements=[],
        )
        mock_chain.invoke.return_value = expected

        result = evaluate_exercise(self.request)

        self.assertEqual(result, expected)
        mock_chain.invoke.assert_called_once()

    @patch("backend.app.services.evaluation_service.evaluation_chain")
    def test_inconsistent_correctness_and_score(self, mock_chain):
        mock_chain.invoke.return_value = ExerciseEvaluationResponse(
            is_correct=True,
            score=60,
            feedback="Partially correct.",
            explanation="The answer misses a requirement.",
            hint="Review the instructions.",
            strengths=["Uses a variable"],
            improvements=["Complete the missing requirement"],
        )

        with self.assertRaises(AIResponseError):
            evaluate_exercise(self.request)


if __name__ == "__main__":
    unittest.main()
