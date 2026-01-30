"""
Wan2.6 Downloader Service
"""

import aiofiles
import httpx
import os
import uuid
import tempfile

class Wan26Downloader:
    """
    Download generated videos from Wan2.6 URL
    """
    
    async def download_video(self, url: str) -> str:
        """
        Download video to temp file
        
        Args:
            url: Video URL
            
        Returns:
            Path to temporary file
        """
        # Create temp file
        fd, path = tempfile.mkstemp(suffix=".mp4")
        os.close(fd)
        
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url) as response:
                if response.status_code != 200:
                    raise Exception(f"Failed to download video: {response.status_code}")
                    
                async with aiofiles.open(path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        await f.write(chunk)
                        
        return path
