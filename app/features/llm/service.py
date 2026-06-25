"""LLM service"""

import json
from typing import List, Optional

from fastapi import HTTPException, status
from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    AsyncGroq,
    RateLimitError,
)
from groq.types.chat import ChatCompletionMessageParam
from pydantic import ValidationError
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from app.core.logger import logger
from app.features.llm.groq_utils import SYSTEM_PROMPT, parse_message, run_inference
from app.features.llm.models import ConversationPrompt
from app.features.llm.repository import ConversationRepository
from app.features.llm.schemas import FormQuestionList


class LLMService:
    def __init__(self, groq_client: AsyncGroq, db: Session, user_id: str) -> None:
        self.groq_client = groq_client
        self.repository = ConversationRepository(db)
        self.user_id = user_id

    async def generate(
        self,
        user_prompt: str,
        conversation_id: Optional[str] = None,
        current_state: Optional[FormQuestionList] = None,
    ) -> tuple[str, FormQuestionList]:
        if not user_prompt:
            logger.warning("LLM generation attempted with empty prompt")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't send empty prompt",
            )

        if not conversation_id:
            conversation_id = str(uuid7())

        logger.info(
            "Generating form questions | conv: %s | prompt: %.80s",
            conversation_id,
            user_prompt,
        )

        prior_prompts = self.repository.get_prompts(conversation_id)

        lines: List[str] = []
        if prior_prompts:
            lines.append("Prior instructions (already applied):")
            for i, p in enumerate(prior_prompts, 1):
                lines.append(f'{i}. "{p}"')
            lines.append("")

        lines.append(f"Current form state: {current_state.model_dump_json() if current_state else 'None'}")
        lines.append("")
        lines.append(f"New instruction: {user_prompt}")

        user_message = "\n".join(lines)

        conversation: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        try:
            llm_response = await run_inference(self.groq_client, conversation)
        except APITimeoutError:
            logger.error("Groq API request timed out")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="LLM request timed out",
            )
        except APIConnectionError:
            logger.error("Groq API connection error")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM service unavailable",
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

        self.repository.create(
            ConversationPrompt(conversation_id=conversation_id, prompt=user_prompt)
        )

        logger.info(
            "Form questions generated successfully | conv: %s | questions: %d",
            conversation_id,
            len(result.questions),
        )

        return conversation_id, result
