from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.models.pricing_request import PricingRequest
from app.models.comment import Comment
from app.routers import pricing_request, pl_decisions, vp_decisions, auth, dropdowns, comments
from app.utils.scheduler import start_scheduler, stop_scheduler

app = FastAPI(title="Avocarbon Deviation Pricing API")

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
