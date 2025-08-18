import os
from dotenv import load_dotenv
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default=os.getenv(
            key="DATABASE_URL",
            default="postgresql://postgres:postgres@localhost:5432/postgres"
        ),
        description="Database connection URL"
    )

    # JWT Security
    secret_key: str = Field(
        default=str(os.getenv(
            key="JWT_SECRET_KEY",
            default="your-secret-key-change-in-production"
        )),
        description="Secret key for JWT"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Token expiration time in minutes"
    )

    # External APIs
    tmdb_api_key: str = Field(
        default="",
        description="TMDB API key"
    )

    # Application
    debug: bool = Field(default=True, description="Modo debug")
    log_level: str = Field(default="INFO", description="Log level")

    # API
    api_v1_str: str = Field(default="/api/v1", description="API prefix")
    project_name: str = Field(
        default="Rurax - Movie Recommendation System",
        description="Project name",
    )

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields instead of generating an error
    )


# Global instance of settings
settings = Settings()
