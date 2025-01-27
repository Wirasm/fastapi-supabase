"""Security provider implementation."""
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware

from ..config import settings
from ..interfaces.security import ISecurityProvider


class SecurityProvider(ISecurityProvider):
    """Default security provider implementation."""

    def __init__(self) -> None:
        """Initialize security provider."""
        self.limiter = Limiter(key_func=get_remote_address)

    def setup_rate_limiting(self, app: FastAPI) -> None:
        """Set up rate limiting for the application."""
        app.state.limiter = self.limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
        app.add_middleware(SlowAPIMiddleware)

    def setup_cors(self, app: FastAPI) -> None:
        """Set up CORS for the application."""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def get_security_headers(self, request: Request) -> dict[str, str]:
        """Get security headers for the application."""
        if not settings.BACKEND_CORS_ORIGINS:  # If no CORS origins, assume development
            return {}

        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "connect-src 'self' https:;"
            ),
        }
