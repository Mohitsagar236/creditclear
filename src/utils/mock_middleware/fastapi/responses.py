"""
Mock implementation of FastAPI response classes.
"""
from typing import Any, Dict, List, Optional, Union


class Response:
    """Base Response class"""
    media_type = None
    
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
    ):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self.media_type = media_type or self.media_type
        self.background = background

    def render(self, content: Any) -> bytes:
        return str(content).encode("utf-8")


class JSONResponse(Response):
    """JSON response class"""
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        import json
        return json.dumps(content).encode("utf-8")


class HTMLResponse(Response):
    """HTML response class"""
    media_type = "text/html"


class PlainTextResponse(Response):
    """Plain text response class"""
    media_type = "text/plain"


class RedirectResponse(Response):
    """Redirect response class"""
    def __init__(
        self,
        url: str,
        status_code: int = 307,
        headers: Optional[Dict[str, str]] = None,
        background: Optional[Any] = None,
    ):
        super().__init__(
            content=None,
            status_code=status_code,
            headers=headers,
            background=background,
        )
        self.headers["location"] = url


class FileResponse(Response):
    """File response class"""
    media_type = None

    def __init__(
        self,
        path: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
        filename: Optional[str] = None,
        stat_result: Optional[Any] = None,
        method: Optional[str] = None,
    ):
        super().__init__(
            content=None,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )
        self.path = path
        self.filename = filename
        self.stat_result = stat_result
        self.method = method
