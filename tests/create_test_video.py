#!/usr/bin/env python3
"""
Create a test video entry in the correct format
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

def create_test_video():
    """Create a properly formatted test video entry"""
    
    try:
        # Initialize database client
        db_client = NotionDatabaseClient(settings.notion_token, settings.notion_database_id)
        
        # Create a new page with proper format
        test_url = "https://www.youtube.com/watch?v=9bZkp7q19f0"  # Gangnam Style
        
        logger.info(f"Creating test video entry: {test_url}")
        
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
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create test video: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_test_video()