"""Form data model"""

from typing import List, Literal, Optional

from pydantic import BaseModel
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base.model import BaseTableModel
from app.core.base.types import PydanticType


# Define the question schema, use pydantic for validation
class FormQuestion(BaseModel):
    id: str
    text: str
    answer_type: Literal["text", "select"]
    answer_select_options: Optional[List[str]]
    answer_select_multiple: Optional[bool]
    required: bool


class Form(BaseTableModel):
    __tablename__ = "forms"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]

    # define questions field with custom PydanticType
    questions: Mapped[Optional[List[FormQuestion]]] = mapped_column(
        PydanticType(List[FormQuestion]), nullable=True
    )

    is_published: Mapped[bool] = mapped_column(default=False)

    # Define many to one relationship with user
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="forms")

    def __str__(self) -> str:
        return "Form: {} - [{}]".format(self.title, self.id)
