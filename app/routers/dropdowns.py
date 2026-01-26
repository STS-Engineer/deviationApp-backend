from fastapi import APIRouter
from app.utils.constants import PRODUCT_LINES, PLANTS, CUSTOMERS
from app.utils.excel_loader import get_customers as get_customers_from_file

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
    """Get list of customers from Excel file, database, or fallback to constants"""
    customers_from_file = get_customers_from_file()
    return {
        "customers": customers_from_file if customers_from_file else CUSTOMERS
    }
