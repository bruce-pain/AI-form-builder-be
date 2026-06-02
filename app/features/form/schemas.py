"""Form request/response schemas"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.core.base.schema import BaseResponseModel
from app.features.form.models import FormQuestion


class FormCreateRequest(BaseModel):
    title: str
    description: str
    questions: Optional[List[FormQuestion]] = None


class FormUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[FormQuestion]] = None


class FormResponseData(BaseModel):
    id: str
    title: str
    description: str
    questions: Optional[List[FormQuestion]]
    is_published: bool
    user_id: str
    created_at: datetime
    updated_at: datetime


class FormResponse(BaseResponseModel):
    data: FormResponseData


class FormListResponseData(BaseModel):
    id: str
    title: str
    description: str
    is_published: bool
    user_id: str
    created_at: datetime
    updated_at: datetime


class FormListResponse(BaseResponseModel):
    data: List[FormListResponseData]
