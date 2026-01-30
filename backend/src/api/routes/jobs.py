"""
Job Management API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from src.models import get_db
from src.services.storage import JobDB
from src.services.observability import logger

class JobResponse(BaseModel):
    job_id: str
    status: str
    progress: int = 0
    script: Optional[str] = None
    assets: List[Dict[str, Any]] = []
    shot_plan: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

router = APIRouter()

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    Get job status and results
    """
    job = JobDB.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
        
    # Calculate simple progress based on state
    progress = 0
    if job.state == "SUCCEEDED":
        progress = 100
    elif job.state == "FAILED":
        progress = 0
    elif job.state == "RUNNING":
        progress = 50  # TODO: More granular progress
    
    # Extract script from IR or Shot Plan if not explicitly stored
    script_content = ""
    if job.ir and "script" in job.ir:
         script_content = job.ir["script"]
    elif job.shot_plan and "shots" in job.shot_plan:
        # Construct script from narrations
        lines = []
        for i, shot in enumerate(job.shot_plan["shots"]):
            lines.append(f"[Scene {i+1}]")
            if "visual_prompt" in shot:
                lines.append(f"画面: {shot['visual_prompt']}")
            if "narration" in shot:
                lines.append(f"旁白: {shot['narration']}")
            lines.append("") # Empty line for spacing
        script_content = "\n".join(lines)
        
    return JobResponse(
        job_id=job.job_id,
        status=job.state,
        progress=progress,
        script=script_content,
        assets=job.assets or [],
        shot_plan=job.shot_plan,
        error=job.error_details
    )
