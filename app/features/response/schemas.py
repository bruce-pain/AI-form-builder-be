"""Response request/response schemas"""

from datetime import datetime
from typing import List, Self

from pydantic import BaseModel, ConfigDict, model_validator

from app.core.base.schema import BaseResponseModel
from app.features.response.models import ResponseAnswer


class ResponseAnswerInput(ResponseAnswer):
    """
    Adds cross-field validation
    """

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


class FormResponseCreateRequest(BaseModel):
    answers: List[ResponseAnswerInput]


class FormResponseData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    answers: List[ResponseAnswer]
    form_id: str
    created_at: datetime


class FormResponseResponse(BaseResponseModel):
    data: FormResponseData


class FormResponseListResponse(BaseResponseModel):
    data: List[FormResponseData]
