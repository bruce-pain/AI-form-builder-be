"""LLM routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies.security import get_current_user
from app.core.groq import client as groq_client
from app.core.limiter import limiter
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
@limiter.limit("10/minute")
async def generate_questions(
    request: Request,
    schema: schemas.LLMRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = LLMService(
        groq_client=groq_client,
        db=db,
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
