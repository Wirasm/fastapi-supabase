"""Security configuration and middleware."""

from fastapi import FastAPI, Request

from .interfaces.security import ISecurityProvider
from .providers.security import SecurityProvider

def setup_security(app: FastAPI) -> None:
    """Configure security middleware and settings."""
    security_provider: ISecurityProvider = SecurityProvider()

    # Set up security features
    security_provider.setup_rate_limiting(app)
    security_provider.setup_cors(app)

    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        headers = security_provider.get_security_headers(request)
        response.headers.update(headers)
        return response
