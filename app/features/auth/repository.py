from typing import Optional

from sqlalchemy.orm import Session

from app.core.base.repository import BaseRepository
from app.features.auth.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User:
        return self.db.query(self.model).filter(self.model.email == email).first()

    def get_by_google_sub(self, google_sub: str) -> Optional[User]:
        """Get the user linked to a Google subject identifier.

        Args:
            google_sub: The `sub` claim from a verified Google ID token.

        Returns:
            The linked user if one exists, otherwise None.
        """
        if not google_sub:
            # Guard against a falsy value becoming `WHERE google_sub IS NULL`,
            # which would match an arbitrary user that has no Google account
            # linked.
            return None

        return (
            self.db.query(self.model)
            .filter(self.model.google_sub == google_sub)
            .first()
        )
