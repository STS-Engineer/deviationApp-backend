"""
Notification model for tracking user notifications across the app
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class NotificationType(str, enum.Enum):
    REQUEST_SUBMITTED = "REQUEST_SUBMITTED"
    PL_APPROVED = "PL_APPROVED"
    PL_REJECTED = "PL_REJECTED"
    PL_ESCALATED = "PL_ESCALATED"
    VP_APPROVED = "VP_APPROVED"
    VP_REJECTED = "VP_REJECTED"
    NEW_COMMENT = "NEW_COMMENT"
    COMMENT_REPLY = "COMMENT_REPLY"
    REQUEST_CLOSED = "REQUEST_CLOSED"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient info
    recipient_email = Column(String(255), nullable=False, index=True)
    recipient_role = Column(String(50), nullable=False)  # COMMERCIAL, PL, VP
    
    # Related request
    request_id = Column(Integer, ForeignKey("pricing_requests.id"), nullable=False, index=True)
    
    # Notification type
    type = Column(Enum(NotificationType), nullable=False, index=True)
    
    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Sender info (who triggered the notification)
    triggered_by_email = Column(String(255), nullable=False)
    triggered_by_name = Column(String(255), nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    action_url = Column(String(500), nullable=True)  # URL to navigate to
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
