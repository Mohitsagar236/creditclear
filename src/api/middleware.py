"""
Enhanced API middleware for the credit risk model.

This module provides advanced middleware for logging, error handling,
rate limiting, and performance monitoring.
"""

import time
import json
import uuid
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import logging
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
import traceback

# Try to import real FastAPI middleware, fall back to mock
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    # Use our mock implementation
    import sys
    import os
    mock_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "utils", "mock_middleware")
    if os.path.exists(mock_path):
        sys.path.insert(0, mock_path)
        from fastapi.middleware.base import BaseHTTPMiddleware
    else:
        # Fallback mock implementation
        class BaseHTTPMiddleware:
            def __init__(self, app=None, dispatch=None):
                self.app = app
                self.dispatch_func = dispatch
            
            async def dispatch(self, request, call_next):
                response = await call_next(request)
                return response

logger = logging.getLogger(__name__)


class APILoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive API request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        client_ip = request.client.host
        
        logger.info(
            f"REQUEST {request_id}: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", ""),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"RESPONSE {request_id}: {response.status_code} ({process_time:.3f}s)",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Add response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                f"ERROR {request_id}: {str(e)} ({process_time:.3f}s)",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "process_time": process_time,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exc_info=True
            )
            
            # Return structured error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers={"X-Request-ID": request_id}
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for API rate limiting."""
    
    def __init__(self, app, calls_per_minute: int = 60, calls_per_hour: int = 1000):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.calls_per_hour = calls_per_hour
        self.minute_windows = defaultdict(lambda: deque())
        self.hour_windows = defaultdict(lambda: deque())
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        current_time = datetime.utcnow()
        
        # Check rate limits
        if await self._is_rate_limited(client_ip, current_time):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.calls_per_minute} calls per minute or {self.calls_per_hour} calls per hour",
                    "retry_after": 60,
                    "timestamp": current_time.isoformat()
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit-Minute": str(self.calls_per_minute),
                    "X-RateLimit-Limit-Hour": str(self.calls_per_hour)
                }
            )
        
        # Record the request
        self._record_request(client_ip, current_time)
        
        response = await call_next(request)
        
        # Add rate limit headers
        minute_remaining = self._get_remaining_calls(client_ip, current_time, "minute")
        hour_remaining = self._get_remaining_calls(client_ip, current_time, "hour")
        
        response.headers["X-RateLimit-Remaining-Minute"] = str(minute_remaining)
        response.headers["X-RateLimit-Remaining-Hour"] = str(hour_remaining)
        
        return response
    
    async def _is_rate_limited(self, client_ip: str, current_time: datetime) -> bool:
        # Clean old entries
        self._clean_old_entries(client_ip, current_time)
        
        # Check minute limit
        minute_calls = len(self.minute_windows[client_ip])
        if minute_calls >= self.calls_per_minute:
            return True
            
        # Check hour limit
        hour_calls = len(self.hour_windows[client_ip])
        if hour_calls >= self.calls_per_hour:
            return True
            
        return False
    
    def _record_request(self, client_ip: str, current_time: datetime):
        self.minute_windows[client_ip].append(current_time)
        self.hour_windows[client_ip].append(current_time)
    
    def _clean_old_entries(self, client_ip: str, current_time: datetime):
        minute_ago = current_time - timedelta(minutes=1)
        hour_ago = current_time - timedelta(hours=1)
        
        # Clean minute window
        while (self.minute_windows[client_ip] and 
               self.minute_windows[client_ip][0] < minute_ago):
            self.minute_windows[client_ip].popleft()
            
        # Clean hour window
        while (self.hour_windows[client_ip] and 
               self.hour_windows[client_ip][0] < hour_ago):
            self.hour_windows[client_ip].popleft()
    
    def _get_remaining_calls(self, client_ip: str, current_time: datetime, window: str) -> int:
        self._clean_old_entries(client_ip, current_time)
        
        if window == "minute":
            return max(0, self.calls_per_minute - len(self.minute_windows[client_ip]))
        elif window == "hour":
            return max(0, self.calls_per_hour - len(self.hour_windows[client_ip]))
        return 0


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for response caching."""
    
    def __init__(self, app, cache_ttl: int = 300):  # 5 minutes default
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.cache = {}
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
            
        # Generate cache key
        cache_key = f"{request.method}:{request.url.path}:{request.url.query}"
        
        # Check cache
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            logger.info(f"Cache HIT for {cache_key}")
            response = Response(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers=cached_response["headers"]
            )
            response.headers["X-Cache"] = "HIT"
            return response
            
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200:
            await self._cache_response(cache_key, response)
            response.headers["X-Cache"] = "MISS"
        
        return response
    
    def _get_cached_response(self, cache_key: str) -> dict:
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.utcnow() < cached_data["expires_at"]:
                return cached_data
            else:
                # Remove expired entry
                del self.cache[cache_key]
        return None
    
    async def _cache_response(self, cache_key: str, response: Response):
        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
            
        # Store in cache
        self.cache[cache_key] = {
            "content": body,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "expires_at": datetime.utcnow() + timedelta(seconds=self.cache_ttl)
        }
        
        # Recreate response with body
        response.body_iterator = self._generate_body(body)
    
    async def _generate_body(self, body: bytes):
        yield body


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and metrics collection."""
    
    def __init__(self, app):
        super().__init__(app)
        self.metrics = {
            "request_count": 0,
            "total_response_time": 0,
            "average_response_time": 0,
            "endpoint_metrics": defaultdict(lambda: {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "errors": 0
            })
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        endpoint = f"{request.method} {request.url.path}"
        
        try:
            response = await call_next(request)
            
            # Calculate metrics
            process_time = time.time() - start_time
            self._update_metrics(endpoint, process_time, response.status_code >= 400)
            
            # Add performance headers
            response.headers["X-Performance-Time"] = f"{process_time:.3f}"
            response.headers["X-Performance-Endpoint-Avg"] = f"{self.metrics['endpoint_metrics'][endpoint]['avg_time']:.3f}"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            self._update_metrics(endpoint, process_time, True)
            raise e
    
    def _update_metrics(self, endpoint: str, process_time: float, is_error: bool):
        # Global metrics
        self.metrics["request_count"] += 1
        self.metrics["total_response_time"] += process_time
        self.metrics["average_response_time"] = (
            self.metrics["total_response_time"] / self.metrics["request_count"]
        )
        
        # Endpoint metrics
        endpoint_data = self.metrics["endpoint_metrics"][endpoint]
        endpoint_data["count"] += 1
        endpoint_data["total_time"] += process_time
        endpoint_data["avg_time"] = endpoint_data["total_time"] / endpoint_data["count"]
        
        if is_error:
            endpoint_data["errors"] += 1
    
    def get_metrics(self) -> dict:
        """Get current performance metrics."""
        return dict(self.metrics)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers and basic protection."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
