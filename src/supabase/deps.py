import logging
from enum import Enum
from typing import Annotated, AsyncGenerator, Optional, List

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from gotrue.errors import AuthApiError

from supabase._async.client import AsyncClient, create_client
from supabase.lib.client_options import AsyncClientOptions

from ..core.config import settings
from .schemas import UserIn

# Change to HTTPBearer
security = HTTPBearer(
    scheme_name="Bearer Auth", description="Enter your Supabase JWT token"
)

super_client: Optional[AsyncClient] = None

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

async def init_super_client() -> None:
    """for validation access_token init at life span event"""
    global super_client
    super_client = await create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
        options=AsyncClientOptions(
            postgrest_client_timeout=10, storage_client_timeout=10
        ),
    )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> UserIn:
    """
    Validate JWT token and return current user with enhanced security checks
    """
    if not super_client:
        raise HTTPException(status_code=500, detail="Super client not initialized")

    try:
        token = credentials.credentials
        if token.startswith("Bearer "):
            token = token[7:]

        # Validate token and get user
        user_rsp = await super_client.auth.get_user(jwt=token)
        
        if not user_rsp or not user_rsp.user:
            raise AuthError("Invalid authentication credentials")

        # Extract user metadata and roles
        user_data = user_rsp.user
        user_metadata = user_data.user_metadata or {}
        roles = user_metadata.get("roles", ["user"])

        # Create UserIn instance with enhanced data
        return UserIn(
            id=user_data.id,
            email=user_data.email,
            roles=roles,
            metadata=user_metadata
        )

    except AuthApiError as e:
        if "expired" in str(e).lower():
            raise AuthError("Token has expired")
        raise AuthError(f"Authentication failed: {str(e)}")
    except Exception as e:
        logging.error(f"Authentication error: {str(e)}")
        raise AuthError("Authentication failed")

async def require_roles(user: UserIn, required_roles: List[UserRole]) -> None:
    """
    Validate user has required roles
    """
    user_roles = set(user.roles)
    required = set(required_roles)
    
    if not (user_roles & required):
        raise PermissionError(f"User does not have required roles: {required}")

# Role-based dependency
def has_roles(*roles: UserRole):
    async def role_checker(user: UserIn = Depends(get_current_user)):
        await require_roles(user, roles)
        return user
    return role_checker

# Enhanced database session with user context
async def get_db(user: UserIn = Depends(get_current_user)) -> AsyncGenerator[AsyncClient, None]:
    """
    Get database session with user context and enhanced error handling
    """
    try:
        client = await create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
            options=AsyncClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                headers={
                    "X-User-Id": user.id,
                    "X-User-Email": user.email
                }
            ),
        )
        yield client
    except Exception as e:
        logging.error(f"Database session error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")

CurrentUser = Annotated[UserIn, Depends(get_current_user)]

SessionDep = Annotated[AsyncClient, Depends(get_db)]
