"""
Main API Entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config.settings import settings
from src.api.routes import generation, jobs, revise, finalize

app = FastAPI(
    title="Prism Health AI Agent API",
    description="API for generating health education videos using Wan2.6",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.static_root), name="static")

# Include Routers
app.include_router(generation.router, prefix="/v1/t2v", tags=["Text-to-Video"])
app.include_router(jobs.router, prefix="/v1/t2v", tags=["Jobs"])
app.include_router(revise.router, prefix="/v1/t2v", tags=["Revision"])
app.include_router(finalize.router, prefix="/v1/t2v", tags=["Finalization"])

@app.on_event("startup")
def on_startup():
    from src.models import Base, engine
    # Create tables
    Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
