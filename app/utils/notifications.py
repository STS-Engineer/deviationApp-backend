"""
Utility functions for creating and managing notifications
"""
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType
from datetime import datetime


def create_notification(
    db: Session,
    recipient_email: str,
    recipient_role: str,
    request_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    triggered_by_email: str,
    triggered_by_name: str,
    action_url: str = None
):
    """
    Create a notification in the database
    """
    notification = Notification(
        recipient_email=recipient_email,
        recipient_role=recipient_role,
        request_id=request_id,
        type=notification_type,
        title=title,
        message=message,
        triggered_by_email=triggered_by_email,
        triggered_by_name=triggered_by_name,
        action_url=action_url
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


def create_pl_decision_notification(
    db: Session,
    request_id: int,
    commercial_email: str,
    pl_name: str,
    pl_email: str,
    action: str,  # APPROVE, REJECT, ESCALATE
    decision_price: float = None
):
    """
    Create notification when PL makes a decision
    """
    notification_type_map = {
        "APPROVE": NotificationType.PL_APPROVED,
        "REJECT": NotificationType.PL_REJECTED,
        "ESCALATE": NotificationType.PL_ESCALATED,
    }
    
    title_map = {
        "APPROVE": "✅ PL Approved Your Request",
        "REJECT": "❌ PL Rejected Your Request",
        "ESCALATE": "⬆️ PL Escalated to VP",
    }
    
    message_map = {
        "APPROVE": f"PL Manager approved your deviation request and suggested €{decision_price:.2f}",
        "REJECT": "PL Manager rejected your deviation request. Please check the comments for details.",
        "ESCALATE": "PL Manager escalated your request to VP for final decision.",
    }
    
    return create_notification(
        db=db,
        recipient_email=commercial_email,
        recipient_role="COMMERCIAL",
        request_id=request_id,
        notification_type=notification_type_map[action],
        title=title_map[action],
        message=message_map[action],
        triggered_by_email=pl_email,
        triggered_by_name=pl_name,
        action_url=f"/pricing-requests/{request_id}"
    )


def create_vp_decision_notification(
    db: Session,
    request_id: int,
    commercial_email: str,
    vp_name: str,
    vp_email: str,
    action: str,  # APPROVE, REJECT
    final_price: float = None
):
    """
    Create notification when VP makes a final decision
    """
    notification_type_map = {
        "APPROVE": NotificationType.VP_APPROVED,
        "REJECT": NotificationType.VP_REJECTED,
    }
    
    title_map = {
        "APPROVE": "✅ VP Approved Your Request",
        "REJECT": "❌ VP Rejected Your Request",
    }
    
    message_map = {
        "APPROVE": f"VP approved your deviation request with final price €{final_price:.2f}",
        "REJECT": "VP rejected your deviation request. Please check the comments for details.",
    }
    
    return create_notification(
        db=db,
        recipient_email=commercial_email,
        recipient_role="COMMERCIAL",
        request_id=request_id,
        notification_type=notification_type_map[action],
        title=title_map[action],
        message=message_map[action],
        triggered_by_email=vp_email,
        triggered_by_name=vp_name,
        action_url=f"/pricing-requests/{request_id}"
    )


def create_comment_notification(
    db: Session,
    request_id: int,
    recipient_email: str,
    recipient_role: str,
    commenter_email: str,
    commenter_name: str,
    comment_preview: str
):
    """
    Create notification when someone comments on a request
    """
    # Truncate preview to 100 chars
    preview = comment_preview[:100] + "..." if len(comment_preview) > 100 else comment_preview
    
    return create_notification(
        db=db,
        recipient_email=recipient_email,
        recipient_role=recipient_role,
        request_id=request_id,
        notification_type=NotificationType.NEW_COMMENT,
        title="💬 New Comment on Your Request",
        message=f"{commenter_name} commented: {preview}",
        triggered_by_email=commenter_email,
        triggered_by_name=commenter_name,
        action_url=f"/pricing-requests/{request_id}"
    )
