#!/usr/bin/env python3
"""Find videos that have working transcripts"""

from src.youtube.playlist_fetcher import PlaylistFetcher
from src.transcript.extractor import TranscriptExtractor
from src.config import settings
import time

def find_working_videos():
    fetcher = PlaylistFetcher(settings.youtube_api_key)
    extractor = TranscriptExtractor()
    
    print("Fetching playlist videos...")
    videos = fetcher.get_playlist_videos(settings.youtube_playlist_id)
    print(f"Found {len(videos)} videos")
    
    working_videos = []
    
    for i, video in enumerate(videos[:5]):  # Test first 5 videos only
        video_id = video['video_id']
        title = video['title']
        
        print(f"\n[{i+1}/5] Testing: {title}")
        print(f"Video ID: {video_id}")
        
        try:
            transcript = extractor.extract_transcript(video_id)
            if transcript:
                print(f"✅ SUCCESS! Transcript length: {len(transcript)} characters")
                working_videos.append(video)
            else:
                print("❌ No transcript available")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Add delay to avoid rate limiting
        print("Waiting 3 seconds...")
        time.sleep(3)
    
    print(f"\n\nSUMMARY:")
    print(f"Working videos: {len(working_videos)}")
    for video in working_videos:
        print(f"- {video['title']} ({video['video_id']})")
    
    return working_videos

if __name__ == "__main__":
    find_working_videos()