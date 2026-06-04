"""Response routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies.security import get_current_user
from app.features.auth.models import User
from app.features.response import schemas
from app.features.response.service import ResponseService

response_router = APIRouter(prefix="/forms", tags=["Responses"])


@response_router.post(
    path="/{form_id}/responses",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.FormResponseResponse,
    summary="Submit a response",
    description="Submit a response to a public form (no authentication required)",
)
def submit_response(
    form_id: str,
    schema: schemas.FormResponseCreateRequest,
    db: Annotated[Session, Depends(get_db)],
):
    service = ResponseService(db=db)
    response = service.submit(form_id=form_id, schema=schema)
    data = schemas.FormResponseData.model_validate(response)
    return schemas.FormResponseResponse(
        status_code=status.HTTP_201_CREATED,
        message="Response submitted successfully",
        data=data,
    )


@response_router.get(
    path="/{form_id}/responses",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FormResponseListResponse,
    summary="List form responses",
    description="Get all responses for a form (authentication required)",
)
def list_form_responses(
    form_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = ResponseService(db=db)
    responses = service.get_form_responses(form_id=form_id, user_id=current_user.id)
    data = [schemas.FormResponseData.model_validate(r) for r in responses]
    return schemas.FormResponseListResponse(
        status_code=status.HTTP_200_OK,
        message="Responses retrieved successfully",
        data=data,
    )


@response_router.get(
    path="/{form_id}/responses/{response_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FormResponseResponse,
    summary="Get a response",
    description="Get a single response for a form (authentication required)",
)
def get_form_response(
    form_id: str,
    response_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = ResponseService(db=db)
    response = service.get_form_response(
        form_id=form_id, response_id=response_id, user_id=current_user.id
    )
    data = schemas.FormResponseData.model_validate(response)
    return schemas.FormResponseResponse(
        status_code=status.HTTP_200_OK,
        message="Response retrieved successfully",
        data=data,
    )
