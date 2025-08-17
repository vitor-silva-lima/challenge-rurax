from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/postgres",
        description="Database connection URL"
    )

    # JWT Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
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

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global instance of settings
settings = Settings()
