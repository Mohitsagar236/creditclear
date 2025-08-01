"""Mock FastAPI middleware package."""

# Import responses
from .responses import Response, JSONResponse, HTMLResponse, PlainTextResponse, RedirectResponse, FileResponse

class MiddlewareInfo:
    """Mock middleware information class"""
    def __init__(self, cls, options=None):
        self.cls = cls
        self.options = options or {}

class FastAPI:
    """Mock FastAPI class."""
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.middleware_stack = []
        self.user_middleware = []
        self.routes = []
    
    def get(self, path, **kwargs):
        """Route decorator for GET method."""
        def decorator(func):
            self.routes.append(("GET", path, func))
            return func
        return decorator
    
    def post(self, path, **kwargs):
        """Route decorator for POST method."""
        def decorator(func):
            self.routes.append(("POST", path, func))
            return func
        return decorator
    
    def put(self, path, **kwargs):
        """Route decorator for PUT method."""
        def decorator(func):
            self.routes.append(("PUT", path, func))
            return func
        return decorator
    
    def delete(self, path, **kwargs):
        """Route decorator for DELETE method."""
        def decorator(func):
            self.routes.append(("DELETE", path, func))
            return func
        return decorator
        
    def add_middleware(self, middleware_class, **kwargs):
        """Add middleware to the application."""
        self.middleware_stack.append((middleware_class, kwargs))
        # Add to user_middleware list as expected by app.user_middleware access
        self.user_middleware.append(MiddlewareInfo(cls=middleware_class, options=kwargs))
        return middleware_class
        
    def include_router(self, router, **kwargs):
        """Include a router in the application."""
        # In a real app, this would add the router's routes to the app
        pass
    
    def exception_handler(self, exc_class_or_status_code):
        """Register an exception handler."""
        def decorator(func):
            # In a real app, this would register the exception handler
            return func
        return decorator


class APIRouter:
    """Mock APIRouter class."""
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.routes = []
    
    def get(self, path, *args, **kwargs):
        """Mock GET route decorator."""
        def decorator(func):
            self.routes.append(("GET", path, func))
            return func
        return decorator
    
    def post(self, path, *args, **kwargs):
        """Mock POST route decorator."""
        def decorator(func):
            self.routes.append(("POST", path, func))
            return func
        return decorator
    
    def put(self, path, *args, **kwargs):
        """Mock PUT route decorator."""
        def decorator(func):
            self.routes.append(("PUT", path, func))
            return func
        return decorator
    
    def delete(self, path, *args, **kwargs):
        """Mock DELETE route decorator."""
        def decorator(func):
            self.routes.append(("DELETE", path, func))
            return func
        return decorator


# For handling validation in Pydantic models
class Path:
    """Mock Path class."""
    def __call__(self, *args, **kwargs):
        return args[0] if args else None


class Query:
    """Mock Query class."""
    def __call__(self, *args, **kwargs):
        return args[0] if args else None


class Body:
    """Mock Body class."""
    def __call__(self, *args, **kwargs):
        return args[0] if args else None


class Depends:
    """Mock Depends class."""
    def __init__(self, dependency=None):
        self.dependency = dependency


class HTTPException(Exception):
    """Mock HTTPException class."""
    def __init__(self, status_code, detail=None, headers=None):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(f"{status_code}: {detail}")


# Mock status codes
class status:
    """Mock status class."""
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_500_INTERNAL_SERVER_ERROR = 500


class Request:
    """Mock Request class."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class BackgroundTasks:
    """Mock BackgroundTasks class."""
    def __init__(self):
        self.tasks = []
    
    def add_task(self, func, *args, **kwargs):
        """Add a task to be run in the background."""
        self.tasks.append((func, args, kwargs))


class WebSocket:
    """Mock WebSocket class."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    async def accept(self):
        """Accept a WebSocket connection."""
        pass
    
    async def send_text(self, text):
        """Send text to the WebSocket client."""
        pass
    
    async def receive_text(self):
        """Receive text from the WebSocket client."""
        return ""
    
    async def close(self):
        """Close the WebSocket connection."""
        pass


class WebSocketDisconnect(Exception):
    """Mock WebSocketDisconnect exception."""
    pass
