from typing import List, Optional

from pydantic import BaseModel

from app.core.base.schema import BaseResponseModel
from app.features.form.schemas import FormQuestionInput


class FormResponse(BaseModel):
    title: Optional[str]
    description: Optional[str]
    questions: List[FormQuestionInput]


class LLMRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None
    current_state: Optional[FormResponse] = None


class LLMResponse(BaseResponseModel):
    data: FormResponse
    conversation_id: str
