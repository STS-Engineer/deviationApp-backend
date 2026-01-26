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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    start_scheduler()


@app.on_event("shutdown")
def shutdown():
    stop_scheduler()


@app.get("/")
def health():
    return {"status": "API is running"}


app.include_router(pricing_request.router)

app.include_router(pl_decisions.router)

app.include_router(vp_decisions.router)

app.include_router(auth.router)

app.include_router(dropdowns.router)

app.include_router(comments.router)

app.include_router(notifications.router)
