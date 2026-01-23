from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid

from app.schemas.pricing_request import (
    PricingRequestCreate,
    PricingRequestResponse,
    PricingRequestDetailResponse,
)
from app.models.pricing_request import PricingRequest
from app.models.enums import RequestStatus
from app.core.deps import get_db
from app.emails.mailer import send_pricing_request_email
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/pricing-requests",
    tags=["Pricing Requests"]
)


@router.post("/", response_model=dict)
def submit_pricing_request(
    payload: PricingRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a new pricing request (Commercial role)
    """
    # Validate avocarbon email
    if not payload.requester_email.endswith("@avocarbon.com"):
        raise HTTPException(
            status_code=400,
            detail="Requester email must end with @avocarbon.com"
        )
    
    if not payload.product_line_responsible_email.endswith("@avocarbon.com"):
        raise HTTPException(
            status_code=400,
            detail="Product line responsible email must end with @avocarbon.com"
        )
    
    # Check if costing number already exists
    existing = db.query(PricingRequest).filter(
        PricingRequest.costing_number == payload.costing_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Costing number {payload.costing_number} already exists"
        )
    
    # Validate price logic
    if payload.target_price > payload.initial_price:
        raise HTTPException(
            status_code=400,
            detail="Target price cannot be higher than initial price"
        )

    try:
        request = PricingRequest(
            costing_number=payload.costing_number,
            project_name=payload.project_name,
            customer=payload.customer,
            product_line=payload.product_line,
            plant=payload.plant,
            yearly_sales=payload.yearly_sales,
            initial_price=payload.initial_price,
            target_price=payload.target_price,
            problem_to_solve=payload.problem_to_solve,
            attachment_path=payload.attachment_path,
            requester_email=payload.requester_email,
            requester_name=payload.requester_name,
            product_line_responsible_email=payload.product_line_responsible_email,
            product_line_responsible_name=payload.product_line_responsible_name,
            vp_email=payload.vp_email,
            vp_name=payload.vp_name,
            status=RequestStatus.UNDER_REVIEW_PL.value
        )

        db.add(request)
        db.commit()
        db.refresh(request)

        # Send email to PL responsible
        try:
            send_pricing_request_email(
                to_email=request.product_line_responsible_email,
                project_name=request.project_name,
                customer=request.customer,
                initial_price=float(request.initial_price),
                target_price=float(request.target_price),
                request_id=request.id,
                costing_number=request.costing_number,
            )
        except Exception as e:
            logger.error(f"Failed to send email for request {request.id}: {str(e)}")
            # Don't fail the request if email fails
            pass

        return {
            "message": "Pricing request submitted successfully",
            "request_id": request.id,
            "status": request.status,
            "costing_number": request.costing_number,
        }
    
    except Exception as e:
        logger.error(f"Error creating pricing request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating pricing request")

@router.get("/", response_model=List[PricingRequestResponse])
def get_pricing_requests(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    product_line: Optional[str] = Query(None),
    requester_email: Optional[str] = Query(None),
):
    """
    Get all pricing requests with optional filtering
    """
    query = db.query(PricingRequest).order_by(
        PricingRequest.created_at.desc()
    )
    
    if status:
        query = query.filter(PricingRequest.status == status)
    
    if product_line:
        query = query.filter(PricingRequest.product_line == product_line)
    
    if requester_email:
        query = query.filter(PricingRequest.requester_email == requester_email)
    
    requests = query.all()
    return requests


@router.get("/{request_id}", response_model=PricingRequestDetailResponse)
def get_pricing_request(
    request_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single pricing request with full details
    """
    request = db.query(PricingRequest).filter(
        PricingRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    return request


@router.get("/user/{requester_email}", response_model=List[PricingRequestResponse])
def get_user_pricing_requests(
    requester_email: str,
    db: Session = Depends(get_db),
):
    """
    Get all pricing requests for a specific commercial user
    """
    requests = db.query(PricingRequest).filter(
        PricingRequest.requester_email == requester_email
    ).order_by(PricingRequest.created_at.desc()).all()

    return requests


@router.post("/upload-attachment")
async def upload_attachment(file: UploadFile = File(...)):
    """
    Upload attachment file for pricing request
    """
    # Create uploads directory if it doesn't exist
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Validate file size (max 10MB)
    max_file_size = 10 * 1024 * 1024
    file_size = 0
    chunks = []
    
    # Read file in chunks
    while chunk := await file.file.read(1024):
        file_size += len(chunk)
        if file_size > max_file_size:
            raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")
        chunks.append(chunk)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            for chunk in chunks:
                f.write(chunk)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    return {
        "filename": file.filename,
        "saved_path": file_path,
        "size": file_size
    }

@router.get("/pl/archived")
def get_pl_archived_requests(
    pl_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get archived requests for a PL responsible (approved or rejected by PL)
    """
    requests = db.query(PricingRequest).filter(
        PricingRequest.product_line_responsible_email == pl_email,
        PricingRequest.status.in_([
            RequestStatus.APPROVED_BY_PL.value,
            RequestStatus.REJECTED_BY_PL.value,
            RequestStatus.APPROVED_BY_VP.value,
            RequestStatus.REJECTED_BY_VP.value,
        ])
    ).order_by(PricingRequest.pl_decision_date.desc()).all()
    
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
            "vp_suggested_price": float(r.vp_suggested_price) if r.vp_suggested_price else None,
            "final_approved_price": float(r.final_approved_price) if r.final_approved_price else None,
            "status": r.status,
            "created_at": r.created_at,
            "pl_decision_date": r.pl_decision_date,
            "vp_decision_date": r.vp_decision_date,
        }
        for r in requests
    ]


@router.get("/vp/archived")
def get_vp_archived_requests(
    vp_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get archived requests for a VP (approved or rejected by VP)
    """
    requests = db.query(PricingRequest).filter(
        PricingRequest.vp_email == vp_email,
        PricingRequest.status.in_([
            RequestStatus.APPROVED_BY_VP.value,
            RequestStatus.REJECTED_BY_VP.value,
        ])
    ).order_by(PricingRequest.vp_decision_date.desc()).all()
    
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
            "vp_suggested_price": float(r.vp_suggested_price) if r.vp_suggested_price else None,
            "final_approved_price": float(r.final_approved_price) if r.final_approved_price else None,
            "status": r.status,
            "created_at": r.created_at,
            "vp_decision_date": r.vp_decision_date,
        }
        for r in requests
    ]