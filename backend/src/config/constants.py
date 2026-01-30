"""
Global Constants
"""

# FFmpeg Configuration
FFMPEG_VIDEO_CODEC = "libx264"
FFMPEG_AUDIO_CODEC = "aac"  # Changed to aac for better compatibility
FFMPEG_VIDEO_BITRATE = "2M"
FFMPEG_AUDIO_BITRATE = "192k"

# Job Configuration
JOB_TIMEOUT_MINUTES = 30
MAX_RETRY_ATTEMPTS = 3

# Quality Modes
QUALITY_MODES = {
    "fast": {
        "preview_seeds": 1,
        "steps": 20,
    },
    "balanced": {
        "preview_seeds": 2,
        "steps": 30,
    },
    "high": {
        "preview_seeds": 4,
        "steps": 50,
    }
}
