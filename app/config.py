"""
Configuration management for Academic Tomorrow Learning Center.

This module handles loading environment variables and application settings
using Pydantic Settings for type-safe configuration management.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DB_HOST: Database host address
        DB_PORT: Database port number
        DB_USER: Database username
        DB_PASSWORD: Database password
        DB_NAME: Database name
        SECRET_KEY: Secret key for session management and security
    """

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str= 'root123'
    DB_NAME: str = "academic_tomorrow"
    SECRET_KEY: str = ''

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: The application settings loaded from environment variables

    Note:
        This function uses lru_cache to ensure settings are loaded only once
    """
    return Settings()
