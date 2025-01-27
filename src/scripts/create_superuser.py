"""Script to create a superuser in Supabase with admin role"""
import asyncio
import logging
from typing import Dict, Any

from supabase._async.client import AsyncClient, create_client
from supabase.lib.client_options import AsyncClientOptions
from gotrue.errors import AuthApiError

from ..core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_superuser() -> None:
    """Create a superuser in Supabase if it doesn't exist"""
    if not settings.SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_SERVICE_KEY is required for admin operations")

    try:
        # Initialize Supabase client with service role key
        admin_client: AsyncClient = await create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY,  # Use service role key for admin operations
            options=AsyncClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
            ),
        )

        # Initialize regular client for testing
        user_client: AsyncClient = await create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
            options=AsyncClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
            ),
        )

        # First try to sign in
        try:
            response = await user_client.auth.sign_in_with_password({
                "email": settings.SUPERUSER_EMAIL,
                "password": settings.SUPERUSER_PASSWORD
            })
            logger.info(f"Superuser already exists: {settings.SUPERUSER_EMAIL}")
            
            # Update metadata if needed using admin client
            user = response.user
            if not user.user_metadata or "roles" not in user.user_metadata:
                await admin_client.auth.admin.update_user_by_id(
                    user.id,
                    {"user_metadata": {"roles": ["admin"], "is_superuser": True}}
                )
                logger.info("Updated superuser metadata with admin role")
            
            return
            
        except AuthApiError as e:
            if "Invalid login credentials" not in str(e):
                raise e
            
            # User doesn't exist, create it using admin client
            logger.info("Creating new superuser...")
            
            # Create user with admin role
            user_metadata: Dict[str, Any] = {
                "roles": ["admin"],
                "is_superuser": True
            }
            
            response = await admin_client.auth.admin.create_user({
                "email": settings.SUPERUSER_EMAIL,
                "password": settings.SUPERUSER_PASSWORD,
                "email_confirm": True,  # Auto-confirm email
                "user_metadata": user_metadata
            })
            
            logger.info(f"Successfully created superuser: {settings.SUPERUSER_EMAIL}")
            
    except Exception as e:
        logger.error(f"Failed to create superuser: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(create_superuser())
