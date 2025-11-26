# backend/app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window_seconds
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        self.requests[client_ip].append(now)
        return True

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return await call_next(request)