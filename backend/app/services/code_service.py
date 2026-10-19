
import logging

from pydantic import ValidationError
from langchain_core.exceptions import OutputParserException
from langchain_google_genai.chat_models import (
    GoogleAPIError,
    GoogleAuthenticationError,
    GoogleInvalidRequestError,
    GoogleModelNotFoundError,
    GooglePermissionDeniedError,
    GoogleRateLimitError,
    ServerError,
)

from backend.app.models.code import CodeRequest
from backend.app.chains.code_analysis_chain import code_analysis_chain
from backend.app.utils.exceptions import AIServiceError, AIResponseError


logger = logging.getLogger(__name__)


def analyze_code(request: CodeRequest):
    try:
        return code_analysis_chain.invoke(
            {
                "language": request.language,
                "code": request.code,
            }
        )

    except (ValidationError, OutputParserException) as exc:
        logger.warning(
            "AI response failed structured-output validation",
            exc_info=True,
        )
        raise AIResponseError(
            "The AI returned an invalid response. Please try again."
        ) from exc

    except GoogleRateLimitError as exc:
        logger.warning("AI provider rate limit reached")
        raise AIServiceError(
            "The AI service is temporarily busy. Please try again later."
        ) from exc

    except (GoogleAuthenticationError, GooglePermissionDeniedError) as exc:
        logger.exception("AI provider authentication or permission failure")
        raise AIServiceError(
            "The AI service is temporarily unavailable."
        ) from exc

    except GoogleModelNotFoundError as exc:
        logger.exception("Configured AI model was not found")
        raise AIServiceError(
            "The AI service is temporarily unavailable."
        ) from exc

    except GoogleInvalidRequestError as exc:
        logger.exception("AI provider rejected the request")
        raise AIServiceError(
            "The AI service could not process this request."
        ) from exc

    except ServerError as exc:
        logger.exception("AI provider server failure")
        raise AIServiceError(
            "The AI service is temporarily unavailable. Please try again later."
        ) from exc

    except GoogleAPIError as exc:
        logger.exception("Unexpected Google AI API failure")
        raise AIServiceError(
            "The AI service is temporarily unavailable."
        ) from exc

    except Exception:
        logger.exception("Unexpected internal code analysis failure")
        raise
