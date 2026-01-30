"""
Jobs API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from src.models import get_db
from src.services.storage import JobDB
from src.services.observability import logger


# Response Models


class ShotAssetResponse(BaseModel):
    """Shot asset response"""

    shot_id: int
    seed: int
    video_url: str
    audio_url: str
    duration_s: int
    resolution: str


class JobStatusResponse(BaseModel):
    """Job status response"""

    job_id: str
    status: str
    created_at: str
    updated_at: str
    template_id: str
    quality_mode: str
    resolution: Optional[str] = None
    total_duration_s: Optional[int] = None
    shot_assets: Optional[List[ShotAssetResponse]] = None
    preview_shot_assets: Optional[List[ShotAssetResponse]] = None
    error_details: Optional[Dict[str, Any]] = None
    shot_plan: Optional[List[Dict[str, Any]]] = None  # Add shot_plan to response
    script: Optional[str] = None # Add full script to response


# Router
router = APIRouter()


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    Get job status and results

    Args:
        job_id: Job identifier
        db: Database session

    Returns:
        JobStatusResponse with current status and assets (if available)
    """
    try:
        # Get job from database
        job = JobDB.get_job(db, job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "JOB_NOT_FOUND",
                        "message": f"Job {job_id} not found",
                    }
                }
            )

        logger.info(
            "job_status_query",
            job_id=job_id,
            status=job.state,
        )

        # Build response
        response_data = {
            "job_id": job.job_id,
            "status": job.state,
            "created_at": job.created_at.isoformat() if job.created_at else "",
            "updated_at": job.updated_at.isoformat() if job.updated_at else "",
            "template_id": job.template_id,
            "quality_mode": job.quality_mode,
        }
        
        # Include shot_plan if available (useful for frontend script display)
        if job.shot_plan:
             # Ensure shot_plan is a list or extract shots if it's a dict
             shots = job.shot_plan
             if isinstance(job.shot_plan, dict):
                 shots = job.shot_plan.get("shots", [])
             
             response_data["shot_plan"] = shots
             
             # Construct simple script string from shot plan for convenience
             script_lines = []
             if isinstance(shots, list):
                 for shot in shots:
                     if isinstance(shot, dict):
                         # Format timestamp (mock start time based on accumulation would be better but simple loop is fine for now)
                         script_lines.append(f"画面：{shot.get('visual_prompt', '')}")
                         script_lines.append(f"旁白：{shot.get('narration', '')}")
             response_data["script"] = "\n".join(script_lines)

        # Add output metadata if job succeeded
        if job.state == "SUCCEEDED":
            response_data["resolution"] = job.resolution
            response_data["total_duration_s"] = job.total_duration_s

            # Add shot assets if available
            if job.shot_assets:
                response_data["shot_assets"] = [
                    {
                        "shot_id": asset["shot_id"],
                        "seed": asset["seed"],
                        "video_url": asset["video_url"],
                        "audio_url": asset["audio_url"],
                        "duration_s": asset["duration_s"],
                        "resolution": asset["resolution"],
                    }
                    for asset in job.shot_assets
                ]

            # Add preview assets if available
            if job.preview_shot_assets:
                response_data["preview_shot_assets"] = [
                    {
                        "shot_id": asset["shot_id"],
                        "seed": asset["seed"],
                        "video_url": asset["video_url"],
                        "audio_url": asset["audio_url"],
                        "duration_s": asset["duration_s"],
                        "resolution": asset["resolution"],
                    }
                    for asset in job.preview_shot_assets
                ]

        # Add error details if job failed
        if job.state == "FAILED" and job.error_details:
            response_data["error_details"] = job.error_details

        return JobStatusResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "job_status_error",
            job_id=job_id,
            error=str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An error occurred while retrieving job status",
                }
            }
        )
