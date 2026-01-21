"""
API routes for comments on pricing requests
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.comment import Comment
from app.models.pricing_request import PricingRequest
from app.schemas.comment import CommentCreate, CommentResponse

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
    
    return new_comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
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
    
    # Verify user is the comment author
    if comment.author_email != author_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only delete your own comments")
    
    db.delete(comment)
    db.commit()
    
    return None
