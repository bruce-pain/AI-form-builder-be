"""Response data model"""

from typing import Annotated, List, Literal, Optional, Self

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base.model import BaseTableModel
from app.core.base.types import PydanticType


class ResponseAnswer(BaseModel):
    question_id: Annotated[str, Field(min_length=1)]
    answer_type: Literal["text", "select"]
    text_answer: Optional[str]
    select_answer: Optional[List[str]]

    @model_validator(mode="after")
    def check_answer_type(self: Self) -> Self:
        if self.answer_type == "select":
            if self.select_answer is None or len(self.select_answer) < 1:
                raise ValueError(
                    "select_answer is required when answer_type is 'select'"
                )
            elif self.text_answer is not None:
                raise ValueError(
                    "text_answer must be None when answer_type is 'select'"
                )
        elif self.answer_type == "text":
            if self.text_answer is None or len(self.text_answer) < 1:
                raise ValueError("text_answer is required when answer_type is 'text'")
            elif self.select_answer is not None:
                raise ValueError(
                    "select_answer must be None when answer_type is 'text'"
                )

        return self


class Response(BaseTableModel):
    __tablename__ = "responses"

    answers: Mapped[List[ResponseAnswer]] = mapped_column(
        PydanticType(List[ResponseAnswer]), nullable=False
    )

    form: Mapped["Form"] = relationship(back_populates="responses")  # noqa: F821
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.id"))

    updated_at = None
