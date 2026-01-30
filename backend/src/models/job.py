from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from src.models import Base
import uuid

class JobModel(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    state = Column(String, index=True, default="PENDING")
    
    # Input Data
    user_input_redacted = Column(Text)
    user_input_hash = Column(String, index=True)
    pii_flags = Column(JSON, default=list)
    
    # Configuration
    template_id = Column(String)
    template_version = Column(String)
    quality_mode = Column(String)
    resolution = Column(String)
    total_duration_s = Column(Integer)
    
    # Generated Content
    ir = Column(JSON)
    shot_plan = Column(JSON)
    shot_requests = Column(JSON)
    external_task_ids = Column(JSON, default=list)
    assets = Column(JSON, default=list) # To store generated video/audio paths
    
    # Revision
    revision_of = Column(String, ForeignKey("jobs.job_id"), nullable=True)
    targeted_fields = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    error_details = Column(JSON, nullable=True)
    state_transitions = Column(JSON, default=list)
    selected_seeds = Column(JSON, nullable=True)
