#!/usr/bin/env python3
"""
Debug script to see what's in the database
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

def debug_database():
    """Debug what's actually in the database"""
    
    try:
        # Initialize database client
        db_client = NotionDatabaseClient(settings.notion_token, settings.notion_database_id)
        
        # Get all pages (not filtered)
        logger.info("🔍 Getting all pages from database...")
        
        response = db_client.client.databases.query(
            database_id=settings.notion_database_id
        )
        
        logger.info(f"Found {len(response['results'])} total pages")
        
        for i, page in enumerate(response['results']):
            logger.info(f"\n📄 Page {i+1}: {page['id']}")
            properties = page.get("properties", {})
            
            for prop_name, prop_data in properties.items():
                prop_type = prop_data.get("type")
                logger.info(f"  🏷️  {prop_name} ({prop_type}):")
                
                if prop_type == "title":
                    title_texts = prop_data.get("title", [])
                    if title_texts:
                        title = title_texts[0].get("plain_text", "")
                        logger.info(f"       Title: '{title}'")
                    else:
                        logger.info(f"       Title: (empty)")
                
                elif prop_type == "url":
                    url = prop_data.get("url")
                    logger.info(f"       URL: '{url}'")
                
                elif prop_type == "rich_text":
                    rich_text = prop_data.get("rich_text", [])
                    if rich_text:
                        text = rich_text[0].get("plain_text", "")
                        logger.info(f"       Text: '{text}'")
                    else:
                        logger.info(f"       Text: (empty)")
                
                elif prop_type == "select":
                    select_data = prop_data.get("select")
                    if select_data:
                        value = select_data.get("name")
                        logger.info(f"       Select: '{value}'")
                    else:
                        logger.info(f"       Select: (empty)")
                
                else:
                    logger.info(f"       Value: {prop_data}")
        
        # Now test URL extraction
        logger.info("\n🔗 Testing URL extraction...")
        unprocessed = db_client.get_unprocessed_videos()
        logger.info(f"Unprocessed videos found: {len(unprocessed)}")
        
        for video in unprocessed:
            logger.info(f"  📹 {video}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_database()