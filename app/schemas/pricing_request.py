from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class PricingRequestCreate(BaseModel):
    """Schema for creating a new pricing request (Commercial role)"""
    costing_number: str = Field(..., min_length=1, max_length=100)
    project_name: str = Field(..., min_length=1, max_length=255)
    customer: str = Field(..., min_length=1, max_length=255)
    product_line: str = Field(..., min_length=1)
    plant: str = Field(..., min_length=1)

    yearly_sales: float = Field(..., gt=0)
    initial_price: float = Field(..., gt=0)
    target_price: float = Field(..., gt=0)

    problem_to_solve: str = Field(..., min_length=1)
    attachment_path: Optional[str] = None

    requester_email: EmailStr
    requester_name: str = Field(..., min_length=1, max_length=255)
    product_line_responsible_email: EmailStr
    product_line_responsible_name: Optional[str] = None
    vp_email: Optional[EmailStr] = None
    vp_name: Optional[str] = None


class PricingRequestResponse(BaseModel):
    """Response for pricing request"""
    id: int
    costing_number: str
    project_name: str
    customer: str
    product_line: str
    plant: str
    yearly_sales: float
    initial_price: float
    target_price: float
    problem_to_solve: str
    attachment_path: Optional[str]
    requester_email: str
    requester_name: Optional[str]
    product_line_responsible_email: str
    product_line_responsible_name: Optional[str]
    vp_email: Optional[str]
    vp_name: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PricingRequestDetailResponse(PricingRequestResponse):
    """Detailed response including decision information"""
    pl_suggested_price: Optional[float]
    pl_comments: Optional[str]
    pl_decision_date: Optional[datetime]
    vp_suggested_price: Optional[float]
    vp_comments: Optional[str]
    vp_decision_date: Optional[datetime]
    final_approved_price: Optional[float]
