"""
Generation API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from src.models import get_db
from src.services.job_manager import JobManager
from src.services.observability import logger

class GenerateRequest(BaseModel):
    user_prompt: str = Field(..., description="User's creative intent", min_length=2, max_length=1000)
    quality_mode: str = Field(default="balanced", description="Generation quality: fast, balanced, high")
    resolution: str = Field(default="1280x720", description="Target resolution")

class GenerateResponse(BaseModel):
    job_id: str
    status: str
    message: str

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_video(
    request: GenerateRequest,
    req: Request,
    db: Session = Depends(get_db),
):
    """
    Submit a new video generation job
    """
    try:
        client_ip = req.client.host if req.client else "unknown"
        
        job_manager = JobManager()
        job = await job_manager.execute_generation_workflow(
            db=db,
            user_input=request.user_prompt,
            quality_mode=request.quality_mode,
            client_ip=client_ip,
            resolution=request.resolution,
        )
        
        return GenerateResponse(
            job_id=job.job_id,
            status=job.state,
            message="Job submitted successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        logger.error("generation_error", error=error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
