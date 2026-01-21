from pydantic import BaseModel, field_validator, Field
from typing import Optional
from enum import Enum


class VPActionEnum(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class VPDecision(BaseModel):
    """Schema for VP decision"""
    action: VPActionEnum
    suggested_price: Optional[float] = Field(None, gt=0)
    comments: str = Field(..., min_length=1)

    @field_validator('comments')
    @classmethod
    def comments_required(cls, v):
        if not v or not v.strip():
            raise ValueError("Comments are mandatory for VP decision")
        return v
