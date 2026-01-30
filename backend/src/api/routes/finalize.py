"""
Finalize API Routes - High-quality rendering workflow
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Optional
from sqlalchemy.orm import Session

from src.models import get_db
from src.services.storage import JobDB
from src.services.job_manager import JobManager
from src.services.observability import logger


# Request/Response Models


class FinalizeRequest(BaseModel):
    """Request for job finalization"""

    selected_seeds: Dict[int, int] = Field(
        ...,
        description="Map of shot_id to selected seed from preview",
        example={"1": 12345, "2": 67890}
    )
    resolution: str = Field(
        default="1920x1080",
        description="Target resolution for final render"
    )


class FinalizeResponse(BaseModel):
    """Response for finalization request"""

    job_id: str
    status: str
    message: str


# Router
router = APIRouter()


@router.post("/jobs/{job_id}/finalize", response_model=FinalizeResponse, status_code=status.HTTP_202_ACCEPTED)
async def finalize_job(
    job_id: str,
    request: FinalizeRequest,
    db: Session = Depends(get_db),
):
    """
    Finalize video generation (High Quality Render)

    Regenerates selected shots at higher resolution (1080p) using
    the specific seeds chosen by the user during preview.

    Args:
        job_id: Job identifier
        request: Finalization request with selected seeds
        db: Database session

    Returns:
        FinalizeResponse with job status
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

        # Validate job state
        if job.state != "SUCCEEDED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_JOB_STATE",
                        "message": f"Job must be in SUCCEEDED state to finalize, current state: {job.state}",
                    }
                }
            )

        logger.info(
            "finalize_request",
            job_id=job_id,
            selected_seeds=request.selected_seeds,
            resolution=request.resolution,
        )

        # Create job manager and execute finalization workflow
        job_manager = JobManager()

        # Execute finalization workflow
        finalized_job = await job_manager.execute_finalization_workflow(
            db=db,
            job_id=job_id,
            selected_seeds=request.selected_seeds,
            target_resolution=request.resolution,
        )

        return FinalizeResponse(
            job_id=finalized_job.job_id,
            status=finalized_job.state,
            message="Finalization started. Use GET /v1/t2v/jobs/{job_id} to track progress.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "finalize_error",
            job_id=job_id,
            error=str(e),
            error_type=type(e).__name__,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "FINALIZATION_ERROR",
                    "message": "An error occurred during finalization",
                }
            }
        )
