import logging
from typing import List, Union, Optional

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, Field, parse_obj_as, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Set up logging
log_format = logging.Formatter("%(asctime)s : %(levelname)s - %(message)s")

# Root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Standard stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)
load_dotenv()

# Default URL as parsed AnyHttpUrl
DEFAULT_SERVER_HOST = parse_obj_as(AnyHttpUrl, "http://localhost:8000")


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Supabase Template"
    VERSION: str = "0.1.0"

    # Supabase Settings
    SUPABASE_URL: str = Field(
        default="",
        description="Supabase URL"
    )
    SUPABASE_KEY: str = Field(
        default="",
        description="Supabase Key"
    )
    SUPABASE_SERVICE_KEY: Optional[str] = Field(
        default=None,
        description="Supabase Service Key"
    )

    # User Settings
    SUPERUSER_EMAIL: str = Field(
        default="",
        description="Superuser email"
    )
    SUPERUSER_PASSWORD: str = Field(
        default="",
        description="Superuser password"
    )

    # Server Settings
    SERVER_HOST: AnyHttpUrl = Field(default=DEFAULT_SERVER_HOST)
    SERVER_PORT: int = 8000

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[AnyHttpUrl]:
        if isinstance(v, str) and not v.startswith("["):
            return [parse_obj_as(AnyHttpUrl, i.strip()) for i in v.split(",")]
        elif isinstance(v, list):
            return [parse_obj_as(AnyHttpUrl, i) for i in v]
        return []

    # Pydantic Config
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        arbitrary_types_allowed=True
    )


settings = Settings()
