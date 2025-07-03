from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from typing import Optional, List, Dict
import logging
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class TranscriptExtractor:
    def __init__(self):
        self.supported_languages = ['en', 'en-US', 'en-GB']  # Prioritize English
        self.rate_limiter = RateLimiter(
            max_requests_per_hour=50,  # Conservative limit
            max_requests_per_day=200,  # Well below 250 practical limit
            min_delay_seconds=3.0,     # 3 seconds between requests
            backoff_multiplier=2.0     # Exponential backoff on failures
        )
    
    def extract_transcript(self, video_id: str, preferred_languages: Optional[List[str]] = None) -> Optional[str]:
        """
        Extract transcript from a YouTube video with rate limiting.
        
        Args:
            video_id: The ID of the YouTube video
            preferred_languages: List of preferred language codes (defaults to English)
            
        Returns:
            Full transcript text or None if unavailable
        """
        languages = preferred_languages or self.supported_languages
        
        # Check rate limiter status
        status = self.rate_limiter.get_status()
        logger.info(f"Rate limiter status: {status['daily_requests']}/{status['daily_limit']} daily, "
                   f"{status['hourly_requests']}/{status['hourly_limit']} hourly")
        
        # Wait if needed (will return False if we should skip)
        if not self.rate_limiter.wait_if_needed():
            logger.warning(f"Skipping transcript extraction for {video_id} due to rate limits")
            return None
        
        success = False
        try:
            # Try to get transcript list
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to find a transcript in preferred languages
            transcript = None
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    break
                except:
                    continue
            
            # If no preferred language found, try to get any available transcript
            if not transcript:
                try:
                    # Get the first available transcript
                    transcript = transcript_list.find_generated_transcript(languages)
                except:
                    # If no generated transcript, get any manual transcript
                    try:
                        transcript = transcript_list.find_manually_created_transcript(languages)
                    except:
                        # Get any transcript available
                        for t in transcript_list:
                            transcript = t
                            break
            
            if transcript:
                # Fetch the actual transcript data
                transcript_data = transcript.fetch()
                
                # Combine all text segments
                full_text = ' '.join([segment.text for segment in transcript_data])
                
                logger.info(f"Successfully extracted transcript for video {video_id}")
                success = True
                return full_text
            else:
                logger.warning(f"No transcript found for video {video_id}")
                return None
                
        except TranscriptsDisabled:
            logger.warning(f"Transcripts are disabled for video {video_id}")
            return None
        except NoTranscriptFound:
            logger.warning(f"No transcript found for video {video_id}")
            return None
        except Exception as e:
            logger.error(f"Error extracting transcript for video {video_id}: {str(e)}")
            # Check if it's a rate limit error
            if "429" in str(e) or "Too Many Requests" in str(e):
                logger.warning("Hit rate limit - will increase backoff")
            return None
        finally:
            # Record the request outcome for rate limiting
            self.rate_limiter.record_request(success)
    
    def extract_transcript_with_timestamps(self, video_id: str, preferred_languages: Optional[List[str]] = None) -> Optional[List[Dict]]:
        """
        Extract transcript with timestamps from a YouTube video.
        
        Args:
            video_id: The ID of the YouTube video
            preferred_languages: List of preferred language codes (defaults to English)
            
        Returns:
            List of transcript segments with timestamps or None if unavailable
        """
        languages = preferred_languages or self.supported_languages
        
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to find a transcript in preferred languages
            transcript = None
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    break
                except:
                    continue
            
            if not transcript:
                # Get any available transcript
                for t in transcript_list:
                    transcript = t
                    break
            
            if transcript:
                # Fetch the actual transcript data with timestamps
                transcript_data = transcript.fetch()
                
                logger.info(f"Successfully extracted transcript with timestamps for video {video_id}")
                return transcript_data
            else:
                logger.warning(f"No transcript found for video {video_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting transcript with timestamps for video {video_id}: {str(e)}")
            return None
    
    def format_transcript_markdown(self, transcript_data: List[Dict], video_title: str = "") -> str:
        """
        Format transcript data into markdown format.
        
        Args:
            transcript_data: List of transcript segments with timestamps
            video_title: Title of the video
            
        Returns:
            Markdown formatted transcript
        """
        if not transcript_data:
            return ""
        
        markdown = f"# Transcript: {video_title}\n\n" if video_title else "# Transcript\n\n"
        
        for segment in transcript_data:
            timestamp = self._format_timestamp(segment.start)
            text = segment.text.strip()
            markdown += f"**[{timestamp}]** {text}\n\n"
        
        return markdown
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"