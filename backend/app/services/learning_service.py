
import logging

from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError
from langchain_google_genai.chat_models import GoogleAPIError

from backend.app.chains.exercise_chain import exercise_chain
from backend.app.models.learning import (
    ExerciseGenerationRequest,
    ExerciseGenerationResponse,
)
from backend.app.utils.exceptions import AIResponseError, AIServiceError


logger = logging.getLogger(__name__)


def generate_exercises(
    request: ExerciseGenerationRequest,
) -> ExerciseGenerationResponse:
    try:
        result = exercise_chain.invoke(
            {
                "language": request.language,
                "code": request.code,
                "count": request.count,
                "analysis": request.analysis.model_dump_json(),
            }
        )

        if len(result.exercises) != request.count:
            raise AIResponseError(
                "The AI generated an unexpected number of exercises. "
                "Please try again."
            )

        return result

    except AIResponseError:
        raise

    except (ValidationError, OutputParserException) as exc:
        logger.warning(
            "Exercise generation returned an invalid response",
            exc_info=True,
        )
        raise AIResponseError(
            "The AI returned an invalid exercise response. Please try again."
        ) from exc

    except GoogleAPIError as exc:
        logger.warning(
            "Google AI request failed during exercise generation",
            exc_info=True,
        )
        raise AIServiceError(
            "The AI service is temporarily unavailable. Please try again later."
        ) from exc

    except Exception:
        logger.exception("Unexpected exercise generation failure")
        raise
