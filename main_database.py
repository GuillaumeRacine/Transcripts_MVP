#!/usr/bin/env python3
"""
YouTube to Notion Transcript Processor - Simplified Main Entry Point

A streamlined application that monitors Notion databases for YouTube videos
and automatically generates AI-powered summaries.
"""

import logging
import sys
from typing import Optional
from datetime import datetime

from src.config import settings
from src.youtube.playlist_fetcher import PlaylistFetcher
from src.transcript.extractor import TranscriptExtractor
from src.summarizer.llm_summarizer import SummarizerFactory
from src.notion.database_client import NotionDatabaseClient
from src.database.models import Database
from src.scheduler.scheduler import TranscriptScheduler
from src.backup.markdown_backup import MarkdownBackup

# Clean logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('transcripts_app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Suppress verbose logging from libraries
for lib in ['googleapiclient.discovery_cache', 'httpx', 'src.notion.database_client', 
           'src.youtube.playlist_fetcher', 'src.transcript.extractor', 
           'src.summarizer.llm_summarizer', 'src.backup.markdown_backup']:
    logging.getLogger(lib).setLevel(logging.WARNING)


class VideoProcessor:
    """Simplified video processor with clean separation of concerns."""
    
    def __init__(self):
        """Initialize all components with validation."""
        self._validate_config()
        self._init_components()
        
    def _validate_config(self):
        """Validate required configuration."""
        if not settings.notion_database_id:
            raise ValueError("NOTION_DATABASE_ID must be configured")
        if not (settings.openai_api_key or settings.anthropic_api_key):
            raise ValueError("Either OPENAI_API_KEY or ANTHROPIC_API_KEY must be configured")
    
    def _init_components(self):
        """Initialize all service components."""
        # YouTube components
        self.youtube_fetcher = PlaylistFetcher(
            api_key=settings.youtube_api_key,
            service_account_file=settings.youtube_service_account_file
        )
        self.transcript_extractor = TranscriptExtractor()
        
        # LLM summarizer
        provider = settings.llm_provider
        api_key = settings.anthropic_api_key if provider == 'anthropic' else settings.openai_api_key
        self.summarizer = SummarizerFactory.create_summarizer(provider, api_key)
        
        # Storage components
        self.notion_client = NotionDatabaseClient(settings.notion_token, settings.notion_database_id)
        self.db = Database(settings.database_url)
        self.markdown_backup = MarkdownBackup()
        
        # Verify schema
        if not self.notion_client.setup_database_schema():
            logger.warning("Database schema validation failed - some features may not work correctly")
    
    def process_single_video(self, video_record: dict, force_reprocess: bool = False) -> bool:
        """Process a single video with clean error handling."""
        page_id = video_record['page_id']
        video_id = video_record['video_id']
        title = video_record.get('title', video_id)
        
        logger.info(f"Processing: {title[:50]}...")
        
        try:
            # Step 1: Update status and fetch details
            self.notion_client.update_video_status(page_id, "Processing")
            video_info = self._fetch_video_details(video_id)
            if not video_info:
                return self._handle_error(page_id, video_id, "Could not fetch video details")
            
            # Step 2: Get or extract transcript
            transcript = self._get_transcript(video_id, force_reprocess)
            if not transcript:
                return self._handle_error(page_id, video_id, "No transcript available")
            
            # Step 3: Generate summary
            summary = self._generate_summary(transcript, video_info)
            
            # Step 4: Create summary page
            success = self._create_summary_page(video_info, summary, transcript)
            
            # Step 5: Update final status
            self._finalize_processing(page_id, video_id, video_info, success)
            
            logger.info(f"Completed: {title[:50]}")
            return True
            
        except Exception as e:
            return self._handle_error(page_id, video_id, str(e))
    
    def _fetch_video_details(self, video_id: str) -> Optional[dict]:
        """Fetch video details from YouTube API."""
        logger.info("   Fetching video details...")
        return self.youtube_fetcher.get_video_details(video_id)
    
    def _get_transcript(self, video_id: str, force_reprocess: bool) -> Optional[str]:
        """Get transcript from cache or extract fresh one."""
        if not force_reprocess and self.db.is_video_processed(video_id):
            logger.info("   Using cached transcript")
            db_record = self.db.get_processed_video_dict(video_id)
            if db_record and db_record.get('transcript'):
                return db_record['transcript']
        
        logger.info("   Extracting transcript...")
        transcript = self.transcript_extractor.extract_transcript(video_id)
        if transcript:
            # Cache the transcript
            self.db.add_processed_video({
                'video_id': video_id,
                'title': 'Processing...',
                'transcript_extracted': True,
                'transcript': transcript
            })
        return transcript
    
    def _generate_summary(self, transcript: str, video_info: dict) -> str:
        """Generate AI summary using configured provider."""
        logger.info("   Generating AI summary...")
        summary = self.summarizer.summarize(
            transcript=transcript,
            instructions=settings.summary_instructions,
            video_metadata=video_info
        )
        
        word_count = len(summary.split())
        logger.info(f"   Generated {word_count} word summary")
        return summary
    
    def _create_summary_page(self, video_info: dict, summary: str, transcript: str) -> bool:
        """Create Notion summary page with fallback to markdown."""
        logger.info("   Creating Notion page...")
        
        try:
            parent_page_id = settings.notion_summaries_parent_page_id
            response = self.notion_client.create_summary_page(
                title=video_info['title'],
                content=summary,
                video_metadata=video_info,
                parent_page_id=parent_page_id
            )
            
            if response:
                logger.info("   Summary page created!")
                return True
            else:
                raise Exception("Failed to create summary page")
                
        except Exception as e:
            logger.error(f"Summary page creation failed: {str(e)}")
            logger.info("Creating markdown backup instead...")
            
            try:
                backup_path = self.markdown_backup.create_backup(
                    video_info=video_info,
                    summary=summary,
                    transcript=transcript
                )
                logger.info(f"Markdown backup created: {backup_path}")
                return False  # Notion creation failed, but backup succeeded
            except Exception as backup_error:
                logger.error(f"Markdown backup also failed: {str(backup_error)}")
                return False
    
    def _finalize_processing(self, page_id: str, video_id: str, video_info: dict, notion_success: bool):
        """Update final status in both Notion and local database."""
        self.notion_client.update_video_status(
            page_id, "Completed",
            processed_date=datetime.now()
        )
        
        self.db.update_video_status(
            video_id,
            summary_generated=True,
            notion_page_created=notion_success
        )
    
    def _handle_error(self, page_id: str, video_id: str, error_message: str) -> bool:
        """Handle processing errors with proper logging and status updates."""
        logger.error(f"Error processing video {video_id}: {error_message}")
        
        self.notion_client.update_video_status(page_id, "Error", error_message=error_message)
        self.db.update_video_status(video_id, error_message=error_message)
        return False
    
    def check_and_process_videos(self, force_reprocess: bool = False):
        """Main processing loop - check for new videos and process them."""
        logger.info("\\nChecking for new videos in Notion...")
        
        try:
            unprocessed_videos = self.notion_client.get_unprocessed_videos()
            
            if not unprocessed_videos:
                logger.info("No new videos found")
                return
            
            logger.info(f"\\nFound {len(unprocessed_videos)} videos to process\\n")
            
            # Process each video
            stats = {'processed': 0, 'errors': 0, 'skipped': 0}
            
            for i, video_record in enumerate(unprocessed_videos):
                title = video_record.get('title', 'Untitled')
                logger.info(f"\\n[{i+1}/{len(unprocessed_videos)}] {title[:60]}")
                
                result = self.process_single_video(video_record, force_reprocess)
                if result is True:
                    stats['processed'] += 1
                elif result is False:
                    stats['errors'] += 1
                else:  # None means skipped due to rate limits
                    stats['skipped'] += 1
            
            # Final summary
            logger.info(f"\\nSummary: {stats['processed']} processed, {stats['errors']} errors, {stats['skipped']} skipped")
            
            if stats['skipped'] > 0:
                logger.info(f"{stats['skipped']} videos were skipped due to rate limits. Run again later to process them.")
                
        except Exception as e:
            logger.error(f"Error checking database: {str(e)}")
            raise
    
    def close(self):
        """Clean up resources."""
        self.db.close()


