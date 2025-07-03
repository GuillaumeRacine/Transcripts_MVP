#!/usr/bin/env python3
"""
Test script to process a single video and create a Notion page
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import settings
from src.youtube.playlist_fetcher import PlaylistFetcher
from src.transcript.extractor import TranscriptExtractor
from src.summarizer.llm_summarizer import SummarizerFactory
from src.notion.client import NotionClient
from src.backup.markdown_backup import MarkdownBackup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_video_processing():
    """Test processing a single video end-to-end"""
    logger.info("🚀 Testing Single Video Processing")
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        
        # YouTube API with service account
        playlist_fetcher = PlaylistFetcher(
            service_account_file="./youtube_service_account.json"
        )
        
        # Transcript extractor
        transcript_extractor = TranscriptExtractor()
        
        # LLM summarizer
        if settings.llm_provider == 'openai' and settings.openai_api_key:
            summarizer = SummarizerFactory.create_summarizer('openai', settings.openai_api_key)
            logger.info("✅ Using OpenAI for summarization")
        elif settings.llm_provider == 'anthropic' and settings.anthropic_api_key:
            summarizer = SummarizerFactory.create_summarizer('anthropic', settings.anthropic_api_key)
            logger.info("✅ Using Anthropic for summarization")
        else:
            logger.error("❌ No LLM provider configured")
            return False
        
        # Notion client
        notion_client = NotionClient(settings.notion_token, settings.notion_page_id)
        
        # Markdown backup
        markdown_backup = MarkdownBackup()
        
        # Get a video from your playlist
        logger.info("Fetching video from your playlist...")
        videos = playlist_fetcher.get_playlist_videos(settings.youtube_playlist_id, max_results=1)
        
        if not videos:
            logger.error("❌ No videos found in playlist")
            return False
        
        video_info = videos[0]
        video_id = video_info['video_id']
        
        logger.info(f"📹 Processing: {video_info['title']} ({video_id})")
        
        # Check if video already exists in Notion
        if notion_client.check_if_video_exists(video_id):
            logger.info("⚠️ Video already exists in Notion, skipping...")
            return True
        
        # Extract transcript
        logger.info("📝 Extracting transcript...")
        transcript = transcript_extractor.extract_transcript(video_id)
        
        if not transcript:
            logger.error("❌ Could not extract transcript (may be rate limited)")
            return False
        
        logger.info(f"✅ Transcript extracted ({len(transcript)} characters)")
        
        # Generate summary
        logger.info("🤖 Generating AI summary...")
        summary = summarizer.summarize(
            transcript=transcript,
            instructions=settings.summary_instructions,
            video_metadata=video_info
        )
        
        logger.info(f"✅ Summary generated ({len(summary)} characters)")
        
        # Create Notion page
        logger.info("📄 Creating Notion page...")
        page_title = f"{video_info['title']} [{video_id}]"
        
        try:
            notion_response = notion_client.create_page(
                title=page_title,
                content=summary,
                video_metadata=video_info
            )
            
            logger.info("✅ Notion page created successfully!")
            logger.info(f"   Page ID: {notion_response['id']}")
            logger.info(f"   Page URL: {notion_response.get('url', 'N/A')}")
            
            return True
            
        except Exception as notion_error:
            logger.error(f"❌ Notion page creation failed: {str(notion_error)}")
            logger.info("📋 Creating markdown backup instead...")
            
            # Create markdown backup
            backup_path = markdown_backup.create_backup(
                video_info=video_info,
                summary=summary,
                transcript=transcript
            )
            
            logger.info(f"✅ Markdown backup created: {backup_path}")
            return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_configuration():
    """Check if all required configuration is present"""
    logger.info("🔍 Checking configuration...")
    
    missing = []
    
    if not os.path.exists("youtube_service_account.json"):
        missing.append("youtube_service_account.json")
    
    if not settings.youtube_playlist_id:
        missing.append("YOUTUBE_PLAYLIST_ID")
    
    if not settings.notion_token:
        missing.append("NOTION_TOKEN")
    
    if not settings.notion_page_id:
        missing.append("NOTION_PAGE_ID")
    
    if not settings.openai_api_key and not settings.anthropic_api_key:
        missing.append("OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    if missing:
        logger.error(f"❌ Missing configuration: {', '.join(missing)}")
        return False
    
    logger.info("✅ All configuration present")
    return True

if __name__ == "__main__":
    logger.info("🎯 Single Video Processing Test")
    
    # Check configuration
    if not check_configuration():
        logger.error("❌ Configuration check failed")
        sys.exit(1)
    
    # Run the test
    success = test_single_video_processing()
    
    if success:
        logger.info("\n🎉 Single video processing test completed successfully!")
        logger.info("Check your Notion page to see the generated summary.")
    else:
        logger.error("\n💥 Single video processing test failed!")
        sys.exit(1)