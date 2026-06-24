from typing import List, Optional

from pydantic import BaseModel

from app.core.base.schema import BaseResponseModel
from app.features.form.schemas import FormQuestionInput


class FormQuestionList(BaseModel):
    questions: List[FormQuestionInput]


class LLMRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None
    current_state: Optional[FormQuestionList] = None


class LLMResponse(BaseResponseModel):
    data: FormQuestionList
    conversation_id: str
