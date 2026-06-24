"""LLM routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies.security import get_current_user
from app.core.groq import client as groq_client
from app.features.auth.models import User
from app.features.llm import schemas
from app.features.llm.service import LLMService

llm_router = APIRouter(prefix="/llm", tags=["LLM"])


@llm_router.post(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LLMResponse,
    summary="Generate form questions",
    description="Generate a list of form questions using an LLM based on a user prompt",
)
def generate_questions(
    schema: schemas.LLMRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = LLMService(groq_client)
    result = service.generate(user_prompt=schema.prompt)
    return schemas.LLMResponse(
        status_code=status.HTTP_200_OK,
        message="Form questions generated successfully",
        data=result,
    )
