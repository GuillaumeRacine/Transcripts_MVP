import logging
import sys
import time
from typing import Optional
from datetime import datetime

from src.config import settings
from src.youtube.playlist_fetcher import PlaylistFetcher
from src.transcript.extractor import TranscriptExtractor
from src.summarizer.llm_summarizer import SummarizerFactory
from src.notion.client import NotionClient
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

class TranscriptProcessor:
    def __init__(self):
        # Initialize components
        self.playlist_fetcher = PlaylistFetcher(
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
        
        self.notion_client = NotionClient(settings.notion_token, settings.notion_page_id)
        self.db = Database(settings.database_url)
        self.markdown_backup = MarkdownBackup()
        
        # Setup Notion page connection on first run
        try:
            self.notion_client.setup_page()
        except Exception as e:
            logger.warning(f"Could not connect to Notion page: {str(e)}")
    
    def process_video(self, video_info: dict) -> bool:
        """
        Process a single video: extract transcript, summarize, and add to Notion.
        
        Args:
            video_info: Dictionary with video information
            
        Returns:
            True if successful, False otherwise
        """
        video_id = video_info['video_id']
        
        # Check if already processed
        if self.db.is_video_processed(video_id):
            logger.info(f"Video {video_id} already processed, skipping.")
            return True
        
        # Check if exists in Notion (backup check)
        if self.notion_client.check_if_video_exists(video_id):
            logger.info(f"Video {video_id} already in Notion, updating database.")
            self.db.add_processed_video({
                **video_info,
                'transcript_extracted': True,
                'summary_generated': True,
                'notion_page_created': True
            })
            return True
        
        logger.info(f"Processing video: {video_info['title']} ({video_id})")
        
        try:
            # Extract transcript
            logger.info("Extracting transcript...")
            transcript = self.transcript_extractor.extract_transcript(video_id)
            
            if transcript is None:
                # Check if this was due to rate limiting (no error message) or actual failure
                status = self.transcript_extractor.rate_limiter.get_status()
                if status['daily_remaining'] <= 0 or status['hourly_remaining'] <= 0:
                    logger.info(f"Skipping video {video_id} due to rate limits")
                    return None  # Skipped due to rate limits
                else:
                    logger.warning(f"No transcript available for video {video_id}")
                    self.db.add_processed_video({
                        **video_info,
                        'error_message': 'No transcript available'
                    })
                    return False
            
            # Update database
            if not self.db.get_processed_video(video_id):
                self.db.add_processed_video({
                    **video_info,
                    'transcript_extracted': True
                })
            else:
                self.db.update_video_status(video_id, transcript_extracted=True)
            
            # Generate summary
            logger.info("Generating summary...")
            summary = self.summarizer.summarize(
                transcript=transcript,
                instructions=settings.summary_instructions,
                video_metadata=video_info
            )
            
            # Update database
            self.db.update_video_status(video_id, summary_generated=True)
            
            # Create Notion page
            logger.info("Creating Notion page...")
            page_title = f"{video_info['title']} [{video_id}]"
            
            notion_success = False
            notion_page_id = None
            
            try:
                notion_response = self.notion_client.create_page(
                    title=page_title,
                    content=summary,
                    video_metadata=video_info
                )
                notion_page_id = notion_response['id']
                notion_success = True
                logger.info("✅ Notion page created successfully")
            except Exception as notion_error:
                logger.error(f"❌ Notion page creation failed: {str(notion_error)}")
                logger.info("Creating markdown backup instead...")
                
                # Create markdown backup
                try:
                    backup_path = self.markdown_backup.create_backup(
                        video_info=video_info,
                        summary=summary,
                        transcript=transcript
                    )
                    logger.info(f"✅ Markdown backup created: {backup_path}")
                except Exception as backup_error:
                    logger.error(f"❌ Markdown backup also failed: {str(backup_error)}")
                    raise backup_error
            
            # Update database with success
            self.db.update_video_status(
                video_id,
                notion_page_created=notion_success,
                notion_page_id=notion_page_id
            )
            
            logger.info(f"Successfully processed video: {video_info['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {str(e)}")
            self.db.update_video_status(video_id, error_message=str(e))
            return False
    
    def check_and_process_playlist(self):
        """Check playlist for new videos and process them."""
        try:
            logger.info(f"Checking playlist {settings.youtube_playlist_id} for new videos...")
            
            # Fetch all videos from playlist
            videos = self.playlist_fetcher.get_playlist_videos(settings.youtube_playlist_id)
            logger.info(f"Found {len(videos)} videos in playlist")
            
            # Process each video (rate limiting handled by TranscriptExtractor)
            processed_count = 0
            error_count = 0
            skipped_count = 0
            
            for i, video in enumerate(videos):
                logger.info(f"Processing video {i+1}/{len(videos)}: {video['title']}")
                
                result = self.process_video(video)
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
            logger.error(f"Error checking playlist: {str(e)}")
            raise
    
    def close(self):
        """Clean up resources."""
        self.db.close()

def main():
    """Main entry point for the application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube Transcript to Notion Processor')
    parser.add_argument('--once', action='store_true', help='Run once instead of scheduling')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule (default)')
    
    args = parser.parse_args()
    
    try:
        processor = TranscriptProcessor()
        
        if args.once:
            # Run once and exit
            processor.check_and_process_playlist()
        else:
            # Run on schedule
            scheduler = TranscriptScheduler(
                check_function=processor.check_and_process_playlist,
                interval_hours=settings.check_interval_hours
            )
            logger.info(f"Starting scheduler with {settings.check_interval_hours} hour interval...")
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