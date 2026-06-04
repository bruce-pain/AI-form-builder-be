"""Form data model"""

from typing import Annotated, List, Literal, Optional, Self

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base.model import BaseTableModel
from app.core.base.types import PydanticType


# Define the question schema, use pydantic for validation
class FormQuestion(BaseModel):
    id: Annotated[str, Field(min_length=1)]
    text: Annotated[str, Field(min_length=1, max_length=500)]
    answer_type: Literal["text", "select"]
    answer_select_options: Optional[List[str]]
    answer_select_multiple: Optional[bool]
    required: bool

    @model_validator(mode="after")
    def check_answer_type(self: Self) -> Self:
        if self.answer_type == "select":
            if self.answer_select_options is None or len(self.answer_select_options) < 1:
                raise ValueError(
                    "answer_select_options is required when answer_type is 'select'"
                )
            elif self.answer_select_multiple is None:
                raise ValueError(
                    "answer_select_multiple is required when answer_type is 'select'"
                )
        elif self.answer_type == "text":
            if self.answer_select_options is not None:
                raise ValueError(
                    "answer_select_options must be None when answer_type is 'text'"
                )
            elif self.answer_select_multiple is not None:
                raise ValueError(
                    "answer_select_multiple must be None when answer_type is 'text'"
                )

        return self


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
    user: Mapped["User"] = relationship(back_populates="forms")  # noqa: F821
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    responses: Mapped[List["Response"]] = relationship(back_populates="form")  # noqa: F821

    def __str__(self) -> str:
        return "Form: {} - [{}]".format(self.title, self.id)
