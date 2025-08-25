"""
Application configuration and settings management.

This module provides centralized configuration management for the
MoneyFlow application, including database, AI, processing, UI, and
logging settings.
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# Load environment variables first, before any settings are created
from dotenv import load_dotenv
load_dotenv()


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    # SQLite Settings
    sqlite_db_path: str = Field(default="data/templates.db")
    
    # MongoDB Settings
    mongo_url: str = Field(default="", env="MONGO_URL")
    mongo_database: str = Field(default="excel_imports")
    
    class Config:
        env_prefix = ""


class AISettings(BaseSettings):
    """AI/OpenAI configuration settings."""
    
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-nano")
    openai_max_retries: int = Field(default=3)
    openai_timeout: int = Field(default=30)
    
    class Config:
        env_prefix = ""


class ProcessingSettings(BaseSettings):
    """Data processing configuration settings."""
    
    batch_size: int = Field(default=1000)
    max_file_size_mb: int = Field(default=100)
    max_rows_preview: int = Field(default=10)
    duplicate_strategy: str = Field(default="skip")
    
    class Config:
        env_prefix = ""


class UISettings(BaseSettings):
    """UI configuration settings."""
    
    window_width: int = Field(default=800)
    window_height: int = Field(default=600)
    theme: str = Field(default="light")
    auto_save_schemas: bool = Field(default=True)
    
    class Config:
        env_prefix = ""


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    log_level: str = Field(default="INFO")
    log_file_path: str = Field(default="logs/app.log")
    log_max_size_mb: int = Field(default=10)
    log_backup_count: int = Field(default=5)
    
    class Config:
        env_prefix = ""


class AppSettings(BaseSettings):
    """Main application settings that combines all other settings."""
    
    # App Info
    app_name: str = "MoneyFlow Data Ingestion"
    app_version: str = "1.0.0"
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Component Settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    ai: AISettings = Field(default_factory=AISettings)
    processing: ProcessingSettings = Field(default_factory=ProcessingSettings)
    ui: UISettings = Field(default_factory=UISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = AppSettings()


def get_settings() -> AppSettings:
    """
    Get the global application settings instance.
    
    Returns:
        AppSettings: The global settings instance
    """
    return settings


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path: Project root directory path
    """
    return Path(__file__).parent.parent.parent


def get_data_directory() -> Path:
    """
    Get the data directory path.
    
    Returns:
        Path: Data directory path
    """
    data_dir = get_project_root() / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def get_logs_directory() -> Path:
    """
    Get the logs directory path.
    
    Returns:
        Path: Logs directory path
    """
    logs_dir = get_project_root() / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


def validate_settings() -> bool:
    """
    Validate that all required settings are properly configured.
    
    Returns:
        bool: True if settings are valid, False otherwise
    """
    try:
        # Check required environment variables
        if not settings.ai.openai_api_key:
            print("Warning: OPENAI_API_KEY not set in environment")
            return False
            
        if not settings.database.mongo_url:
            print("Warning: MONGO_URL not set in environment")
            return False
            
        # Check file paths exist
        project_root = get_project_root()
        if not project_root.exists():
            print(f"Error: Project root directory not found: {project_root}")
            return False
            
        # Create required directories
        get_data_directory()
        get_logs_directory()
        
        return True
        
    except Exception as e:
        print(f"Error validating settings: {e}")
        return False
