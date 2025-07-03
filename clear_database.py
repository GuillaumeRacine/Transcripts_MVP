#!/usr/bin/env python3
"""Clear the database to start fresh"""

from src.database.models import Database, ProcessedVideo
from src.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_database():
    """Clear all processed videos from the database"""
    try:
        db = Database(settings.database_url)
        
        # Get count before clearing
        videos = db.get_all_processed_videos()
        count = len(videos)
        
        if count == 0:
            logger.info("Database is already empty")
            return
        
        logger.info(f"Found {count} videos in database")
        
        # Clear all videos
        for video in videos:
            db.session.delete(video)
        
        db.session.commit()
        db.close()
        
        logger.info(f"✅ Cleared {count} videos from database")
        
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        raise

if __name__ == "__main__":
    clear_database()