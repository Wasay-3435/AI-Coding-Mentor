
import unittest
from unittest.mock import patch

from backend.app.models.code import CodeRequest
from backend.app.services.code_service import analyze_code
from backend.app.utils.exceptions import AIServiceError
from langchain_google_genai.chat_models import GoogleRateLimitError


class TestAnalyzeCode(unittest.TestCase):
    def setUp(self):
        self.request = CodeRequest(
            language="python",
            code="print(1 + 1)",
        )

    @patch("backend.app.services.code_service.code_analysis_chain")
    def test_successful_analysis_returns_result(self, mock_chain):
        expected_result = {
            "summary": "The code prints 2.",
            "issues": [],
            "suggestions": [],
        }
        mock_chain.invoke.return_value = expected_result

        result = analyze_code(self.request)

        self.assertEqual(result, expected_result)
        mock_chain.invoke.assert_called_once_with(
            {
                "language": "python",
                "code": "print(1 + 1)",
            }
        )

    @patch("backend.app.services.code_service.code_analysis_chain")
    def test_rate_limit_raises_ai_service_error(self, mock_chain):
        original_error = GoogleRateLimitError("Rate limit reached")
        mock_chain.invoke.side_effect = original_error

        with self.assertRaises(AIServiceError) as context:
            analyze_code(self.request)

        self.assertIn("temporarily busy", str(context.exception))
        self.assertIs(context.exception.__cause__, original_error)

    @patch("backend.app.services.code_service.code_analysis_chain")
    def test_unexpected_error_is_reraised(self, mock_chain):
        original_error = RuntimeError("Simulated internal failure")
        mock_chain.invoke.side_effect = original_error

        with self.assertRaises(RuntimeError) as context:
            analyze_code(self.request)

        self.assertIs(context.exception, original_error)


if __name__ == "__main__":
    unittest.main()
