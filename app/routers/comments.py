"""
API routes for comments on pricing requests
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.comment import Comment
from app.models.pricing_request import PricingRequest
from app.schemas.comment import CommentCreate, CommentResponse
from app.utils.notifications import create_comment_notification

router = APIRouter(prefix="/api/comments", tags=["comments"])


@router.get("/request/{request_id}", response_model=list[CommentResponse])
def get_comments(request_id: int, db: Session = Depends(get_db)):
    """
    Get all comments for a pricing request
    """
    # Verify request exists
    request = db.query(PricingRequest).filter(PricingRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    comments = db.query(Comment).filter(Comment.request_id == request_id).order_by(Comment.created_at).all()
    return comments


@router.get("/request/{request_id}/archived", response_model=list[CommentResponse])
def get_archived_comments(request_id: int, db: Session = Depends(get_db)):
    """
    Get archived comments for a pricing request
    """
    # Verify request exists
    request = db.query(PricingRequest).filter(PricingRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    comments = db.query(Comment).filter(
        Comment.request_id == request_id,
        Comment.is_archived == True
    ).order_by(Comment.created_at).all()
    return comments


@router.post("/request/{request_id}", response_model=CommentResponse)
def create_comment(
    request_id: int,
    comment: CommentCreate,
    author_email: str = Query(...),
    author_name: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Add a comment to a pricing request
    """
    # Verify request exists
    request = db.query(PricingRequest).filter(PricingRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    # Determine role based on email
    role = "COMMERCIAL"  # default
    if author_email == request.product_line_responsible_email:
        role = "PL"
    elif author_email == request.vp_email:
        role = "VP"
    
    new_comment = Comment(
        request_id=request_id,
        author_email=author_email,
        author_name=author_name,
        author_role=role,
        content=comment.content
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # Create notifications for relevant parties
    # Notify PL if commercial commented
    if role == "COMMERCIAL" and request.product_line_responsible_email:
        create_comment_notification(
            db=db,
            recipient_email=request.product_line_responsible_email,
            recipient_role="PL",
            request_id=request_id,
            commenter_name=author_name,
            commenter_email=author_email,
            comment_preview=comment.content[:100],
        )
    
    # Notify VP if commercial commented and request is escalated
    if role == "COMMERCIAL" and request.vp_email and request.vp_email != request.product_line_responsible_email:
        from app.models.enums import RequestStatus
        if request.status in [RequestStatus.ESCALATED_TO_VP.value, RequestStatus.APPROVED_BY_VP.value, RequestStatus.REJECTED_BY_VP.value]:
            create_comment_notification(
                db=db,
                recipient_email=request.vp_email,
                recipient_role="VP",
                request_id=request_id,
                commenter_name=author_name,
                commenter_email=author_email,
                comment_preview=comment.content[:100],
            )
    
    # Notify commercial if PL or VP commented
    if role in ["PL", "VP"] and request.requester_email:
        create_comment_notification(
            db=db,
            recipient_email=request.requester_email,
            recipient_role="COMMERCIAL",
            request_id=request_id,
            commenter_name=author_name,
            commenter_email=author_email,
            comment_preview=comment.content[:100],
        )
    
    # Notify VP if PL commented and request is escalated or approved
    if role == "PL" and request.vp_email and request.vp_email != request.product_line_responsible_email:
        from app.models.enums import RequestStatus
        if request.status in [RequestStatus.ESCALATED_TO_VP.value, RequestStatus.APPROVED_BY_VP.value, RequestStatus.REJECTED_BY_VP.value]:
            create_comment_notification(
                db=db,
                recipient_email=request.vp_email,
                recipient_role="VP",
                request_id=request_id,
                commenter_name=author_name,
                commenter_email=author_email,
                comment_preview=comment.content[:100],
            )
    
    # Notify PL if VP commented (so they can see the discussion)
    if role == "VP" and request.product_line_responsible_email and request.product_line_responsible_email != request.vp_email:
        create_comment_notification(
            db=db,
            recipient_email=request.product_line_responsible_email,
            recipient_role="PL",
            request_id=request_id,
            commenter_name=author_name,
            commenter_email=author_email,
            comment_preview=comment.content[:100],
        )
    
    return new_comment


@router.patch("/{comment_id}/archive", response_model=CommentResponse)
def archive_comment(
    comment_id: int,
    author_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Archive a discussion thread (only author or PL/VP can archive)
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    # Get request details to verify permissions
    request = db.query(PricingRequest).filter(PricingRequest.id == comment.request_id).first()
    
    # Allow author, PL responsible, or VP to archive
    is_author = comment.author_email == author_email
    is_pl = author_email == request.product_line_responsible_email
    is_vp = author_email == request.vp_email
    
    if not (is_author or is_pl or is_vp):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to archive this comment")
    
    comment.is_archived = True
    db.commit()
    db.refresh(comment)
    
    return comment


@router.patch("/{comment_id}/unarchive", response_model=CommentResponse)
def unarchive_comment(
    comment_id: int,
    author_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Unarchive a discussion thread (only author or PL/VP can unarchive)
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    # Get request details to verify permissions
    request = db.query(PricingRequest).filter(PricingRequest.id == comment.request_id).first()
    
    # Allow author, PL responsible, or VP to unarchive
    is_author = comment.author_email == author_email
    is_pl = author_email == request.product_line_responsible_email
    is_vp = author_email == request.vp_email
    
    if not (is_author or is_pl or is_vp):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to unarchive this comment")
    
    comment.is_archived = False
    db.commit()
    db.refresh(comment)
    
    return comment


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    author_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Delete a comment (only author can delete)
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    # Only author can delete
    if comment.author_email != author_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the author can delete this comment")
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}
