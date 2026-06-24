"""LLM routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis

from app.core.dependencies.security import get_current_user
from app.core.groq import client as groq_client
from app.core.redis import get_redis_client
from app.features.auth.models import User
from app.features.llm import schemas
from app.features.llm.service import LLMService

llm_router = APIRouter(prefix="/llm", tags=["LLM"])


@llm_router.post(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LLMResponse,
    summary="Generate form questions",
    description="Generate or modify a list of form questions using an LLM based on a user prompt, with conversation memory",
)
async def generate_questions(
    schema: schemas.LLMRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    redis: Annotated[Redis, Depends(get_redis_client)],
):
    service = LLMService(
        groq_client=groq_client,
        redis_client=redis,
        user_id=current_user.id,
    )
    conversation_id, result = await service.generate(
        user_prompt=schema.prompt,
        conversation_id=schema.conversation_id,
        current_state=schema.current_state,
    )
    return schemas.LLMResponse(
        status_code=status.HTTP_200_OK,
        message="Form questions generated successfully",
        data=result,
        conversation_id=conversation_id,
    )
