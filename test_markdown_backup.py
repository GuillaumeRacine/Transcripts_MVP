#!/usr/bin/env python3
"""
Test script for markdown backup system
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.backup.markdown_backup import MarkdownBackup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_markdown_backup():
    """Test the markdown backup system"""
    logger.info("=== Testing Markdown Backup System ===")
    
    # Create test backup directory
    backup_dir = "test_markdown_backups"
    backup_system = MarkdownBackup(backup_dir)
    
    # Test video info
    video_info = {
        'video_id': 'dQw4w9WgXcQ',
        'title': 'Rick Astley - Never Gonna Give You Up (Official Video)',
        'channel_title': 'Rick Astley',
        'published_at': '2009-10-25T06:57:33Z',
        'description': 'The official video for "Never Gonna Give You Up" by Rick Astley. "Never Gonna Give You Up" was a global smash on its release in July 1987, topping the charts in 25 countries including Rick\'s native UK and the US Billboard Hot 100.'
    }
    
    # Test summary
    summary = """# Video Summary

## Key Points
- This is a test summary of the famous Rick Astley video
- The song became a global hit in 1987
- It's known for the "Rickrolling" internet meme

## Main Topics
1. **Music Video Production**: The classic 1980s style video
2. **Cultural Impact**: How it became an internet phenomenon
3. **Legacy**: Its continued popularity decades later

## Actionable Takeaways
- Classic songs can have unexpected second lives online
- Simple, memorable content often has the most lasting impact
- The internet can transform any content into a cultural phenomenon
"""
    
    # Test transcript
    transcript = """We're no strangers to love
You know the rules and so do I
A full commitment's what I'm thinking of
You wouldn't get this from any other guy

I just wanna tell you how I'm feeling
Gotta make you understand

Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you"""
    
    try:
        # Test creating backup
        logger.info("Creating markdown backup...")
        backup_path = backup_system.create_backup(video_info, summary, transcript)
        logger.info(f"✅ Backup created at: {backup_path}")
        
        # Test listing backups
        logger.info("Listing backups...")
        backups = backup_system.list_backups()
        logger.info(f"✅ Found {len(backups)} backup(s)")
        
        # Test getting stats
        logger.info("Getting backup stats...")
        stats = backup_system.get_backup_stats()
        logger.info(f"✅ Backup stats: {stats}")
        
        # Test reading the created file
        logger.info("Reading backup file...")
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"✅ Backup file content ({len(content)} characters):")
        logger.info("--- First 500 characters ---")
        logger.info(content[:500])
        logger.info("--- End of preview ---")
        
        # Test backup without transcript
        logger.info("Creating backup without transcript...")
        backup_path_2 = backup_system.create_backup(video_info, summary)
        logger.info(f"✅ Second backup created at: {backup_path_2}")
        
        # Test cleanup
        logger.info("Testing cleanup...")
        removed = backup_system.cleanup_old_backups(max_backups=1)
        logger.info(f"✅ Cleaned up {removed} old backup(s)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False
    
    finally:
        # Clean up test directory
        try:
            import shutil
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
                logger.info(f"🧹 Cleaned up test directory: {backup_dir}")
        except Exception as e:
            logger.warning(f"Could not clean up test directory: {str(e)}")

if __name__ == "__main__":
    logger.info("🚀 Starting Markdown Backup Tests")
    
    success = test_markdown_backup()
    
    if success:
        logger.info("✅ All markdown backup tests passed!")
    else:
        logger.error("❌ Markdown backup tests failed!")
        sys.exit(1)