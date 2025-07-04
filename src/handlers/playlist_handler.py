#!/usr/bin/env python3
"""
Playlist Handler for YouTube to Notion Transcript Processor

Handles fetching videos from YouTube playlists and adding them to Notion database.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs

from src.youtube.playlist_fetcher import PlaylistFetcher
from src.notion.database_client import NotionDatabaseClient

logger = logging.getLogger(__name__)


class PlaylistHandler:
    """Handler for processing YouTube playlists and adding videos to Notion database."""
    
    def __init__(self, youtube_fetcher: PlaylistFetcher, notion_client: NotionDatabaseClient):
        """
        Initialize playlist handler.
        
        Args:
            youtube_fetcher: YouTube API client
            notion_client: Notion database client
        """
        self.youtube_fetcher = youtube_fetcher
        self.notion_client = notion_client
    
    def extract_playlist_id(self, playlist_url: str) -> Optional[str]:
        """
        Extract playlist ID from YouTube URL.
        
        Args:
            playlist_url: YouTube playlist URL
            
        Returns:
            Playlist ID or None if not found
        """
        try:
            # Handle different URL formats:
            # https://www.youtube.com/playlist?list=PLU9jW31vWD03JHBlzrMdVmqDW_sNn0JUL
            # https://youtube.com/playlist?list=PLU9jW31vWD03JHBlzrMdVmqDW_sNn0JUL
            # https://www.youtube.com/watch?v=VIDEO_ID&list=PLU9jW31vWD03JHBlzrMdVmqDW_sNn0JUL
            
            parsed_url = urlparse(playlist_url)
            query_params = parse_qs(parsed_url.query)
            
            # Look for 'list' parameter
            if 'list' in query_params:
                playlist_id = query_params['list'][0]
                logger.info(f"Extracted playlist ID: {playlist_id}")
                return playlist_id
            
            # Try regex as fallback
            pattern = r'[?&]list=([a-zA-Z0-9_-]+)'
            match = re.search(pattern, playlist_url)
            if match:
                playlist_id = match.group(1)
                logger.info(f"Extracted playlist ID via regex: {playlist_id}")
                return playlist_id
            
            logger.error(f"Could not extract playlist ID from URL: {playlist_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting playlist ID: {str(e)}")
            return None
    
    def get_playlist_info(self, playlist_id: str) -> Optional[Dict]:
        """
        Get playlist information from YouTube API.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            Playlist information dictionary
        """
        try:
            request = self.youtube_fetcher.youtube.playlists().list(
                part="snippet,contentDetails",
                id=playlist_id
            )
            response = request.execute()
            
            if response['items']:
                item = response['items'][0]
                return {
                    'playlist_id': playlist_id,
                    'title': item['snippet']['title'],
                    'description': item['snippet'].get('description', ''),
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'video_count': item['contentDetails']['itemCount']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error fetching playlist info: {str(e)}")
            return None
    
    def add_videos_to_notion(self, videos: List[Dict], playlist_info: Optional[Dict] = None) -> Tuple[int, int]:
        """
        Add videos to Notion database.
        
        Args:
            videos: List of video dictionaries
            playlist_info: Optional playlist information
            
        Returns:
            Tuple of (added_count, skipped_count)
        """
        added_count = 0
        skipped_count = 0
        
        # Get existing videos once before the loop to avoid triggering playlist expansion
        existing_videos = self.notion_client.get_unprocessed_videos(expand_playlists=False)
        video_ids = [v.get('video_id') for v in existing_videos if v.get('video_id')]
        
        # Also check processed videos
        processed_videos = self.notion_client.get_processed_videos()
        processed_video_ids = [v.get('video_id') for v in processed_videos if v.get('video_id')]
        
        all_existing_ids = set(video_ids + processed_video_ids)
        
        for video in videos:
            try:
                
                if video['video_id'] in all_existing_ids:
                    logger.info(f"   Skipping: {video['title'][:50]}... (already exists)")
                    skipped_count += 1
                    continue
                
                # Create video URL
                video_url = f"https://www.youtube.com/watch?v={video['video_id']}"
                
                # Prepare page properties
                properties = {
                    'Video URL': {
                        'url': video_url
                    },
                    'Title': {
                        'title': [{'text': {'content': video['title']}}]
                    },
                    'Status': {
                        'select': {'name': 'New'}
                    }
                }
                
                # Note: Not adding playlist info to properties since the database 
                # schema may not have these fields. Users can manually add 
                # Playlist and Channel fields to their database if desired.
                
                # Create page in Notion database
                response = self.notion_client.create_page(properties)
                
                if response:
                    logger.info(f"   Added: {video['title'][:50]}...")
                    added_count += 1
                else:
                    logger.warning(f"   Failed to add: {video['title'][:50]}...")
                    
            except Exception as e:
                logger.error(f"Error adding video {video.get('title', 'Unknown')}: {str(e)}")
                continue
        
        return added_count, skipped_count
    
    def process_playlist(self, playlist_url: str, max_videos: Optional[int] = None) -> Dict:
        """
        Process a complete YouTube playlist and add videos to Notion.
        
        Args:
            playlist_url: YouTube playlist URL
            max_videos: Optional limit on number of videos to process
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing playlist: {playlist_url}")
        
        # Extract playlist ID
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            return {
                'success': False,
                'error': 'Could not extract playlist ID from URL',
                'added': 0,
                'skipped': 0,
                'total': 0
            }
        
        try:
            # Get playlist information
            logger.info("   Fetching playlist information...")
            playlist_info = self.get_playlist_info(playlist_id)
            
            if playlist_info:
                logger.info(f"   Playlist: {playlist_info['title']}")
                logger.info(f"   Channel: {playlist_info['channel_title']}")
                logger.info(f"   Total videos: {playlist_info['video_count']}")
            
            # Fetch all videos from playlist
            logger.info("   Fetching videos from playlist...")
            videos = self.youtube_fetcher.get_playlist_videos(playlist_id)
            
            if not videos:
                return {
                    'success': False,
                    'error': 'No videos found in playlist',
                    'added': 0,
                    'skipped': 0,
                    'total': 0
                }
            
            # Smart limiting for rate limit management
            original_count = len(videos)
            if max_videos and max_videos < len(videos):
                logger.info(f"   Limiting to first {max_videos} videos")
                videos = videos[:max_videos]
            elif len(videos) > 15:
                # Auto-limit large playlists to prevent rate limit issues
                logger.info(f"   Large playlist detected ({len(videos)} videos)")
                logger.info(f"   Limiting to first 15 videos to avoid rate limits")
                logger.info(f"   Run again to add more videos from this playlist")
                videos = videos[:15]
            
            logger.info(f"   Found {len(videos)} videos to process")
            if len(videos) < original_count:
                logger.info(f"   ({original_count - len(videos)} videos will be added in subsequent runs)")
            logger.info("   Adding videos to Notion database...")
            
            # Add videos to Notion database
            added_count, skipped_count = self.add_videos_to_notion(videos, playlist_info)
            
            # Return results
            results = {
                'success': True,
                'playlist_info': playlist_info,
                'added': added_count,
                'skipped': skipped_count,
                'total': len(videos),
                'playlist_id': playlist_id
            }
            
            logger.info(f"   Playlist processing complete!")
            logger.info(f"   Added: {added_count}, Skipped: {skipped_count}, Total: {len(videos)}")
            if len(videos) < original_count:
                remaining = original_count - len(videos) - skipped_count
                logger.info(f"   Remaining in playlist: {remaining} videos (add them by running playlist command again)")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing playlist: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'added': 0,
                'skipped': 0,
                'total': 0
            }