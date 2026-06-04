"""Response service"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.features.form.repository import FormRepository
from app.features.response import schemas
from app.features.response.models import Response
from app.features.response.repository import ResponseRepository


class ResponseService:
    def __init__(self, db: Session):
        self.repository = ResponseRepository(db)
        self.form_repository = FormRepository(db)

    def submit(self, form_id: str, schema: schemas.ResponseCreateRequest) -> Response:
        logger.info("Submitting response for form: %s", form_id)

        form = self.form_repository.get_public_form(form_id)
        if not form:
            logger.warning("Form not found or not published | id: %s", form_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found or not published",
            )

        response = Response(form_id=form_id, answers=schema.answers)
        created = self.repository.create(response)
        logger.info(
            "Response submitted successfully | id: %s | form: %s", created.id, form_id
        )
        return created

    def get_form_responses(self, form_id: str, user_id: str) -> list[Response]:
        logger.info("Fetching responses for form: %s | user: %s", form_id, user_id)
        form = self.form_repository.get_user_form(user_id, form_id)
        if not form:
            logger.warning("Form not found | id: %s | user: %s", form_id, user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found",
            )
        responses = self.repository.get_by_form(form.id)
        logger.info("Retrieved %d responses for form: %s", len(responses), form.id)
        return responses

    def get_form_response(
        self, form_id: str, response_id: str, user_id: str
    ) -> Response:
        logger.info(
            "Fetching response | id: %s | form: %s | user: %s",
            response_id,
            form_id,
            user_id,
        )
        form = self.form_repository.get_user_form(user_id, form_id)
        if not form:
            logger.warning("Form not found | id: %s | user: %s", form_id, user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found",
            )
        response = self.repository.get_form_response(form.id, response_id)
        if not response:
            logger.warning(
                "Response not found | id: %s | form: %s", response_id, form.id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found",
            )
        logger.info(
            "Response retrieved successfully | id: %s | form: %s", response_id, form.id
        )
        return response
