#!/usr/bin/env python3
"""
Test script for service account integration with YouTube API
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.youtube.playlist_fetcher import PlaylistFetcher
from src.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_service_account():
    """Test service account authentication"""
    try:
        # Test with service account file
        service_account_file = "./youtube_service_account.json"
        
        if not os.path.exists(service_account_file):
            logger.error(f"Service account file not found: {service_account_file}")
            return False
            
        logger.info("Testing service account authentication...")
        fetcher = PlaylistFetcher(service_account_file=service_account_file)
        
        # Test with a known public video first
        test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        
        logger.info(f"Testing video details fetch for: {test_video_id}")
        video_details = fetcher.get_video_details(test_video_id)
        
        if video_details:
            logger.info(f"✅ Successfully fetched video details")
            logger.info(f"  Title: {video_details['title']}")
            logger.info(f"  Channel: {video_details['channel_title']}")
            logger.info(f"  Views: {video_details['view_count']:,}")
            
            # Now test with your actual playlist if you have one
            if hasattr(settings, 'youtube_playlist_id') and settings.youtube_playlist_id:
                logger.info(f"Testing your playlist: {settings.youtube_playlist_id}")
                try:
                    videos = fetcher.get_playlist_videos(settings.youtube_playlist_id, max_results=3)
                    if videos:
                        logger.info(f"✅ Successfully fetched {len(videos)} videos from your playlist")
                        for i, video in enumerate(videos[:2]):
                            logger.info(f"  {i+1}. {video['title']} ({video['video_id']})")
                    else:
                        logger.warning("Your playlist appears to be empty")
                except Exception as e:
                    logger.warning(f"Could not fetch from your playlist: {str(e)}")
            
            return True
        else:
            logger.warning("Could not fetch video details")
            return False
            
    except Exception as e:
        logger.error(f"❌ Service account test failed: {str(e)}")
        return False

def test_api_key_fallback():
    """Test API key fallback if available"""
    try:
        if not settings.youtube_api_key:
            logger.info("No API key configured, skipping API key test")
            return None
            
        logger.info("Testing API key authentication...")
        fetcher = PlaylistFetcher(api_key=settings.youtube_api_key)
        
        # Test with same playlist
        test_playlist_id = "PLrAXtmRdnEQy6XRKiQaK3C1GF_RXjGPcH"
        
        videos = fetcher.get_playlist_videos(test_playlist_id, max_results=2)
        
        if videos:
            logger.info(f"✅ API key also works - fetched {len(videos)} videos")
            return True
        else:
            logger.warning("No videos found with API key")
            return False
            
    except Exception as e:
        logger.error(f"❌ API key test failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== YouTube API Authentication Test ===")
    
    # Test service account
    service_account_success = test_service_account()
    
    # Test API key fallback
    api_key_success = test_api_key_fallback()
    
    # Summary
    logger.info("\n=== Test Results ===")
    logger.info(f"Service Account: {'✅ PASS' if service_account_success else '❌ FAIL'}")
    if api_key_success is not None:
        logger.info(f"API Key: {'✅ PASS' if api_key_success else '❌ FAIL'}")
    else:
        logger.info("API Key: ⏭️ SKIPPED (not configured)")
    
    if service_account_success or api_key_success:
        logger.info("\n🎉 At least one authentication method is working!")
    else:
        logger.info("\n💥 Both authentication methods failed. Check your credentials.")
        sys.exit(1)