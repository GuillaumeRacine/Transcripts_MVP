#!/usr/bin/env python3
"""
YouTube to Notion Transcript Processor

Automatically processes YouTube videos from Notion database and generates
comprehensive AI-powered summaries using Claude 3 Opus.
"""

import logging
import os
import sys
import time
from typing import Optional, Dict
from datetime import datetime

from src.config import settings
from src.youtube.playlist_fetcher import PlaylistFetcher
from src.transcript.extractor import TranscriptExtractor
from src.summarizer.multi_part_summarizer import MultiPartSummarizer
from src.notion.database_client import NotionDatabaseClient
from src.database.models import Database
from src.scheduler.scheduler import TranscriptScheduler
from src.backup.markdown_backup import MarkdownBackup
from src.handlers.playlist_handler import PlaylistHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('transcripts_app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Suppress verbose library logging
for lib in ['googleapiclient.discovery_cache', 'httpx']:
    logging.getLogger(lib).setLevel(logging.WARNING)


class VideoProcessor:
    """Main video processor for YouTube to Notion workflow."""
    
    def __init__(self):
        """Initialize processor with all required components."""
        self._validate_config()
        self._init_components()
        
    def _validate_config(self):
        """Validate required configuration."""
        if not settings.notion_database_id:
            raise ValueError("NOTION_DATABASE_ID must be configured")
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY must be configured")
    
    def _init_components(self):
        """Initialize all service components."""
        # YouTube components
        self.youtube_fetcher = PlaylistFetcher(
            api_key=settings.youtube_api_key,
            service_account_file=settings.youtube_service_account_file
        )
        self.transcript_extractor = TranscriptExtractor()
        
        # Use multi-part summarizer for comprehensive analysis
        # Use configurable delay between API calls to prevent overload
        self.summarizer = MultiPartSummarizer(settings.anthropic_api_key, api_delay=settings.api_call_delay)
        
        # Storage components
        self.notion_client = NotionDatabaseClient(settings.notion_token, settings.notion_database_id)
        self.db = Database(settings.database_url)
        self.markdown_backup = MarkdownBackup()
        
        # Playlist handler
        self.playlist_handler = PlaylistHandler(self.youtube_fetcher, self.notion_client)
        
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
            # Cache the transcript (will be updated with full video info later)
            self.db.add_processed_video({
                'video_id': video_id,
                'title': 'Processing...',
                'published_at': '2024-01-01T00:00:00Z',  # Placeholder, will be updated
                'transcript_extracted': True,
                'transcript': transcript
            })
        return transcript
    
    def _generate_summary(self, transcript: str, video_info: dict) -> str:
        """Generate comprehensive AI summary using Claude 3 Opus."""
        logger.info("   Generating comprehensive AI summary...")
        
        summary = self.summarizer.generate_comprehensive_summary(
            transcript=transcript,
            video_metadata=video_info
        )
        
        word_count = len(summary.split())
        logger.info(f"   Generated {word_count} word comprehensive summary")
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
    
    def process_playlist(self, playlist_url: str, max_videos: Optional[int] = None) -> Dict:
        """Process a YouTube playlist and add videos to Notion database."""
        logger.info(f"\nProcessing YouTube playlist...")
        
        try:
            result = self.playlist_handler.process_playlist(playlist_url, max_videos)
            
            if result['success']:
                logger.info(f"\nPlaylist processing completed successfully!")
                logger.info(f"Added {result['added']} new videos to database")
                logger.info(f"Skipped {result['skipped']} existing videos")
                logger.info(f"Total videos in playlist: {result['total']}")
                
                if result.get('playlist_info'):
                    playlist_info = result['playlist_info']
                    logger.info(f"\nPlaylist: {playlist_info['title']}")
                    logger.info(f"Channel: {playlist_info['channel_title']}")
                
                # Suggest next steps with rate limit considerations
                if result['added'] > 0:
                    logger.info(f"\nNext steps:")
                    if result['added'] > 10:
                        logger.info(f"⚠️  Large playlist detected ({result['added']} videos)")
                        logger.info(f"To avoid rate limits, consider processing in batches:")
                        logger.info(f"python main_database.py --once  # Process some videos now")
                        logger.info(f"# Wait 10-15 minutes, then run again for remaining videos")
                    else:
                        logger.info(f"Run 'python main_database.py --once' to process the new videos")
                    
            else:
                logger.error(f"Failed to process playlist: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing playlist: {str(e)}")
            return {'success': False, 'error': str(e), 'added': 0, 'skipped': 0, 'total': 0}

    def check_api_health(self) -> dict:
        """Check Claude API health before processing."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=settings.anthropic_api_key)
            
            start_time = time.time()
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=50,
                temperature=0,
                messages=[{"role": "user", "content": "Respond with: OK"}]
            )
            elapsed = time.time() - start_time
            
            if elapsed < 5:
                return {"status": "healthy", "delay": elapsed}
            else:
                return {"status": "slow", "delay": elapsed}
                
        except Exception as e:
            if "overloaded" in str(e).lower() or "529" in str(e):
                return {"status": "overloaded", "error": str(e)}
            return {"status": "error", "error": str(e)}
    
    def check_and_process_videos(self, force_reprocess: bool = False, check_health: bool = True):
        """Main processing loop - check for new videos and process them."""
        
        # Check API health first (unless disabled)
        if check_health:
            logger.info("\n🏥 Checking API health...")
            health = self.check_api_health()
            
            if health["status"] == "overloaded":
                logger.warning("⚠️  API is overloaded. Skipping processing.")
                logger.warning("Try again in 30-60 minutes.")
                return
            elif health["status"] == "error":
                logger.error(f"API error: {health.get('error', 'Unknown')}")
                return
            elif health["status"] == "slow":
                logger.warning(f"API is slow (response time: {health['delay']:.1f}s)")
                logger.warning("Processing will continue but expect delays.")
            else:
                logger.info(f"✅ API is healthy (response time: {health['delay']:.1f}s)")
        
        logger.info("\nChecking for new videos in Notion...")
        
        try:
            # First, check for any playlist URLs that need expanding
            self._check_and_expand_playlists()
            
            # Then get regular videos to process
            unprocessed_videos = self.notion_client.get_unprocessed_videos(expand_playlists=False)
            
            if not unprocessed_videos:
                logger.info("No new videos found")
                return
            
            logger.info(f"\nFound {len(unprocessed_videos)} videos to process\n")
            
            # Batch processing optimized for cloud deployment
            if len(unprocessed_videos) > 15:
                logger.info(f"⚠️  Large batch detected ({len(unprocessed_videos)} videos)")
                logger.info(f"Processing first 15 videos to prevent timeout...")
                unprocessed_videos = unprocessed_videos[:15]
                logger.info(f"Remaining videos will be processed in next scheduled run")
            
            # Process each video with intelligent batching for large sets
            stats = {'processed': 0, 'errors': 0, 'skipped': 0}
            is_large_batch = len(unprocessed_videos) > 10
            
            for i, video_record in enumerate(unprocessed_videos):
                title = video_record.get('title', 'Untitled')
                logger.info(f"\n[{i+1}/{len(unprocessed_videos)}] {title[:60]}")
                
                result = self.process_single_video(video_record, force_reprocess)
                if result is True:
                    stats['processed'] += 1
                elif result is False:
                    stats['errors'] += 1
                else:  # None means skipped due to rate limits
                    stats['skipped'] += 1
                
                # Always add delay between videos to avoid rate limits
                if i < len(unprocessed_videos) - 1:
                    import time
                    # Very conservative adaptive delay based on success/error rate
                    if stats['errors'] == 0:
                        delay = settings.video_processing_delay  # Base delay when no errors
                    elif stats['errors'] <= 1:
                        delay = settings.video_processing_delay * 2  # Double delay with 1 error
                    elif stats['errors'] <= 2:
                        delay = settings.video_processing_delay * 3  # Triple delay with 2 errors
                    else:
                        # Much longer delay with many errors
                        delay = min(
                            settings.video_processing_delay * 5 + (stats['errors'] * settings.error_backoff_multiplier), 
                            settings.max_processing_delay
                        )
                    
                    logger.info(f"   Waiting {delay}s before next video...")
                    time.sleep(delay)
                
                # Stop processing immediately after first error during API overload periods
                if stats['errors'] >= 1:
                    remaining = len(unprocessed_videos) - i - 1
                    if remaining > 0:
                        logger.warning(f"\n⚠️ API overload detected after {stats['errors']} error(s). Stopping to prevent cascading failures.")
                        logger.warning(f"Remaining {remaining} videos will be processed when API stabilizes.")
                        logger.warning(f"Suggestion: Try again in 30-60 minutes when API load decreases.")
                        break
            
            # Final summary
            logger.info(f"\nSummary: {stats['processed']} processed, {stats['errors']} errors, {stats['skipped']} skipped")
            
            if stats['skipped'] > 0:
                logger.info(f"{stats['skipped']} videos were skipped due to rate limits. Run again later to process them.")
            
            if stats['errors'] > 0 and len(unprocessed_videos) > 10:
                logger.info(f"\nFor large playlists, consider processing in smaller batches using:")
                logger.info(f"python main_database.py --once --interval 30  # Process every 30 minutes")
                logger.info(f"Or wait 5-10 minutes before running again to avoid rate limits.")
                
        except Exception as e:
            logger.error(f"Error checking database: {str(e)}")
            raise
    
    def _check_and_expand_playlists(self):
        """Check for playlist URLs and expand them if needed."""
        try:
            # Query for playlist URLs that haven't been expanded
            response = self.notion_client.client.databases.query(
                database_id=self.notion_client.database_id,
                filter={
                    "and": [
                        {
                            "property": "Video URL",
                            "url": {
                                "contains": "list="
                            }
                        },
                        {
                            "or": [
                                {
                                    "property": "Status",
                                    "select": {
                                        "does_not_equal": "Playlist Expanded"
                                    }
                                },
                                {
                                    "property": "Status",
                                    "select": {
                                        "is_empty": True
                                    }
                                }
                            ]
                        }
                    ]
                }
            )
            
            playlist_entries = []
            for page in response.get("results", []):
                properties = page.get("properties", {})
                
                # Extract video URL
                video_url_prop = properties.get("Video URL", {})
                if video_url_prop.get("type") == "url":
                    video_url = video_url_prop.get("url")
                    if video_url and self.notion_client.is_playlist_url(video_url):
                        title = self.notion_client._extract_title_from_page(properties)
                        playlist_entries.append({
                            'page_id': page['id'],
                            'playlist_url': video_url,
                            'title': title
                        })
            
            if playlist_entries:
                logger.info(f"Found {len(playlist_entries)} playlist(s) to expand")
                for entry in playlist_entries:
                    logger.info(f"Expanding playlist: {entry['title']}")
                    result = self.playlist_handler.process_playlist(entry['playlist_url'])
                    
                    if result['success']:
                        logger.info(f"Added {result['added']} videos from playlist")
                        self.notion_client.update_video_status(
                            entry['page_id'], 
                            "Playlist Expanded",
                            title=f"[PLAYLIST] {entry['title']}"
                        )
                    else:
                        logger.error(f"Failed to expand playlist: {result.get('error')}")
                        self.notion_client.update_video_status(
                            entry['page_id'], 
                            "Error",
                            error_message=f"Playlist expansion failed: {result.get('error')}"
                        )
        except Exception as e:
            logger.error(f"Error checking for playlists: {str(e)}")
    
    def close(self):
        """Clean up resources."""
        self.db.close()


def main():
    """Main entry point with argument parsing."""
    import argparse
    
    print("\nYouTube to Notion Transcript Processor")
    print("-" * 40)
    
    parser = argparse.ArgumentParser(description='YouTube Transcript to Notion Database Processor')
    parser.add_argument('--once', action='store_true', help='Run once instead of scheduling')
    parser.add_argument('--reprocess', action='store_true', help='Force reprocessing of already processed videos')
    parser.add_argument('--interval', type=int, help='Check interval in minutes (overrides env setting)')
    parser.add_argument('--playlist', type=str, help='Process a YouTube playlist URL and add videos to database')
    parser.add_argument('--max-videos', type=int, help='Maximum number of videos to add from playlist (default: all)')
    
    args = parser.parse_args()
    
    try:
        processor = VideoProcessor()
        
        if args.playlist:
            # Process playlist and add videos to database
            processor.process_playlist(args.playlist, args.max_videos)
        elif args.once:
            # Run once and exit
            if args.interval:
                # Special mode: process for a limited time with delays
                import time
                start_time = time.time()
                max_duration = args.interval * 60  # Convert minutes to seconds
                
                logger.info(f"Processing videos for up to {args.interval} minutes with delays...")
                
                while time.time() - start_time < max_duration:
                    unprocessed = processor.notion_client.get_unprocessed_videos(expand_playlists=False)
                    if not unprocessed:
                        logger.info("No more videos to process")
                        break
                    
                    # Process just a few videos at a time
                    batch = unprocessed[:3]
                    logger.info(f"Processing batch of {len(batch)} videos...")
                    
                    for video in batch:
                        result = processor.process_single_video(video, force_reprocess=args.reprocess)
                        if result is False:  # Error occurred
                            logger.info("Waiting 30 seconds after error...")
                            time.sleep(30)
                    
                    remaining_time = max_duration - (time.time() - start_time)
                    if remaining_time > 60:
                        logger.info("Waiting 60 seconds before next batch...")
                        time.sleep(60)
                    else:
                        break
                        
                logger.info(f"Batch processing session completed")
            else:
                processor.check_and_process_videos(force_reprocess=args.reprocess)
        else:
            # Run continuously
            if args.interval:
                interval_hours = args.interval / 60.0
                interval_minutes = int(interval_hours * 60)
                logger.info(f"\nStarting continuous monitor (checking every {interval_minutes} minutes)")
            else:
                interval_hours = settings.check_interval_hours
                interval_minutes = int(interval_hours * 60)
                logger.info(f"\nStarting continuous monitor (checking every {interval_minutes} minutes)")
            
            scheduler = TranscriptScheduler(
                check_function=lambda: processor.check_and_process_videos(force_reprocess=args.reprocess),
                interval_hours=interval_hours
            )
            logger.info("Press Ctrl+C to stop\n")
            scheduler.start(run_immediately=True)
        
    except KeyboardInterrupt:
        logger.info("\nApplication stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    finally:
        if 'processor' in locals():
            processor.close()


if __name__ == "__main__":
    main()