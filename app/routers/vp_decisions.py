from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db
from app.models.pricing_request import PricingRequest
from app.models.enums import RequestStatus
from app.schemas.vp_decision import VPDecision, VPActionEnum
from app.emails.mailer import send_vp_decision_to_commercial
from app.utils.notifications import create_vp_decision_notification
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vp-decisions", tags=["VP Decisions"])


@router.get("/inbox")
def get_vp_inbox(
    vp_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get all escalated pricing requests for a VP
    """
    requests = db.query(PricingRequest).filter(
        PricingRequest.vp_email == vp_email,
        PricingRequest.status == RequestStatus.ESCALATED_TO_VP.value
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
            "pl_suggested_price": float(r.pl_suggested_price) if r.pl_suggested_price else None,
            "pl_comments": r.pl_comments,
            "requester_email": r.requester_email,
            "requester_name": r.requester_name,
            "product_line_responsible_name": r.product_line_responsible_name,
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in requests
    ]


@router.post("/{request_id}")
def vp_decide(
    request_id: int,
    decision: VPDecision,
    db: Session = Depends(get_db),
):
    """
    VP makes a final decision on an escalated pricing request
    Options: APPROVE, REJECT
    """
    request = db.query(PricingRequest).filter(
        PricingRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != RequestStatus.ESCALATED_TO_VP.value:
        raise HTTPException(
            status_code=400,
            detail=f"Request is not escalated to VP (current status: {request.status})"
        )

    action = decision.action

    try:
        if action == VPActionEnum.APPROVE:
            request.status = RequestStatus.APPROVED_BY_VP.value
            request.final_approved_price = decision.suggested_price or request.target_price

        elif action == VPActionEnum.REJECT:
            request.status = RequestStatus.REJECTED_BY_VP.value
            request.final_approved_price = None  # Clear any previous approved price

        request.vp_suggested_price = decision.suggested_price
        request.vp_comments = decision.comments
        request.vp_decision_date = datetime.utcnow()

        db.commit()
        db.refresh(request)

        # Send decision notification to commercial
        send_vp_decision_to_commercial(
            to_email=request.requester_email,
            project_name=request.project_name,
            decision=request.status,
            comments=request.vp_comments,
            final_price=request.final_approved_price,
            costing_number=request.costing_number,
        )

        # Create in-app notification
        create_vp_decision_notification(
            db=db,
            recipient_email=request.requester_email,
            recipient_role="COMMERCIAL",
            request_id=request.id,
            vp_name=request.vp_name or request.vp_email,
            vp_email=request.vp_email,
            action=action.value,
            final_price=request.final_approved_price,
        )

        return {
            "message": f"VP decision processed: {action.value}",
            "request_id": request.id,
            "status": request.status,
            "final_price": float(request.final_approved_price) if request.final_approved_price else None,
        }

    except Exception as e:
        logger.error(f"Error processing VP decision: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing VP decision")


@router.get("/{request_id}")
def get_vp_request_detail(
    request_id: int,
    db: Session = Depends(get_db),
):
    """
    Get full details of an escalated pricing request for VP review
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
        "product_line_responsible_email": request.product_line_responsible_email,
        "product_line_responsible_name": request.product_line_responsible_name,
        "pl_suggested_price": float(request.pl_suggested_price) if request.pl_suggested_price else None,
        "pl_comments": request.pl_comments,
        "pl_decision_date": request.pl_decision_date,
        "status": request.status,
        "created_at": request.created_at,
    }
