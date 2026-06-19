"""Response data model"""

from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base.model import BaseTableModel
from app.core.base.types import PydanticType


class ResponseAnswer(BaseModel):
    question_id: Annotated[str, Field(min_length=1)]
    answer_type: Literal["text", "select"]
    text_answer: Optional[str] = None
    select_answer: Optional[List[str]] = None


class Response(BaseTableModel):
    __tablename__ = "responses"

    answers: Mapped[List[ResponseAnswer]] = mapped_column(
        PydanticType(List[ResponseAnswer]), nullable=False
    )

    form: Mapped["Form"] = relationship(back_populates="responses")  # noqa: F821
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.id"))

    updated_at = None
