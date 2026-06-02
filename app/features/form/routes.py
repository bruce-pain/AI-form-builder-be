"""Form routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies.security import get_current_user
from app.features.auth.models import User
from app.features.form import schemas
from app.features.form.service import FormService

form_router = APIRouter(prefix="/forms", tags=["Forms"])


@form_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.FormResponse,
    summary="Create a new form",
    description="Create a new form for the authenticated user",
)
def create_form(
    schema: schemas.FormCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = FormService(db=db)
    form = service.create(schema=schema, user_id=current_user.id)
    data = schemas.FormResponseData.model_validate(form)
    return schemas.FormResponse(
        status_code=status.HTTP_201_CREATED,
        message="Form created successfully",
        data=data,
    )


@form_router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FormListResponse,
    summary="List user forms",
    description="Get all forms created by the authenticated user",
)
def list_user_forms(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = FormService(db=db)
    forms = service.list_user_forms(user_id=current_user.id)
    data = [schemas.FormListResponseData.model_validate(f) for f in forms]
    return schemas.FormListResponse(
        status_code=status.HTTP_200_OK,
        message="Forms retrieved successfully",
        data=data,
    )


@form_router.patch(
    path="/{form_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FormResponse,
    summary="Update a form",
    description="Update a single form belonging to the authenticated user",
)
def update_form(
    form_id: str,
    schema: schemas.FormUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = FormService(db=db)
    form = service.update_form(
        user_id=current_user.id,
        form_id=form_id,
        schema=schema,
    )
    data = schemas.FormResponseData.model_validate(form)
    return schemas.FormResponse(
        status_code=status.HTTP_200_OK,
        message="Form updated successfully",
        data=data,
    )


@form_router.delete(
    path="/{form_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FormResponse,
    summary="Delete a form",
    description="Delete a single form belonging to the authenticated user",
)
def delete_form(
    form_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = FormService(db=db)
    form = service.delete_form(user_id=current_user.id, form_id=form_id)
    data = schemas.FormResponseData.model_validate(form)
    return schemas.FormResponse(
        status_code=status.HTTP_200_OK,
        message="Form deleted successfully",
        data=data,
    )


@form_router.get(
    path="/{form_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FormResponse,
    summary="Get a form",
    description="Get a single form belonging to the authenticated user",
)
def get_form(
    form_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = FormService(db=db)
    form = service.get_user_form(user_id=current_user.id, form_id=form_id)
    data = schemas.FormResponseData.model_validate(form)
    return schemas.FormResponse(
        status_code=status.HTTP_200_OK,
        message="Form retrieved successfully",
        data=data,
    )


@form_router.get(
    path="/public/{form_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FormResponse,
    summary="Get a public form",
    description="Get a single published form (no authentication required)",
)
def get_public_form(
    form_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    service = FormService(db=db)
    form = service.get_public_form(form_id=form_id)
    data = schemas.FormResponseData.model_validate(form)
    return schemas.FormResponse(
        status_code=status.HTTP_200_OK,
        message="Form retrieved successfully",
        data=data,
    )
