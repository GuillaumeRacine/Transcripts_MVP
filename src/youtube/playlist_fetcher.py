from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PlaylistFetcher:
    def __init__(self, api_key: Optional[str] = None, service_account_file: Optional[str] = None):
        """
        Initialize PlaylistFetcher with either API key or service account authentication.
        
        Args:
            api_key: YouTube API key (for simple authentication)
            service_account_file: Path to service account JSON file (for OAuth2 authentication)
        """
        if service_account_file:
            # Use service account authentication
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/youtube.readonly']
            )
            self.youtube = build('youtube', 'v3', credentials=credentials)
            logger.info("Using service account authentication")
        elif api_key:
            # Use API key authentication
            self.youtube = build('youtube', 'v3', developerKey=api_key)
            logger.info("Using API key authentication")
        else:
            raise ValueError("Either api_key or service_account_file must be provided")
    
    def get_playlist_videos(self, playlist_id: str, max_results: int = 50) -> List[Dict]:
        """
        Fetch all videos from a YouTube playlist.
        
        Args:
            playlist_id: The ID of the YouTube playlist
            max_results: Maximum number of results per API call (max 50)
            
        Returns:
            List of video information dictionaries
        """
        videos = []
        next_page_token = None
        
        try:
            while True:
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=max_results,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    video_info = {
                        'video_id': item['contentDetails']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet'].get('description', ''),
                        'published_at': item['snippet']['publishedAt'],
                        'thumbnail_url': item['snippet']['thumbnails']['default']['url'],
                        'channel_title': item['snippet']['channelTitle'],
                        'playlist_position': item['snippet']['position']
                    }
                    videos.append(video_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            logger.info(f"Fetched {len(videos)} videos from playlist {playlist_id}")
            return videos
            
        except Exception as e:
            logger.error(f"Error fetching playlist videos: {str(e)}")
            raise
    
    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific video.
        
        Args:
            video_id: The ID of the YouTube video
            
        Returns:
            Dictionary with video details or None if not found
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                item = response['items'][0]
                return {
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'duration': item['contentDetails']['duration'],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'tags': item['snippet'].get('tags', [])
                }
            return None
            
        except Exception as e:
            logger.error(f"Error fetching video details for {video_id}: {str(e)}")
            return None