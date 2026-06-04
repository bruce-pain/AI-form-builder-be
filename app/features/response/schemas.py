"""Response request/response schemas"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from app.core.base.schema import BaseResponseModel
from app.features.response.models import ResponseAnswer


class ResponseCreateRequest(BaseModel):
    answers: List[ResponseAnswer]


class ResponseData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    answers: List[ResponseAnswer]
    form_id: str
    created_at: datetime
    updated_at: datetime


class ResponseResponse(BaseResponseModel):
    data: ResponseData


class ResponseListResponse(BaseResponseModel):
    data: List[ResponseData]
