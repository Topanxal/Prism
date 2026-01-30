"""
Asset Storage Service
"""

import os
import json
from typing import Dict, Any
from src.config.settings import settings

class AssetStorage:
    """
    Manage storage of generated assets (videos, audio, metadata)
    """
    
    def __init__(self):
        # Ensure directories exist
        os.makedirs(settings.static_video_dir, exist_ok=True)
        os.makedirs(settings.static_audio_dir, exist_ok=True)
        os.makedirs(settings.static_metadata_dir, exist_ok=True)
        
    def get_video_storage_path(self, job_id: str, shot_id: str) -> str:
        """Get absolute path for storing video"""
        filename = f"{job_id}_{shot_id}.mp4"
        return os.path.join(settings.static_video_dir, filename)
        
    def get_audio_storage_path(self, job_id: str, shot_id: str) -> str:
        """Get absolute path for storing audio"""
        filename = f"{job_id}_{shot_id}.mp3"
        return os.path.join(settings.static_audio_dir, filename)
        
    def get_video_url(self, job_id: str, shot_id: str) -> str:
        """Get public URL for video"""
        # TODO: Construct full URL properly based on host
        filename = f"{job_id}_{shot_id}.mp4"
        return f"{settings.static_url_prefix}/{settings.static_video_subdir}/{filename}"
        
    def get_audio_url(self, job_id: str, shot_id: str) -> str:
        """Get public URL for audio"""
        filename = f"{job_id}_{shot_id}.mp3"
        return f"{settings.static_url_prefix}/{settings.static_audio_subdir}/{filename}"
        
    def write_job_metadata(self, job_id: str, metadata: Dict[str, Any]) -> None:
        """Write job metadata to JSON file"""
        filename = f"{job_id}.json"
        path = os.path.join(settings.static_metadata_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
