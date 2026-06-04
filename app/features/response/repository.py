from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.base.repository import BaseRepository
from app.features.response.models import Response


class ResponseRepository(BaseRepository[Response]):
    """Repository for Response model operations."""

    def __init__(self, db: Session):
        super().__init__(Response, db)

    def get_by_form(self, form_id: str) -> List[Response]:
        """Get all responses for a given form.

        Args:
            form_id: The ID of the form whose responses to retrieve.

        Returns:
            A list of responses belonging to the given form.
        """
        return self.db.query(self.model).filter(self.model.form_id == form_id).all()

    def get_form_response(self, form_id: str, response_id: str) -> Optional[Response]:
        """Get a single response for a specific form.

        Args:
            form_id: The ID of the form the response belongs to.
            response_id: The ID of the response to retrieve.

        Returns:
            The response if found and belongs to the form, otherwise None.
        """
        return (
            self.db.query(self.model)
            .filter(
                self.model.id == response_id,
                self.model.form_id == form_id,
            )
            .first()
        )
