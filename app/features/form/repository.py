from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.base.repository import BaseRepository
from app.features.form.models import Form


class FormRepository(BaseRepository[Form]):
    def __init__(self, db: Session):
        super().__init__(Form, db)

    def get_by_user(self, user_id: str) -> List[Form]:
        """Get all forms created by a single user.

        Args:
            user_id: The ID of the user whose forms to retrieve.

        Returns:
            A list of forms belonging to the given user.
        """
        return self.db.query(self.model).filter(self.model.user_id == user_id).all()

    def get_user_form(self, user_id: str, form_id: str) -> Optional[Form]:
        """Get a single form that belongs to a specific user.

        Args:
            user_id: The ID of the user who owns the form.
            form_id: The ID of the form to retrieve.

        Returns:
            The form if found and owned by the user, otherwise None.
        """
        return (
            self.db.query(self.model)
            .filter(
                self.model.id == form_id,
                self.model.user_id == user_id,
            )
            .first()
        )

    def get_public_form(self, form_id: str) -> Optional[Form]:
        """Get a single form that has `is_published` set to True.

        Args:
            form_id: The ID of the published form to retrieve.

        Returns:
            The form if found and published, otherwise None.
        """
        return (
            self.db.query(self.model)
            .filter(
                self.model.id == form_id,
                self.model.is_published.is_(True),
            )
            .first()
        )
