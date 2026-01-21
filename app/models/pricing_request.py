from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Text,
    DateTime,
    Float,
    Boolean
)
from sqlalchemy.sql import func
from app.core.database import Base


class PricingRequest(Base):
    __tablename__ = "pricing_requests"

    id = Column(Integer, primary_key=True, index=True)

    # Commercial submitted fields
    costing_number = Column(String(100), nullable=False, unique=True, index=True)
    project_name = Column(String(255), nullable=False)
    customer = Column(String(255), nullable=False)
    product_line = Column(String(100), nullable=False)
    plant = Column(String(100), nullable=False)

    yearly_sales = Column(Numeric, nullable=False)
    initial_price = Column(Numeric, nullable=False)
    target_price = Column(Numeric, nullable=False)

    problem_to_solve = Column(Text, nullable=False)
    attachment_path = Column(String(500), nullable=True)

    # Users involved
    requester_email = Column(String(255), nullable=False, index=True)
    requester_name = Column(String(255), nullable=False)
    product_line_responsible_email = Column(String(255), nullable=False, index=True)
    product_line_responsible_name = Column(String(255), nullable=True)
    vp_email = Column(String(255), nullable=True, index=True)
    vp_name = Column(String(255), nullable=True)

    # Decision tracking
    pl_suggested_price = Column(Numeric, nullable=True)
    pl_comments = Column(Text, nullable=True)
    pl_decision_date = Column(DateTime(timezone=True), nullable=True)
    
    vp_suggested_price = Column(Numeric, nullable=True)
    vp_comments = Column(Text, nullable=True)
    vp_decision_date = Column(DateTime(timezone=True), nullable=True)

    # Final outcome
    final_approved_price = Column(Numeric, nullable=True)
    
    status = Column(String(50), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        index=True
    )
