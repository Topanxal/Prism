"""
Job Manager - Core orchestration logic
"""

import asyncio
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from src.models.job import JobModel
from src.services.storage import JobDB
from src.services.job_state import transition_state
from src.services.observability import logger
from src.services.rate_limiter import RateLimiter
from src.core.input_processor import InputProcessor
from src.core.llm_orchestrator import LLMOrchestrator
from src.core.template_router import TemplateRouter
from src.core.prompt_compiler import PromptCompiler
from src.core.wan26_adapter import Wan26Adapter, ShotGenerationRequest
from src.core.validator import Validator
from src.services.wan26_downloader import Wan26Downloader
from src.services.asset_storage import AssetStorage
from src.config.settings import settings
from src.services.mock_data import MockDataService


class JobManager:
    """
    Orchestrates the entire text-to-video generation workflow
    """

    def __init__(self):
        self.input_processor = InputProcessor()
        self.llm_orchestrator = LLMOrchestrator()
        self.template_router = TemplateRouter()
        self.prompt_compiler = PromptCompiler()
        self.wan26_adapter = Wan26Adapter()
        self.validator = Validator()
        self.rate_limiter = RateLimiter()
        self.downloader = Wan26Downloader()
        self.storage = AssetStorage()

    async def execute_generation_workflow(
        self,
        db: Session,
        user_input: str,
        quality_mode: str,
        client_ip: str,
        resolution: str = "1280x720",
    ) -> JobModel:
        """
        Execute full generation workflow
        """
        # 1. Rate Limiting
        limit_check = self.rate_limiter.check_rate_limit(client_ip)
        if not limit_check["allowed"]:
            raise ValueError(f"Rate limit exceeded. Try again after {limit_check['reset_at']}")

        # 2. Input Processing
        processed_input = self.input_processor.process_input(user_input)
        
        # 3. Create Job Record
        job = JobDB.create_job(
            db=db,
            user_input_redacted=processed_input["redacted_text"],
            user_input_hash=processed_input["input_hash"],
            pii_flags=processed_input["pii_flags"],
            quality_mode=quality_mode,
            resolution=resolution,
            state="PENDING"
        )
        
        # MOCK MODE CHECK
        if settings.mock_mode:
            logger.info("mock_mode_activated", job_id=job.job_id)
            
            # Transition to RUNNING
            transition_state(db, job.job_id, "RUNNING", "mock_processing_started")
            
            # Simulate processing delay
            # await asyncio.sleep(2) 
            
            # Use mock data
            mock_ir = MockDataService.get_mock_ir()
            mock_shot_plan = MockDataService.get_mock_shot_plan()
            mock_assets = MockDataService.get_mock_shot_assets()
            
            # Update job with mock data
            job.ir = mock_ir
            job.shot_plan = {"shots": mock_shot_plan}
            job.assets = mock_assets
            db.commit()
            
            # Transition to SUCCEEDED
            transition_state(db, job.job_id, "SUCCEEDED", "mock_processing_complete")
            
            return job

        # START BACKGROUND PROCESSING
        # In a real app, this would be offloaded to Celery/Redis Queue
        # Here we use asyncio.create_task for simplicity
        asyncio.create_task(self._process_job_background(db, job.job_id, processed_input, quality_mode))
        
        return job

    async def _process_job_background(
        self,
        db: Session,
        job_id: str,
        processed_input: Dict[str, Any],
        quality_mode: str,
    ):
        """
        Background processing task
        """
        try:
            transition_state(db, job_id, "RUNNING", "processing_started")
            
            # 1. LLM IR Parsing
            ir = self.llm_orchestrator.parse_ir(processed_input["redacted_text"], quality_mode)
            
            # 2. Template Routing
            # Note: We need a fresh db session for background task if not passed correctly, 
            # but here we assume db is thread-safe or scoped correctly for this simple example.
            # In production, create a new session here.
            template_match = self.template_router.match_template(ir.dict(), db)
            
            if not template_match:
                # Fallback to generic template or error
                # For now, raise error
                raise ValueError("No suitable template found")
                
            # 3. Template Instantiation
            shot_plan = self.llm_orchestrator.instantiate_template(ir, template_match.template)
            
            # Update Job with intermediate results
            job = JobDB.get_job(db, job_id)
            job.ir = ir.dict()
            job.template_id = template_match.template_id
            job.template_version = template_match.version
            job.shot_plan = shot_plan.dict()
            db.commit()
            
            # 4. Video Generation (Parallel)
            tasks = []
            shot_requests = []
            
            for shot in shot_plan.shots:
                compiled = self.prompt_compiler.compile_shot_prompt(
                    shot, shot_plan.dict(), ir.dict()
                )
                
                request = ShotGenerationRequest(
                    prompt=compiled.compiled_prompt,
                    negative_prompt=compiled.compiled_negative_prompt,
                    duration=shot.get("duration_s", 5),
                    size="1280*720", # TODO: Use job config
                    seed=shot.get("seed", 12345)
                )
                
                shot_requests.append({
                    "shot_id": shot["shot_id"],
                    "request": request.dict(),
                    "task_id": None
                })
                
                tasks.append(self.wan26_adapter.submit_shot_request(request))
                
            # Submit all requests
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update shot requests with task IDs
            active_tasks = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error("shot_submission_failed", shot_id=shot_requests[i]["shot_id"], error=str(response))
                    # Handle partial failure?
                else:
                    shot_requests[i]["task_id"] = response.task_id
                    active_tasks.append((shot_requests[i]["shot_id"], response.task_id))
            
            job.shot_requests = shot_requests
            db.commit()
            
            # 5. Poll for Completion
            # Simple polling implementation
            assets = []
            for shot_id, task_id in active_tasks:
                result = await self.wan26_adapter.poll_task_status(task_id)
                if result.status == "succeeded":
                    # Download video
                    local_path = await self.downloader.download_video(result.video_url)
                    
                    # Move to permanent storage
                    storage_path = self.storage.get_video_storage_path(job_id, str(shot_id))
                    import shutil
                    shutil.move(local_path, storage_path)
                    
                    assets.append({
                        "shot_id": shot_id,
                        "video_url": self.storage.get_video_url(job_id, str(shot_id)),
                        "status": "completed"
                    })
                else:
                    assets.append({
                        "shot_id": shot_id,
                        "status": "failed",
                        "error": result.error
                    })
            
            JobDB.update_job_assets(db, job_id, assets)
            
            transition_state(db, job_id, "SUCCEEDED", "processing_complete")
            
        except Exception as e:
            logger.error("job_processing_failed", job_id=job_id, error=str(e))
            JobDB.update_job_error(db, job_id, {"message": str(e)})
            transition_state(db, job_id, "FAILED", str(e))

    async def execute_revision_workflow(
        self,
        db: Session,
        parent_job_id: str,
        feedback: str,
        targeted_fields: List[str],
        suggested_modifications: Dict[str, Any],
        client_ip: Optional[str] = None,
    ) -> JobModel:
        """
        Execute revision workflow
        """
        # Get parent job
        parent_job = JobDB.get_job(db, parent_job_id)
        if not parent_job:
            raise ValueError(f"Parent job not found: {parent_job_id}")

        # MOCK MODE CHECK
        if settings.mock_mode:
            logger.info("mock_mode_revision", parent_job_id=parent_job_id)
            
            # Copy parent data
            import copy
            mock_ir = copy.deepcopy(parent_job.ir) if parent_job.ir else {}
            if "narration" in targeted_fields and isinstance(mock_ir, dict):
                if "audio" not in mock_ir: mock_ir["audio"] = {}
                mock_ir["audio"]["narration_tone"] = "casual_mock"
            
            # Create revised job
            job = JobDB.create_job(
                db=db,
                user_input_redacted=parent_job.user_input_redacted,
                user_input_hash=parent_job.user_input_hash,
                pii_flags=parent_job.pii_flags,
                template_id=parent_job.template_id,
                template_version=parent_job.template_version,
                quality_mode=parent_job.quality_mode,
                resolution=parent_job.resolution,
                ir=mock_ir,
                shot_plan=parent_job.shot_plan,
                revision_of=parent_job_id,
                targeted_fields=targeted_fields,
                state="SUCCEEDED", # Immediate success for mock
                assets=parent_job.assets # Reuse assets
            )
            
            return job

        # Real revision logic would go here
        # For now, just raise not implemented for live mode
        raise NotImplementedError("Live revision not yet implemented")

    async def execute_finalization_workflow(
        self,
        db: Session,
        job_id: str,
        selected_seeds: Dict[int, int],
        target_resolution: str = "1920x1080",
    ) -> JobModel:
        """
        Execute finalization workflow
        """
        job = JobDB.get_job(db, job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")
            
        JobDB.update_job_selected_seeds(db, job_id, selected_seeds)
        
        # MOCK MODE CHECK
        if settings.mock_mode:
            logger.info("mock_mode_finalization", job_id=job_id)
            
            # Update assets metadata
            new_assets = []
            if job.assets:
                for asset in job.assets:
                    new_asset = asset.copy()
                    new_asset["resolution"] = target_resolution
                    new_assets.append(new_asset)
            
            JobDB.update_job_assets(db, job_id, new_assets)
            transition_state(db, job_id, "SUCCEEDED", "mock_finalization_complete")
            
            return job
            
        raise NotImplementedError("Live finalization not yet implemented")
