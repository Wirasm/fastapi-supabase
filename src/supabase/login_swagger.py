"""
This is a temporary endpoint for obtaining a JWT token for testing the API via Swagger UI.
It should be removed in a production environment.

To obtain a JWT token, provide a valid email and password in the request body.

Insert the token as: Bearer <your_token>

Instructions:
1. Enter your Supabase email and password
2. Copy the returned access_token
3. Click the 'Authorize' button at the top
4. Enter the token as: Bearer <your_token>
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from supabase._async.client import AsyncClient, create_client
from supabase.lib.client_options import AsyncClientOptions
from gotrue.errors import AuthApiError

from ..core.config import settings
from .schemas import TokenResponse, UserIn

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        401: {"description": "Invalid credentials"},
        403: {"description": "Forbidden"},
        429: {"description": "Too many requests"},
    }
)

security = HTTPBasic(auto_error=False)

@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Get access token for Swagger testing",
    description="""
    Obtain a JWT token for testing the API via Swagger UI.
    
    **Note**: This endpoint is for development/testing purposes only.
    In production, use the proper authentication flow.
    
    Instructions:
    1. Enter your Supabase email and password
    2. Copy the returned access_token
    3. Click the 'Authorize' button at the top
    4. Enter the token as: Bearer <your_token>
    """,
)
async def get_test_token(credentials: HTTPBasicCredentials = Depends(security)):
    """Get JWT token for Swagger UI testing"""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Please provide credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    try:
        client: AsyncClient = await create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
            options=AsyncClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
            ),
        )
        
        response = await client.auth.sign_in_with_password({
            "email": credentials.username,
            "password": credentials.password
        })
        
        if not response.user or not response.session:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        # Create UserIn instance with enhanced data
        user = UserIn(
            id=response.user.id,
            email=response.user.email,
            roles=response.user.user_metadata.get("roles", ["user"]) if response.user.user_metadata else ["user"],
            metadata=response.user.user_metadata or {},
            is_active=True
        )

        return TokenResponse(
            access_token=response.session.access_token,
            token_type="bearer",
            expires_in=response.session.expires_in,
            refresh_token=response.session.refresh_token,
            user=user
        )

    except AuthApiError as e:
        if "Invalid login credentials" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        elif "Email not confirmed" in str(e):
            raise HTTPException(
                status_code=403,
                detail="Please confirm your email address"
            )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )
