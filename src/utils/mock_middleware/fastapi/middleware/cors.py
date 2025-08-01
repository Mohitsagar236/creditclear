"""
Mock implementation of CORS middleware for FastAPI.
"""
from typing import List, Optional, Sequence, Union, Dict, Any


class CORSMiddleware:
    """
    Mock implementation of CORS middleware.
    Mimics the behavior of fastapi.middleware.cors.CORSMiddleware
    """

    def __init__(
        self,
        app,
        allow_origins: Sequence[str] = (),
        allow_methods: Sequence[str] = ("GET",),
        allow_headers: Sequence[str] = (),
        allow_credentials: bool = False,
        allow_origin_regex: Optional[str] = None,
        expose_headers: Sequence[str] = (),
        max_age: int = 600,
    ):
        self.app = app
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
        self.allow_origin_regex = allow_origin_regex
        self.expose_headers = expose_headers
        self.max_age = max_age

    async def __call__(self, scope, receive, send):
        """Mock CORS middleware call implementation"""
        # Just pass through to the wrapped app
        await self.app(scope, receive, send)
