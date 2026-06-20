from typing import List

from pydantic import BaseModel

from app.core.base.schema import BaseResponseModel
from app.features.form.schemas import FormQuestionInput


class FormQuestionList(BaseModel):
    questions: List[FormQuestionInput]


class LLMRequest(BaseModel):
    prompt: str


class LLMResponse(BaseResponseModel):
    data: FormQuestionList
