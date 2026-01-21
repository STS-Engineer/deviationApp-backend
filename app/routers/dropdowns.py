from fastapi import APIRouter
from app.utils.constants import PRODUCT_LINES, PLANTS
from app.utils.excel_loader import get_customers

router = APIRouter(prefix="/dropdowns", tags=["Dropdowns"])


@router.get("/product-lines")
def get_product_lines():
    """Get list of available product lines"""
    return {"product_lines": PRODUCT_LINES}


@router.get("/plants")
def get_plants():
    """Get list of available plants"""
    return {"plants": PLANTS}


@router.get("/customers")
def get_customers_list():
    """Get list of customers from Excel file or database"""
    customers = get_customers()
    return {
        "customers": customers if customers else [
            "Customer A",
            "Customer B",
            "Customer C",
        ]
    }
