
import unittest

from backend.app.models.code import CodeAnalysisResponse
from backend.app.models.learning import (
    ExerciseEvaluationResponse,
    ExerciseGenerationResponse,
    LearningSessionReportResponse,
    PracticeExercise,
)
from backend.app.services.session_service import (
    SessionNotFoundError,
    create_session,
    get_session_report,
    record_analysis,
    record_evaluation,
    record_generated_exercises,
)


class TestSessionService(unittest.TestCase):
    def setUp(self):
        self.session = create_session()
        self.session_id = self.session["session_id"]

    def test_create_session_returns_unique_id(self):
        another_session = create_session()

        self.assertTrue(self.session_id)
        self.assertNotEqual(
            self.session_id,
            another_session["session_id"],
        )

    def test_empty_session_report(self):
        report = get_session_report(self.session_id)

        self.assertIsInstance(report, LearningSessionReportResponse)
        self.assertEqual(report.total_analyses, 0)
        self.assertEqual(report.total_exercises_generated, 0)
        self.assertEqual(report.total_exercises_attempted, 0)
        self.assertEqual(report.average_score, 0)
        self.assertEqual(report.correct_answers, 0)
        self.assertTrue(report.recommendations)

    def test_report_tracks_analysis_exercise_and_evaluation(self):
        analysis = CodeAnalysisResponse(
            summary="The variable x is undefined.",
            issues=[
                {
                    "type": "Runtime Error",
                    "severity": "High",
                    "explanation": "x is used before it is defined.",
                }
            ],
            suggestions=["Define x before using it."],
        )

        exercise = PracticeExercise(
            title="Define a variable",
            concept="Variable assignment",
            difficulty="beginner",
            instructions="Define x and print its value.",
            starter_code="",
            expected_skills=["Variable assignment"],
        )

        exercises = ExerciseGenerationResponse(
            exercises=[exercise],
        )

        evaluation = ExerciseEvaluationResponse(
            is_correct=False,
            score=60,
            feedback="Partially correct.",
            explanation="The answer misses a requirement.",
            hint="Review the exercise instructions.",
            strengths=["A variable was created."],
            improvements=["Print the variable's value."],
        )

        record_analysis(self.session_id, analysis)
        record_generated_exercises(self.session_id, exercises)
        record_evaluation(
            self.session_id,
            evaluation,
            exercise.concept,
        )

        report = get_session_report(self.session_id)

        self.assertEqual(report.total_analyses, 1)
        self.assertEqual(report.total_exercises_generated, 1)
        self.assertEqual(report.total_exercises_attempted, 1)
        self.assertEqual(report.average_score, 60)
        self.assertEqual(report.correct_answers, 0)
        self.assertIn(
            "Variable assignment",
            report.concepts_to_practice,
        )

    def test_unknown_session_raises_error(self):
        with self.assertRaises(SessionNotFoundError):
            get_session_report("unknown-session-id")


if __name__ == "__main__":
    unittest.main()
