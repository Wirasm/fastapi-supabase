"""Security interfaces."""
from abc import ABC, abstractmethod

from fastapi import FastAPI, Request


class ISecurityProvider(ABC):
    """Interface for security providers."""

    @abstractmethod
    def setup_rate_limiting(self, app: FastAPI) -> None:
        """Set up rate limiting for the application."""
        pass

    @abstractmethod
    def setup_cors(self, app: FastAPI) -> None:
        """Set up CORS for the application."""
        pass

    @abstractmethod
    def get_security_headers(self, request: Request) -> dict[str, str]:
        """Get security headers for the application."""
        pass
