from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db
from app.models.pricing_request import PricingRequest
from app.models.enums import RequestStatus
from app.schemas.pl_decision import PLDecision, PLActionEnum
from app.emails.mailer import (
    send_pl_decision_to_commercial,
    send_escalation_to_vp,
)
from app.utils.notifications import create_pl_decision_notification
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pl-decisions", tags=["PL Decisions"])


@router.get("/inbox")
def get_pl_inbox(
    pl_email: str = Query(...),
    archived: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get pricing requests for a PL responsible.
    If archived=false: Get pending requests (UNDER_REVIEW_PL status)
    If archived=true: Get completed requests (APPROVED_BY_PL or REJECTED_BY_PL status)
    """
    if not archived:
        # Pending requests - only those under review by this PL
        requests = db.query(PricingRequest).filter(
            PricingRequest.product_line_responsible_email == pl_email,
            PricingRequest.status == RequestStatus.UNDER_REVIEW_PL.value
        ).order_by(PricingRequest.created_at.desc()).all()
    else:
        # Archived/completed requests - those this PL has already decided on
        requests = db.query(PricingRequest).filter(
            PricingRequest.product_line_responsible_email == pl_email,
            PricingRequest.status.in_([
                RequestStatus.APPROVED_BY_PL.value,
                RequestStatus.REJECTED_BY_PL.value,
                RequestStatus.ESCALATED_TO_VP.value,
                RequestStatus.APPROVED_BY_VP.value,
                RequestStatus.REJECTED_BY_VP.value,
                RequestStatus.CLOSED.value
            ])
        ).order_by(PricingRequest.created_at.desc()).all()
    
    return [
        {
            "id": r.id,
            "costing_number": r.costing_number,
            "project_name": r.project_name,
            "customer": r.customer,
            "product_line": r.product_line,
            "plant": r.plant,
            "yearly_sales": float(r.yearly_sales),
            "initial_price": float(r.initial_price),
            "target_price": float(r.target_price),
            "problem_to_solve": r.problem_to_solve,
            "requester_email": r.requester_email,
            "requester_name": r.requester_name,
            "pl_suggested_price": float(r.pl_suggested_price) if r.pl_suggested_price else None,
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in requests
    ]


@router.post("/{request_id}")
def pl_decide(
    request_id: int,
    decision: PLDecision,
    db: Session = Depends(get_db),
):
    """
    PL responsible makes a decision on a pricing request
    Options: APPROVE, REJECT, ESCALATE
    """
    request = db.query(PricingRequest).filter(
        PricingRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != RequestStatus.UNDER_REVIEW_PL.value:
        raise HTTPException(
            status_code=400,
            detail=f"Request is not under Product Line review (current status: {request.status})"
        )

    action = decision.action

    try:
        if action == PLActionEnum.APPROVE:
            request.status = RequestStatus.APPROVED_BY_PL.value
            request.final_approved_price = decision.suggested_price or request.target_price

        elif action == PLActionEnum.REJECT:
            request.status = RequestStatus.REJECTED_BY_PL.value
            request.final_approved_price = None  # Clear any previous approved price

        elif action == PLActionEnum.ESCALATE:
            if not request.vp_email:
                raise HTTPException(
                    status_code=400,
                    detail="VP email not defined for this request. Cannot escalate."
                )
            request.status = RequestStatus.ESCALATED_TO_VP.value

        request.pl_suggested_price = decision.suggested_price
        request.pl_comments = decision.comments
        request.pl_decision_date = datetime.utcnow()

        db.commit()
        db.refresh(request)

        # Send appropriate email notifications
        if action in [PLActionEnum.APPROVE, PLActionEnum.REJECT]:
            try:
                send_pl_decision_to_commercial(
                    to_email=request.requester_email,
                    project_name=request.project_name,
                    decision=request.status,
                    comments=request.pl_comments,
                    suggested_price=request.pl_suggested_price,
                    costing_number=request.costing_number,
                )
            except Exception as email_error:
                logger.warning(f"Email notification failed (non-critical): {str(email_error)}")
                # Continue even if email fails - decision is already saved
            
            # Create in-app notification
            try:
                create_pl_decision_notification(
                    db=db,
                    recipient_email=request.requester_email,
                    recipient_role="COMMERCIAL",
                    request_id=request.id,
                    pl_name=request.product_line_responsible_name or request.product_line_responsible_email,
                    pl_email=request.product_line_responsible_email,
                    action=action.value,
                    suggested_price=request.pl_suggested_price,
                )
            except Exception as notification_error:
                logger.warning(f"In-app notification failed (non-critical): {str(notification_error)}")
                # Continue even if notification fails

        elif action == PLActionEnum.ESCALATE:
            try:
                send_escalation_to_vp(
                    to_email=request.vp_email,
                    project_name=request.project_name,
                    target_price=float(request.target_price),
                    comments=request.pl_comments,
                    initial_price=float(request.initial_price),
                    pl_name=request.product_line_responsible_name or request.product_line_responsible_email,
                    costing_number=request.costing_number,
                )
            except Exception as email_error:
                logger.warning(f"Escalation email failed (non-critical): {str(email_error)}")
                # Continue even if email fails - decision is already saved

        return {
            "message": f"Product Line decision processed: {action.value}",
            "request_id": request.id,
            "status": request.status
        }

    except Exception as e:
        logger.error(f"Error processing PL decision: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing decision: {str(e)}")


@router.get("/{request_id}")
def get_pl_request_detail(
    request_id: int,
    db: Session = Depends(get_db),
):
    """
    Get full details of a pricing request for PL review
    """
    request = db.query(PricingRequest).filter(
        PricingRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    return {
        "id": request.id,
        "costing_number": request.costing_number,
        "project_name": request.project_name,
        "customer": request.customer,
        "product_line": request.product_line,
        "plant": request.plant,
        "yearly_sales": float(request.yearly_sales),
        "initial_price": float(request.initial_price),
        "target_price": float(request.target_price),
        "problem_to_solve": request.problem_to_solve,
        "attachment_path": request.attachment_path,
        "requester_email": request.requester_email,
        "requester_name": request.requester_name,
        "status": request.status,
        "created_at": request.created_at,
    }
