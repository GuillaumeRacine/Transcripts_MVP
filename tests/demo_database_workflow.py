#!/usr/bin/env python3
"""
Demo script showing the complete database workflow with mock data
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

def demo_complete_workflow():
    """Demonstrate the complete workflow with status updates"""
    
    logger.info("🎬 Demo: Complete Database Workflow")
    
    try:
        # Initialize database client
        db_client = NotionDatabaseClient(settings.notion_token, settings.notion_database_id)
        
        # Get unprocessed videos
        logger.info("1️⃣ Checking for unprocessed videos...")
        unprocessed = db_client.get_unprocessed_videos()
        
        if not unprocessed:
            logger.info("❌ No unprocessed videos found")
            logger.info("💡 Add a YouTube URL to your database first!")
            return False
        
        video = unprocessed[0]
        page_id = video['page_id']
        video_id = video['video_id']
        
        logger.info(f"📹 Found video: {video.get('title', 'Untitled')} ({video_id})")
        
        # Simulate the processing workflow
        logger.info("2️⃣ Updating status to 'Processing'...")
        db_client.update_video_status(page_id, "Processing")
        
        # Mock video metadata (normally from YouTube API)
        mock_metadata = {
            'video_id': video_id,
            'title': 'Mock Video: How to Build Great Products',
            'channel_title': 'Tech Talks',
            'published_at': '2024-01-15T10:00:00Z',
            'duration': 'PT45M30S',
            'view_count': 125000,
            'description': 'A comprehensive guide to building products that users love.'
        }
        
        logger.info("3️⃣ Adding video metadata...")
        db_client.update_video_status(
            page_id, "Processing",
            title=mock_metadata['title'],
            video_id=video_id,
            channel=mock_metadata['channel_title'],
            duration="45 minutes"
        )
        
        # Mock summary (normally from LLM)
        mock_summary = f"""# {mock_metadata['title']}

## Executive Summary

This video provides a comprehensive framework for building products that truly resonate with users. The speaker emphasizes the importance of user-centered design and iterative development.

## Key Insights

### 1. Start with User Problems
- Always begin by identifying real user pain points
- Conduct thorough user research before building anything
- Validate problems through direct user interviews

### 2. Build, Measure, Learn
- Create minimum viable products (MVPs) to test hypotheses
- Use data-driven decision making
- Iterate quickly based on user feedback

### 3. Focus on User Experience
- Design for simplicity and ease of use
- Prioritize user flows over feature complexity
- Test usability with real users regularly

## Actionable Takeaways

1. **User Research**: Spend at least 20% of development time on user research
2. **MVP Approach**: Launch with core features only, expand based on usage
3. **Feedback Loops**: Implement multiple ways to collect user feedback
4. **Data Analytics**: Track key metrics from day one
5. **Iterative Design**: Plan for continuous improvement cycles

## Resources Mentioned

- Book: "The Lean Startup" by Eric Ries
- Framework: Jobs-to-be-Done methodology
- Tool: UserVoice for feedback collection
- Metric: Net Promoter Score (NPS)

## Source
**YouTube URL**: https://www.youtube.com/watch?v={video_id}
**Channel**: {mock_metadata['channel_title']}
**Published**: January 15, 2024
"""
        
        logger.info("4️⃣ Creating summary page...")
        summary_response = db_client.create_summary_page(
            title=f"Summary: {mock_metadata['title']}",
            content=mock_summary,
            video_metadata=mock_metadata
        )
        
        if summary_response:
            summary_page_id = summary_response['id']
            logger.info(f"✅ Summary page created: {summary_page_id}")
        else:
            summary_page_id = "Failed to create"
            logger.error("❌ Summary page creation failed")
        
        logger.info("5️⃣ Updating final status...")
        from datetime import datetime
        db_client.update_video_status(
            page_id, "Completed",
            processed_date=datetime.now(),
            summary_page_id=summary_page_id
        )
        
        logger.info("🎉 Workflow completed successfully!")
        logger.info(f"📋 Check your database - video should now show 'Completed' status")
        logger.info(f"📄 Summary page created in Notion")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = demo_complete_workflow()
    
    if success:
        logger.info("\n✨ Database workflow demonstration complete!")
        logger.info("\n🔄 How the real workflow works:")
        logger.info("1. Add YouTube URLs to your Notion database")
        logger.info("2. Run: python main_database.py --once")
        logger.info("3. App detects new videos and processes them")
        logger.info("4. Status updates automatically in your database")
        logger.info("5. Summary pages created with AI-generated content")
        logger.info("6. If errors occur, they're logged in the Error column")
    else:
        logger.error("Demo failed - check your database setup")