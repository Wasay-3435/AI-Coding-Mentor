
import logging

from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError
from langchain_google_genai.chat_models import GoogleAPIError

from backend.app.chains.evaluation_chain import evaluation_chain
from backend.app.models.learning import (
    ExerciseEvaluationResponse,
    ExerciseSubmissionRequest,
)
from backend.app.utils.exceptions import AIResponseError, AIServiceError


logger = logging.getLogger(__name__)


def evaluate_exercise(
    request: ExerciseSubmissionRequest,
) -> ExerciseEvaluationResponse:
    try:
        result = evaluation_chain.invoke(
            {
                "language": request.language,
                "title": request.exercise.title,
                "concept": request.exercise.concept,
                "difficulty": request.exercise.difficulty,
                "instructions": request.exercise.instructions,
                "starter_code": request.exercise.starter_code,
                "expected_skills": ", ".join(
                    request.exercise.expected_skills
                ),
                "answer": request.answer,
            }
        )

        if result.is_correct and result.score < 90:
            logger.warning(
                "AI returned inconsistent correctness and score fields"
            )
            raise AIResponseError(
                "The AI returned an inconsistent evaluation. Please try again."
            )

        return result

    except AIResponseError:
        raise

    except (ValidationError, OutputParserException) as exc:
        logger.warning(
            "Exercise evaluation returned an invalid response",
            exc_info=True,
        )
        raise AIResponseError(
            "The AI returned an invalid evaluation. Please try again."
        ) from exc

    except GoogleAPIError as exc:
        logger.warning(
            "Google AI request failed during exercise evaluation",
            exc_info=True,
        )
        raise AIServiceError(
            "The AI service is temporarily unavailable. Please try again later."
        ) from exc

    except Exception:
        logger.exception("Unexpected exercise evaluation failure")
        raise
