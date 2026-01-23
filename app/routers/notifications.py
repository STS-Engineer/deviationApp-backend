"""
API routes for notifications
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.deps import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/user/{user_email}", response_model=list[NotificationResponse])
def get_user_notifications(
    user_email: str,
    db: Session = Depends(get_db)
):
    """
    Get all notifications for a user (paginated, ordered by newest first)
    """
    notifications = (
        db.query(Notification)
        .filter(Notification.recipient_email == user_email)
        .order_by(desc(Notification.created_at))
        .limit(50)
        .all()
    )
    return notifications


@router.get("/user/{user_email}/unread", response_model=dict)
def get_unread_count(
    user_email: str,
    db: Session = Depends(get_db)
):
    """
    Get count of unread notifications for a user
    """
    unread_count = (
        db.query(Notification)
        .filter(
            Notification.recipient_email == user_email,
            Notification.is_read == False
        )
        .count()
    )
    return {"unread_count": unread_count}


@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read
    """
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    
    return {"message": "Notification marked as read"}


@router.patch("/user/{user_email}/read-all")
def mark_all_as_read(
    user_email: str,
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read for a user
    """
    db.query(Notification).filter(
        Notification.recipient_email == user_email,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a notification
    """
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted"}
