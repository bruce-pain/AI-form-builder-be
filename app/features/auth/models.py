"""User data model"""

from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base.model import BaseTableModel


class User(BaseTableModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[Optional[str]]
    google_sub: Mapped[Optional[str]] = mapped_column(
        unique=True, index=True, nullable=True
    )

    forms: Mapped[List["Form"]] = relationship(back_populates="user")  # noqa: F821

    def __str__(self) -> str:
        return "User: {}".format(self.email)
