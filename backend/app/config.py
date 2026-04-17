# =============================================================================
# config.py — Application Configuration
# =============================================================================
# PURPOSE: Centralize all application settings in one type-safe place.
# Uses pydantic-settings to automatically load values from environment
# variables and .env files with validation and type coercion.
#
# PRIORITY ORDER (highest to lowest):
#   1. Environment variables (set in Docker, shell, or CI/CD)
#   2. Values from .env file
#   3. Default values defined below
#
# USAGE:
#   from app.config import settings
#   print(settings.database_url)      # The active DB connection string
#   print(settings.jwt_secret_key)    # The JWT signing secret
# =============================================================================

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Each field maps to an environment variable of the same name (case-insensitive).
    For example, `database_url` reads from the DATABASE_URL env var.
    """

    model_config = SettingsConfigDict(
        env_file=".env",           # Path to .env file (relative to working dir)
        env_file_encoding="utf-8",
        extra="ignore",            # Don't fail on unknown env vars
    )

    # -------------------------------------------------------------------------
    # DATABASE
    # -------------------------------------------------------------------------
    # database_url: Async connection string used by the FastAPI application.
    #   Uses the asyncpg driver for non-blocking database operations.
    # database_url_sync: Synchronous connection string used by Alembic.
    #   Alembic's autogenerate needs a sync connection to inspect the DB schema.
    # -------------------------------------------------------------------------
    database_url: str = "postgresql+asyncpg://energy_user:energy_pass_dev@localhost:5433/energy_platform"
    database_url_sync: str = "postgresql+psycopg2://energy_user:energy_pass_dev@localhost:5433/energy_platform"

    # -------------------------------------------------------------------------
    # JWT AUTHENTICATION
    # -------------------------------------------------------------------------
    # jwt_secret_key: The secret used to sign JWT tokens. MUST be changed in
    #   production to a cryptographically random string (32+ characters).
    # jwt_algorithm: The signing algorithm. HS256 is standard for symmetric keys.
    # jwt_access_token_expire_minutes: Token lifetime. After expiry, the user
    #   must log in again to get a new token.
    # -------------------------------------------------------------------------
    jwt_secret_key: str = "CHANGE-ME-IN-PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # -------------------------------------------------------------------------
    # APPLICATION
    # -------------------------------------------------------------------------
    # app_name: Displayed in the Swagger UI title bar and API metadata.
    # debug: When True, SQLAlchemy logs all SQL queries to stdout.
    # log_level: Controls Python logging verbosity (debug/info/warning/error).
    # -------------------------------------------------------------------------
    app_name: str = "AI Energy Optimization Platform"
    debug: bool = True
    log_level: str = "info"

    # -------------------------------------------------------------------------
    # CORS (Phase 1)
    # -------------------------------------------------------------------------
    allowed_origins: str = "*"

    # -------------------------------------------------------------------------
    # RATE LIMITING (Phase 1)
    # -------------------------------------------------------------------------
    rate_limit_per_minute: int = 100

    # -------------------------------------------------------------------------
    # REDIS (Phase 2)
    # -------------------------------------------------------------------------
    redis_url: str = "redis://localhost:6379/0"

    # -------------------------------------------------------------------------
    # EMAIL / SENDGRID (Phase 2 — Notifications)
    # -------------------------------------------------------------------------
    sendgrid_api_key: str = ""
    from_email: str = "alerts@energyplatform.io"

    @property
    def cors_origins(self) -> list[str]:
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================
settings = Settings()


def validate_production_settings() -> None:
    """Fail fast if JWT secret is the default in non-debug mode."""
    if not settings.debug and settings.jwt_secret_key == "CHANGE-ME-IN-PRODUCTION":
        raise RuntimeError(
            "FATAL: jwt_secret_key is the default value and DEBUG=false. "
            "Set a secure JWT_SECRET_KEY environment variable for production."
        )