def main():
    """Main entry point with argument parsing."""
    import argparse
    
    print("\\nYouTube to Notion Transcript Processor")
    print("-" * 40)
    
    parser = argparse.ArgumentParser(description='YouTube Transcript to Notion Database Processor')
    parser.add_argument('--once', action='store_true', help='Run once instead of scheduling')
    parser.add_argument('--reprocess', action='store_true', help='Force reprocessing of already processed videos')
    parser.add_argument('--interval', type=int, help='Check interval in minutes (overrides env setting)')
    
    args = parser.parse_args()
    
    try:
        processor = VideoProcessor()
        
        if args.once:
            # Run once and exit
            processor.check_and_process_videos(force_reprocess=args.reprocess)
        else:
            # Run continuously
            if args.interval:
                interval_hours = args.interval / 60.0
                logger.info(f"\\nStarting continuous monitor (checking every {args.interval} minutes)")
            else:
                interval_hours = settings.check_interval_hours
                logger.info(f"\\nStarting continuous monitor (checking every {interval_hours} hours)")
            
            scheduler = TranscriptScheduler(
                check_function=lambda: processor.check_and_process_videos(force_reprocess=args.reprocess),
                interval_hours=interval_hours
            )
            logger.info("Press Ctrl+C to stop\\n")
            scheduler.start(run_immediately=True)
        
    except KeyboardInterrupt:
        logger.info("\\nApplication stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    finally:
        if 'processor' in locals():
            processor.close()


if __name__ == "__main__":
    main()