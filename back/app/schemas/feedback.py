from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FeedbackCreate(BaseModel):
    category: str
    comment: str
    page_url: str


class FeedbackResponse(BaseModel):
    id: int
    username: str
    category: str
    comment: str
    page_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
