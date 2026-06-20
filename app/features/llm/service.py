"""LLM service"""

import json
from typing import List

from fastapi import HTTPException, status
from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)
from groq.types.chat import ChatCompletionMessageParam
from pydantic import ValidationError

from app.core.logger import logger
from app.features.llm.groq_utils import SYSTEM_PROMPT, parse_message, run_inference
from app.features.llm.schemas import FormQuestionList


class LLMService:
    def generate(self, user_prompt: str) -> FormQuestionList:
        if not user_prompt:
            logger.warning("LLM generation attempted with empty prompt")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't send empty prompt",
            )

        logger.info("Generating form questions | prompt: %.80s", user_prompt)

        conversation: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        try:
            llm_response = run_inference(conversation)
        except APIConnectionError:
            logger.error("Groq API connection error")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM service unavailable",
            )
        except APITimeoutError:
            logger.error("Groq API request timed out")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="LLM request timed out",
            )
        except RateLimitError:
            logger.error("Groq API rate limit exceeded")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="LLM rate limit exceeded. Please try again later.",
            )
        except AuthenticationError:
            logger.error("Groq API authentication failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="LLM configuration error",
            )
        except APIStatusError as e:
            logger.error("Groq API error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM service error: {e}",
            )

        try:
            result = parse_message(llm_response)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error("Failed to parse LLM response: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid LLM response",
            )

        if not result:
            logger.error("LLM returned empty response")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating result",
            )

        logger.info(
            "Form questions generated successfully | questions: %d",
            len(result.questions),
        )

        return result
