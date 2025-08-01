"""Mock FastAPI middleware base classes."""

class BaseHTTPMiddleware:
    """Mock base class for HTTP middleware."""
    def __init__(self, app=None, dispatch=None):
        self.app = app
        self.dispatch_func = dispatch
    
    async def dispatch(self, request, call_next):
        """Default dispatch method - should be overridden by subclasses."""
        response = await call_next(request)
        return response
        
    async def __call__(self, scope, receive, send):
        """ASGI middleware call."""
        # This is a simplified mock - just pass through
        if self.app:
            await self.app(scope, receive, send)

class ScopeType:
    """Mock scope type."""
    HTTP = "http"
    WEBSOCKET = "websocket"
