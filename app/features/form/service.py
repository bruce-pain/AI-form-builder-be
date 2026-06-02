"""Form service"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.features.form import schemas
from app.features.form.models import Form
from app.features.form.repository import FormRepository


class FormService:
    def __init__(self, db: Session):
        self.repository = FormRepository(db)

    def create(self, schema: schemas.FormCreateRequest, user_id: str) -> Form:
        logger.info("Creating form for user: %s | title: %s", user_id, schema.title)
        form = Form(
            title=schema.title,
            description=schema.description,
            questions=schema.questions,
            user_id=user_id,
        )
        created = self.repository.create(form)
        logger.info(
            "Form created successfully | id: %s | user: %s", created.id, user_id
        )
        return created

    def list_user_forms(self, user_id: str) -> list[Form]:
        logger.info("Fetching all forms for user: %s", user_id)
        forms = self.repository.get_by_user(user_id)
        logger.info("Retrieved %d forms for user: %s", len(forms), user_id)
        return forms

    def get_user_form(self, user_id: str, form_id: str) -> Form:
        logger.info("Fetching form | id: %s | user: %s", form_id, user_id)
        form = self.repository.get_user_form(user_id, form_id)
        if not form:
            logger.warning("Form not found | id: %s | user: %s", form_id, user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found",
            )
        logger.info("Form retrieved successfully | id: %s | user: %s", form_id, user_id)
        return form

    def update_form(
        self, user_id: str, form_id: str, schema: schemas.FormUpdateRequest
    ) -> Form:
        logger.info("Updating form | id: %s | user: %s", form_id, user_id)
        form = self.get_user_form(user_id, form_id)
        update_data = schema.model_dump(exclude_none=True)
        if not update_data:
            logger.warning("No fields to update | id: %s | user: %s", form_id, user_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )
        logger.info(
            "Form update fields: %s | id: %s | user: %s",
            list(update_data.keys()),
            form_id,
            user_id,
        )
        for key, value in update_data.items():
            setattr(form, key, value)
        self.repository.db.commit()
        self.repository.db.refresh(form)
        logger.info("Form updated successfully | id: %s | user: %s", form_id, user_id)
        return form

    def delete_form(self, user_id: str, form_id: str) -> None:
        logger.info("Deleting form | id: %s | user: %s", form_id, user_id)
        form = self.repository.get_user_form(user_id, form_id)
        if form:
            self.repository.delete(form.id)
            logger.info(
                "Form deleted successfully | id: %s | user: %s", form_id, user_id
            )
        else:
            logger.info(
                "Form not found, skipping | id: %s | user: %s", form_id, user_id
            )

    def get_public_form(self, form_id: str) -> Form:
        logger.info("Fetching public form | id: %s", form_id)
        form = self.repository.get_public_form(form_id)
        if not form:
            logger.warning("Public form not found | id: %s", form_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found or not published",
            )
        logger.info("Public form retrieved successfully | id: %s", form_id)
        return form
