import logging
import sys
import time
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcripts_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseTranscriptProcessor:
    def __init__(self):
        # Validate configuration
        if not settings.notion_database_id:
            raise ValueError("NOTION_DATABASE_ID must be configured for database-driven workflow")
        
        # Initialize components
        self.youtube_fetcher = PlaylistFetcher(
            api_key=settings.youtube_api_key,
            service_account_file=settings.youtube_service_account_file
        )
        self.transcript_extractor = TranscriptExtractor()
        
        # Initialize LLM summarizer based on provider
        if settings.llm_provider == 'openai' and settings.openai_api_key:
            self.summarizer = SummarizerFactory.create_summarizer('openai', settings.openai_api_key)
        elif settings.llm_provider == 'anthropic' and settings.anthropic_api_key:
            self.summarizer = SummarizerFactory.create_summarizer('anthropic', settings.anthropic_api_key)
        else:
            raise ValueError("No valid LLM provider configured")
        
        self.notion_client = NotionDatabaseClient(settings.notion_token, settings.notion_database_id)
        self.db = Database(settings.database_url)
        self.markdown_backup = MarkdownBackup()
        
        # Verify database schema
        if not self.notion_client.setup_database_schema():
            logger.warning("Database schema validation failed - some features may not work correctly")
    
    def process_video_from_database(self, video_record: dict) -> bool:
        """
        Process a single video from the database record.
        
        Args:
            video_record: Database record with video information
            
        Returns:
            True if successful, False otherwise
        """
        page_id = video_record['page_id']
        video_id = video_record['video_id']
        video_url = video_record['video_url']
        
        logger.info(f"Processing video from database: {video_id}")
        
        try:
            # Update status to processing
            self.notion_client.update_video_status(page_id, "Processing")
            
            # Get video details from YouTube API
            logger.info("Fetching video details from YouTube...")
            video_info = self.youtube_fetcher.get_video_details(video_id)
            
            if not video_info:
                error_msg = f"Could not fetch video details for {video_id}"
                logger.error(error_msg)
                self.notion_client.update_video_status(
                    page_id, "Error", 
                    error_message=error_msg
                )
                return False
            
            # Update database record with video metadata
            self.notion_client.update_video_status(
                page_id, "Processing",
                title=video_info['title'],
                video_id=video_id,
                channel=video_info['channel_title'],
                duration=video_info.get('duration', 'Unknown')
            )
            
            # Check if already processed in local database
            if self.db.is_video_processed(video_id):
                logger.info(f"Video {video_id} already processed locally, skipping transcript extraction.")
                # Still continue to create summary if not done
            else:
                # Extract transcript
                logger.info("Extracting transcript...")
                transcript = self.transcript_extractor.extract_transcript(video_id)
                
                if transcript is None:
                    # Check if this was due to rate limiting
                    status = self.transcript_extractor.rate_limiter.get_status()
                    if status['daily_remaining'] <= 0 or status['hourly_remaining'] <= 0:
                        logger.info(f"Skipping video {video_id} due to rate limits")
                        self.notion_client.update_video_status(
                            page_id, "Rate Limited", 
                            error_message="Skipped due to YouTube API rate limits"
                        )
                        return None  # Skipped due to rate limits
                    else:
                        error_msg = f"No transcript available for video {video_id}"
                        logger.warning(error_msg)
                        self.notion_client.update_video_status(
                            page_id, "Error", 
                            error_message=error_msg
                        )
                        return False
                
                # Update local database
                self.db.add_processed_video({
                    **video_info,
                    'transcript_extracted': True
                })
            
            # Generate summary
            logger.info("Generating summary...")
            summary = self.summarizer.summarize(
                transcript=transcript,
                instructions=settings.summary_instructions,
                video_metadata=video_info
            )
            
            # Create summary page
            logger.info("Creating summary page...")
            page_title = f"{video_info['title']}"
            
            summary_success = False
            summary_page_id = None
            
            try:
                summary_response = self.notion_client.create_summary_page(
                    title=page_title,
                    content=summary,
                    video_metadata=video_info
                )
                
                if summary_response:
                    summary_page_id = summary_response['id']
                    summary_success = True
                    logger.info("✅ Summary page created successfully")
                else:
                    raise Exception("Failed to create summary page")
                    
            except Exception as summary_error:
                logger.error(f"❌ Summary page creation failed: {str(summary_error)}")
                logger.info("Creating markdown backup instead...")
                
                # Create markdown backup
                try:
                    backup_path = self.markdown_backup.create_backup(
                        video_info=video_info,
                        summary=summary,
                        transcript=transcript
                    )
                    logger.info(f"✅ Markdown backup created: {backup_path}")
                    summary_page_id = f"Backup: {backup_path}"
                except Exception as backup_error:
                    logger.error(f"❌ Markdown backup also failed: {str(backup_error)}")
                    summary_page_id = f"Error: {str(backup_error)}"
            
            # Update final status
            self.notion_client.update_video_status(
                page_id, "Completed",
                processed_date=datetime.now(),
                summary_page_id=summary_page_id
            )
            
            # Update local database
            self.db.update_video_status(
                video_id,
                summary_generated=True,
                notion_page_created=summary_success,
                notion_page_id=summary_page_id
            )
            
            logger.info(f"Successfully processed video: {video_info['title']}")
            return True
            
        except Exception as e:
            error_msg = f"Error processing video {video_id}: {str(e)}"
            logger.error(error_msg)
            
            # Update status to error
            self.notion_client.update_video_status(
                page_id, "Error", 
                error_message=str(e)
            )
            
            # Update local database
            self.db.update_video_status(video_id, error_message=str(e))
            return False
    
    def check_and_process_new_videos(self):
        """Check database for new videos and process them."""
        try:
            logger.info("Checking Notion database for new videos...")
            
            # Get unprocessed videos from Notion database
            unprocessed_videos = self.notion_client.get_unprocessed_videos()
            
            if not unprocessed_videos:
                logger.info("No new videos to process")
                return
            
            logger.info(f"Found {len(unprocessed_videos)} unprocessed videos")
            
            # Process each video
            processed_count = 0
            error_count = 0
            skipped_count = 0
            
            for i, video_record in enumerate(unprocessed_videos):
                logger.info(f"Processing video {i+1}/{len(unprocessed_videos)}: {video_record.get('title', 'Untitled')} ({video_record['video_id']})")
                
                result = self.process_video_from_database(video_record)
                if result is True:
                    processed_count += 1
                elif result is False:
                    error_count += 1
                else:  # None means skipped due to rate limits
                    skipped_count += 1
            
            logger.info(f"Processing complete. Processed: {processed_count}, Errors: {error_count}, Skipped: {skipped_count}")
            
            if skipped_count > 0:
                logger.info(f"💡 {skipped_count} videos were skipped due to rate limits. Run again later to process them.")
            
        except Exception as e:
            logger.error(f"Error checking database: {str(e)}")
            raise
    
    def close(self):
        """Clean up resources."""
        self.db.close()

def main():
    """Main entry point for the database-driven application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube Transcript to Notion Database Processor')
    parser.add_argument('--once', action='store_true', help='Run once instead of scheduling')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule (default)')
    
    args = parser.parse_args()
    
    try:
        processor = DatabaseTranscriptProcessor()
        
        if args.once:
            # Run once and exit
            processor.check_and_process_new_videos()
        else:
            # Run on schedule
            scheduler = TranscriptScheduler(
                check_function=processor.check_and_process_new_videos,
                interval_hours=settings.check_interval_hours
            )
            logger.info(f"Starting database monitor with {settings.check_interval_hours} hour interval...")
            scheduler.start(run_immediately=True)
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    finally:
        if 'processor' in locals():
            processor.close()

if __name__ == "__main__":
    main()