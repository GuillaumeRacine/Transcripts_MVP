from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # YouTube API Configuration
    youtube_api_key: Optional[str] = Field(None, env="YOUTUBE_API_KEY")
    youtube_service_account_file: Optional[str] = Field("./youtube_service_account.json", env="YOUTUBE_SERVICE_ACCOUNT_FILE")
    youtube_playlist_id: Optional[str] = Field(None, env="YOUTUBE_PLAYLIST_ID")
    
    # LLM Configuration (Claude 3 Opus)
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    
    # Notion Configuration
    notion_token: str = Field(..., env="NOTION_TOKEN")
    notion_database_id: str = Field(..., env="NOTION_DATABASE_ID")
    notion_summaries_parent_page_id: Optional[str] = Field(None, env="NOTION_SUMMARIES_PARENT_PAGE_ID")
    
    # Database Configuration
    database_url: str = Field("sqlite:///./transcripts.db", env="DATABASE_URL")
    
    # Scheduler Configuration
    check_interval_hours: float = Field(0.25, env="CHECK_INTERVAL_HOURS")  # 15 minutes = 0.25 hours
    
    # API Rate Limiting Configuration - Ultra-conservative settings for 99% reliability
    api_call_delay: float = Field(10.0, env="API_CALL_DELAY", description="Delay between API calls in seconds")
    video_processing_delay: int = Field(60, env="VIDEO_PROCESSING_DELAY", description="Base delay between processing videos in seconds")
    error_backoff_multiplier: int = Field(30, env="ERROR_BACKOFF_MULTIPLIER", description="Additional delay per error in seconds")
    max_processing_delay: int = Field(600, env="MAX_PROCESSING_DELAY", description="Maximum delay between videos in seconds")
    max_retries: int = Field(10, env="MAX_RETRIES", description="Maximum retry attempts for API calls")
    base_backoff: int = Field(10, env="BASE_BACKOFF", description="Base backoff time for retries in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()