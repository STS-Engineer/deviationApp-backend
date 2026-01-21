from pydantic import BaseModel, field_validator, Field
from typing import Optional
from enum import Enum


class PLActionEnum(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"


class PLDecision(BaseModel):
    """Schema for PL decision"""
    action: PLActionEnum
    suggested_price: Optional[float] = Field(None, gt=0)
    comments: Optional[str] = Field(None, min_length=1)

    @field_validator('comments')
    @classmethod
    def comments_required_for_reject_escalate(cls, v, info):
        if info.data.get('action') in [PLActionEnum.REJECT, PLActionEnum.ESCALATE]:
            if not v or not v.strip():
                raise ValueError("Comments are mandatory for rejection or escalation")
        return v
