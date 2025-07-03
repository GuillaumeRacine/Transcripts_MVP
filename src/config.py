from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # YouTube API Configuration
    youtube_api_key: Optional[str] = Field(None, env="YOUTUBE_API_KEY")
    youtube_service_account_file: Optional[str] = Field(None, env="YOUTUBE_SERVICE_ACCOUNT_FILE")
    youtube_playlist_id: str = Field(..., env="YOUTUBE_PLAYLIST_ID")
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    llm_provider: str = Field("openai", env="LLM_PROVIDER")
    
    # Notion Configuration
    notion_token: str = Field(..., env="NOTION_TOKEN")
    notion_page_id: Optional[str] = Field(None, env="NOTION_PAGE_ID")  # For legacy page-based workflow
    notion_database_id: Optional[str] = Field(None, env="NOTION_DATABASE_ID")  # For new database workflow
    
    # Database Configuration
    database_url: str = Field("sqlite:///./transcripts.db", env="DATABASE_URL")
    
    # Scheduler Configuration
    check_interval_hours: int = Field(24, env="CHECK_INTERVAL_HOURS")
    
    # Summary Configuration
    summary_instructions: str = Field(
        "Provide a concise summary of the video transcript focusing on key insights, "
        "main topics discussed, and actionable takeaways. Format the output with clear "
        "headers and bullet points.",
        env="SUMMARY_INSTRUCTIONS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()