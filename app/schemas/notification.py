"""
Schemas for notification API responses
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationResponse(BaseModel):
    id: int
    recipient_email: str
    recipient_role: str
    request_id: int
    type: str
    title: str
    message: str
    triggered_by_email: str
    triggered_by_name: str
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
