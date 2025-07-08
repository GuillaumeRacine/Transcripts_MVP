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
    check_interval_hours: int = Field(24, env="CHECK_INTERVAL_HOURS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()