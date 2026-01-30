from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.core.database import engine, Base
from app.models.pricing_request import PricingRequest
from app.models.comment import Comment
from app.models.notification import Notification
from app.routers import pricing_request, pl_decisions, vp_decisions, auth, dropdowns, comments, notifications
from app.utils.scheduler import start_scheduler, stop_scheduler
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Avocarbon Deviation Pricing API")

# Custom middleware to preserve HTTPS in redirects
class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # If response is a redirect, preserve the original scheme
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get("location")
            if location and location.startswith("http://"):
                # Check if the original request was HTTPS
                scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
                if scheme == "https":
                    location = location.replace("http://", "https://", 1)
                    response.headers["location"] = location
        return response

# Add HTTPS redirect middleware first
app.add_middleware(HTTPSRedirectMiddleware)

# Add CORS middleware - allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Fixed: wildcard origins cannot be used with credentials=True
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    try:
        logger.info("Starting up application...")
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        logger.info("Starting scheduler...")
        try:
            start_scheduler()
            logger.info("Scheduler started successfully")
        except Exception as scheduler_error:
            logger.warning(f"Scheduler startup warning (non-critical): {str(scheduler_error)}")
        
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Critical startup error: {str(e)}", exc_info=True)
        # Don't raise - allow app to start even if scheduler fails
        # raise


@app.on_event("shutdown")
def shutdown():
    try:
        logger.info("Shutting down application...")
        stop_scheduler()
        logger.info("Scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}", exc_info=True)


@app.get("/")
def health():
    """Health check endpoint"""
    try:
        logger.info("Health check requested")
        # Ensure database tables exist
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as db_err:
            logger.warning(f"Could not create tables: {db_err}")
        
        return {
            "status": "API is running",
            "message": "Backend service is healthy and operational",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "version": "1.0.0"
        }


@app.get("/api/health")
def api_health():
    """Detailed API health check endpoint"""
    try:
        logger.info("Detailed health check requested")
        return {
            "status": "healthy",
            "service": "Avocarbon Deviation Pricing API",
            "timestamp": None
        }
    except Exception as e:
        logger.error(f"API health check error: {str(e)}")
        return {
            "status": "error",
            "service": "Avocarbon Deviation Pricing API",
            "error": str(e)
        }


app.include_router(pricing_request.router)

app.include_router(pl_decisions.router)

app.include_router(vp_decisions.router)

app.include_router(auth.router)

app.include_router(dropdowns.router)

app.include_router(comments.router)

app.include_router(notifications.router)
