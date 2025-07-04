#!/usr/bin/env python3
"""
Test script for the new database-driven workflow
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

def test_database_connection():
    """Test connection to Notion database"""
    logger.info("🚀 Testing Database Connection")
    
    try:
        if not settings.notion_database_id:
            logger.error("❌ NOTION_DATABASE_ID not configured")
            return False
        
        # Initialize database client
        db_client = NotionDatabaseClient(settings.notion_token, settings.notion_database_id)
        
        # Test schema validation
        logger.info("🔍 Checking database schema...")
        schema_valid = db_client.setup_database_schema()
        
        if not schema_valid:
            logger.error("❌ Database schema validation failed")
            logger.info("Please create a Notion database with these properties:")
            logger.info("  - Title (Title)")
            logger.info("  - Video URL (URL)")
            logger.info("  - Video ID (Text)")
            logger.info("  - Status (Select) with options: Processing, Completed, Error, Rate Limited")
            logger.info("  - Channel (Text)")
            logger.info("  - Duration (Text)")
            logger.info("  - Processed Date (Date)")
            logger.info("  - Summary Page (Text)")
            logger.info("  - Error (Text)")
            return False
        
        # Test getting unprocessed videos
        logger.info("📋 Checking for unprocessed videos...")
        unprocessed = db_client.get_unprocessed_videos()
        
        logger.info(f"✅ Found {len(unprocessed)} unprocessed videos")
        
        if unprocessed:
            logger.info("Unprocessed videos:")
            for i, video in enumerate(unprocessed[:5]):  # Show first 5
                logger.info(f"  {i+1}. {video.get('title', 'Untitled')} ({video['video_id']})")
                logger.info(f"      URL: {video['video_url']}")
                logger.info(f"      Status: {video.get('status', 'None')}")
        else:
            logger.info("No unprocessed videos found. Add some video URLs to your database!")
        
        # Test URL parsing
        logger.info("🔗 Testing URL parsing...")
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ"
        ]
        
        for url in test_urls:
            video_id = db_client.extract_video_id_from_url(url)
            logger.info(f"  {url} -> {video_id}")
        
        logger.info("✅ Database connection test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_test_database_entry():
    """Create a test entry in the database"""
    logger.info("🧪 Creating test database entry...")
    
    try:
        db_client = NotionDatabaseClient(settings.notion_token, settings.notion_database_id)
        
        # Test video (Rick Astley)
        test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        logger.info(f"This would create an entry for: {test_video_url}")
        logger.info("Please manually add this URL to your Notion database to test the workflow")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test entry creation failed: {str(e)}")
        return False

def check_configuration():
    """Check if all required configuration is present"""
    logger.info("🔍 Checking configuration...")
    
    missing = []
    
    if not os.path.exists("youtube_service_account.json"):
        missing.append("youtube_service_account.json")
    
    if not settings.notion_token:
        missing.append("NOTION_TOKEN")
    
    if not settings.notion_database_id:
        missing.append("NOTION_DATABASE_ID")
    
    if not settings.openai_api_key and not settings.anthropic_api_key:
        missing.append("OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    if missing:
        logger.error(f"❌ Missing configuration: {', '.join(missing)}")
        return False
    
    logger.info("✅ All configuration present")
    return True

if __name__ == "__main__":
    logger.info("🎯 Database Workflow Test")
    
    # Check configuration
    if not check_configuration():
        logger.error("❌ Configuration check failed")
        sys.exit(1)
    
    # Test database connection
    success = test_database_connection()
    
    if success:
        logger.info("\n🎉 Database workflow test completed successfully!")
        logger.info("\n📝 Next steps:")
        logger.info("1. Create a Notion database with the required properties")
        logger.info("2. Add some YouTube video URLs to the database")
        logger.info("3. Run: python main_database.py --once")
        logger.info("4. Check your database for processed videos!")
    else:
        logger.error("\n💥 Database workflow test failed!")
        sys.exit(1)