"""
Rate Limiter Service
"""

from typing import Dict, Any
from datetime import datetime, timedelta

class RateLimiter:
    """
    Simple in-memory rate limiter (Mock implementation)
    In production, use Redis
    """
    
    def __init__(self):
        self._requests = {}
        self._concurrent_jobs = {}
        
    def check_rate_limit(self, client_ip: str) -> Dict[str, Any]:
        """Check if request is allowed"""
        return {"allowed": True, "reset_at": datetime.utcnow() + timedelta(minutes=1)}
        
    def check_concurrent_jobs(self, client_ip: str) -> Dict[str, Any]:
        """Check concurrent job limit"""
        current = self._concurrent_jobs.get(client_ip, 0)
        return {"allowed": True, "current": current, "max": 5}
        
    def increment_concurrent_jobs(self, client_ip: str):
        """Increment concurrent job count"""
        self._concurrent_jobs[client_ip] = self._concurrent_jobs.get(client_ip, 0) + 1
        
    def decrement_concurrent_jobs(self, client_ip: str):
        """Decrement concurrent job count"""
        if client_ip in self._concurrent_jobs:
            self._concurrent_jobs[client_ip] = max(0, self._concurrent_jobs[client_ip] - 1)
