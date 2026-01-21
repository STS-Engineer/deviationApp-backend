"""
Comment/Notes model for discussion threads on pricing requests
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("pricing_requests.id"), nullable=False, index=True)
    
    author_email = Column(String(255), nullable=False)
    author_name = Column(String(255), nullable=False)
    author_role = Column(String(50), nullable=False)  # COMMERCIAL, PL, VP
    
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
