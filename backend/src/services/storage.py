"""
Job DB Service
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from src.models.job import JobModel
import json

class JobDB:
    """
    Database operations for Jobs
    """
    
    @staticmethod
    def get_job(db: Session, job_id: str) -> Optional[JobModel]:
        return db.query(JobModel).filter(JobModel.job_id == job_id).first()
        
    @staticmethod
    def create_job(
        db: Session,
        **kwargs
    ) -> JobModel:
        job = JobModel(**kwargs)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
        
    @staticmethod
    def update_job_assets(db: Session, job_id: str, assets: List[Dict[str, Any]]) -> None:
        job = JobDB.get_job(db, job_id)
        if job:
            job.assets = assets
            db.commit()
            
    @staticmethod
    def update_job_error(db: Session, job_id: str, error_details: Dict[str, Any]) -> None:
        job = JobDB.get_job(db, job_id)
        if job:
            job.error_details = error_details
            db.commit()
            
    @staticmethod
    def update_job_selected_seeds(db: Session, job_id: str, selected_seeds: Dict[int, int]) -> None:
        job = JobDB.get_job(db, job_id)
        if job:
            job.selected_seeds = selected_seeds
            db.commit()

class TemplateDB:
    """
    Database operations for Templates (Mock for now as templates are JSON files)
    """
    
    @staticmethod
    def list_templates(db: Session) -> List[Any]:
        # TODO: Load from JSON files in src/templates
        return []
        
    @staticmethod
    def get_template(db: Session, template_id: str, version: str) -> Optional[Any]:
        # TODO: Load specific template
        # Mock return for now
        return type('obj', (object,), {
            'to_dict': lambda: {
                "template_id": template_id,
                "version": version,
                "shot_skeletons": [],
                "tags": {},
                "constraints": {}
            }
        })
