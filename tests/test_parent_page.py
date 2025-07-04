#!/usr/bin/env python3
"""
Test creating summary pages under the specified parent page
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import settings
from src.notion.database_client import NotionDatabaseClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_parent_page():
    """Test creating a video entry and processing it to the parent page"""
    
    try:
        # Initialize database client
        db_client = NotionDatabaseClient(settings.notion_token, settings.notion_database_id)
        
        # Use a different test video
        test_url = "https://www.youtube.com/watch?v=kJQP7kiw5Fk"  # Despacito
        
        logger.info(f"Creating test video for parent page: {test_url}")
        logger.info(f"Parent page ID: {settings.notion_summaries_parent_page_id}")
        
        # Create page using Notion API directly
        response = db_client.client.pages.create(
            parent={"database_id": settings.notion_database_id},
            properties={
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": ""  # Empty title - will be filled by processor
                            }
                        }
                    ]
                },
                "Video URL": {
                    "url": test_url
                }
            }
        )
        
        logger.info(f"✅ Created test entry: {response['id']}")
        logger.info(f"🔗 Video URL: {test_url}")
        logger.info("Now run: python main_database.py --once")
        logger.info("The summary page should be created under your Transcripts parent page!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create test video: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_parent_page()