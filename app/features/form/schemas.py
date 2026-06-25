"""Form request/response schemas"""

from datetime import datetime
from typing import Annotated, List, Optional, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.base.schema import BaseResponseModel
from app.features.form.models import FormQuestion


class FormQuestionInput(FormQuestion):
    """
    Adds extra cross field validation
    """

    @model_validator(mode="after")
    def check_answer_type(self: Self) -> Self:
        if self.answer_type == "select":
            if (
                self.answer_select_options is None
                or len(self.answer_select_options) < 1
            ):
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


class FormCreateRequest(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=255)]
    description: Annotated[str, Field(min_length=1, max_length=2000)]
    questions: Optional[List[FormQuestionInput]] = Field(default=None, min_length=1)
    conversation_id: Optional[str] = None


class FormUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=1, max_length=2000)
    questions: Optional[List[FormQuestionInput]] = Field(default=None, min_length=1)
    is_published: Optional[bool] = None


class FormResponseData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    questions: Optional[List[FormQuestion]]
    is_published: bool
    conversation_id: Optional[str]
    user_id: str
    created_at: datetime
    updated_at: datetime


class FormResponse(BaseResponseModel):
    data: FormResponseData


class FormListResponseData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    is_published: bool
    user_id: str
    created_at: datetime
    updated_at: datetime


class FormListResponse(BaseResponseModel):
    data: List[FormListResponseData]
