import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List, Protocol, Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import EmailStr

from gotrue.errors import AuthApiError

from supabase._async.client import AsyncClient, create_client
from supabase.lib.client_options import AsyncClientOptions

from ..core.config import settings
from .schemas import UserIn


class ISupabaseClient(Protocol):
    """Interface for Supabase client operations"""
    async def table(self, name: str) -> AsyncClient: ...
    async def auth(self) -> AsyncClient: ...


class IAuthService(ABC):
    """Interface for authentication service"""
    @abstractmethod
    async def get_current_user(self, token: str) -> UserIn:
        """Get current authenticated user"""
        pass

    @abstractmethod
    async def validate_roles(self, user: UserIn, roles: List[str]) -> None:
        """Validate user roles"""
        pass


class SupabaseAuthService(IAuthService):
    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_current_user(self, token: str) -> UserIn:
        try:
            logging.info(f"Attempting to get user with token")
            
            # Get the user directly with the token
            response = await self.client.auth.get_user(token)
            logging.info(f"Got user response: {response}")
            
            if not response or not response.user:
                logging.error("No user found in response")
                raise AuthError("Invalid authentication credentials")

            user_email = response.user.email
            if not user_email:
                logging.error("No email found in user data")
                raise AuthError("User email is required")

            return UserIn(
                id=response.user.id,
                email=user_email,  # EmailStr validation is handled by the Pydantic model
                is_active=True,
                roles=response.user.user_metadata.get("roles", []),
                metadata=response.user.user_metadata
            )
        except AuthApiError as e:
            logging.error(f"AuthApiError: {str(e)}")
            raise AuthError(str(e))
        except Exception as e:
            logging.error(f"Unexpected error in get_current_user: {str(e)}")
            raise AuthError(f"Authentication failed: {str(e)}")

    async def validate_roles(self, user: UserIn, roles: List[str]) -> None:
        if not any(role in user.roles for role in roles):
            raise PermissionError("User does not have required roles")


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class AuthError(HTTPException):
    def __init__(self, detail: str, headers: Optional[dict] = None):
        super().__init__(status_code=401, detail=detail, headers=headers or {"WWW-Authenticate": "Bearer"})


class PermissionError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=403, detail=detail)


# Security scheme
security = HTTPBearer(
    scheme_name="Bearer Auth",
    description="Enter your JWT token",
    auto_error=True,
    bearerFormat="JWT"
)

# Global client instance
super_client: Optional[AsyncClient] = None


async def init_super_client() -> None:
    """Initialize Supabase client at lifespan event"""
    global super_client
    try:
        options = AsyncClientOptions(
            postgrest_client_timeout=settings.SUPABASE_TIMEOUT,
            storage_client_timeout=settings.SUPABASE_TIMEOUT,
            auto_refresh_token=True,
            persist_session=True
        )
        
        super_client = await create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
            options=options
        )
        logging.info("Supabase client initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize Supabase client: {e}")
        raise


def get_auth_service() -> IAuthService:
    """Get authentication service instance"""
    if not super_client:
        raise HTTPException(
            status_code=500,
            detail="Authentication service not initialized"
        )
    return SupabaseAuthService(super_client)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> UserIn:
    """Get current user from token.
    
    Args:
        credentials: The HTTP Authorization credentials containing the JWT token
        
    Returns:
        UserIn: The current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        if not super_client:
            logging.error("Database connection not initialized")
            raise HTTPException(
                status_code=500,
                detail="Database connection not initialized"
            )
        
        logging.info(f"Validating token: {credentials.credentials}")
        
        # Get user data directly from the token
        user = await super_client.auth.get_user(credentials.credentials)
        logging.info(f"Got user: {user}")
        
        if not user or not user.user:
            logging.error("No user found in session")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
            )
        
        user_data = {
            "id": user.user.id,
            "email": user.user.email,
            "is_superuser": user.user.user_metadata.get("is_superuser", False),
            "roles": user.user.user_metadata.get("roles", [])
        }
        logging.info(f"User data: {user_data}")
        
        return UserIn(**user_data)
        
    except Exception as e:
        logging.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )


async def get_db(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> AsyncClient:
    """Get database client instance with authenticated session.
    
    Args:
        credentials: The HTTP Authorization credentials containing the JWT token
        
    Returns:
        AsyncClient: The Supabase client instance with authenticated session
        
    Raises:
        HTTPException: If database connection is not initialized
    """
    try:
        if not super_client:
            logging.error("Database connection not initialized")
            raise HTTPException(
                status_code=500,
                detail="Database connection not initialized"
            )
        
        # Set auth headers for database operations
        super_client.postgrest.auth(credentials.credentials)
        return super_client
        
    except Exception as e:
        logging.error(f"Error setting up database client: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


def has_roles(*roles: UserRole):
    """Role-based authorization dependency.
    
    Args:
        roles: Variable number of UserRole enums representing required roles
        
    Returns:
        Callable: An async function that checks if the user has any of the required roles
        
    Raises:
        PermissionError: If user lacks the required roles
    """
    async def role_checker(
        user: UserIn = Depends(get_current_user),
        auth_service: IAuthService = Depends(get_auth_service)
    ):
        try:
            await auth_service.validate_roles(user, [role.value for role in roles])
            logging.info(f"User {user.email} authorized with roles: {[role.value for role in roles]}")
            return user
        except Exception as e:
            logging.error(f"Role validation failed for user {user.email}: {str(e)}")
            raise
    return role_checker