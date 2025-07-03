#!/usr/bin/env python3
"""
Test script for rate limiting behavior
"""
import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.transcript.extractor import TranscriptExtractor
from src.utils.rate_limiter import RateLimiter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rate_limiter():
    """Test the rate limiter directly"""
    logger.info("=== Testing Rate Limiter ===")
    
    # Create a rate limiter with lower limits for testing
    rate_limiter = RateLimiter(
        max_requests_per_hour=10,  # Lower limit for testing
        max_requests_per_day=50,   # Lower limit for testing
        cache_file="test_rate_limit_cache.json"
    )
    
    # Check initial status
    status = rate_limiter.get_status()
    logger.info(f"Initial status: {status}")
    
    # Test multiple requests
    for i in range(5):
        can_request, reason = rate_limiter.can_make_request()
        if can_request:
            rate_limiter.record_request()
            logger.info(f"Request {i+1}: ✅ Allowed")
        else:
            logger.info(f"Request {i+1}: ❌ Rate limited - {reason}")
        
        status = rate_limiter.get_status()
        logger.info(f"  Status: {status}")
        
        time.sleep(0.1)  # Small delay
    
    # Clean up test file
    try:
        os.remove("test_rate_limit_cache.json")
    except:
        pass

def test_transcript_extraction():
    """Test transcript extraction with rate limiting"""
    logger.info("\n=== Testing Transcript Extraction with Rate Limits ===")
    
    extractor = TranscriptExtractor()
    
    # Show current rate limit status
    status = extractor.rate_limiter.get_status()
    logger.info(f"Current rate limit status: {status}")
    
    # Test with known videos that should have transcripts
    test_videos = [
        "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "9bZkp7q19f0",  # Gangnam Style
        "kJQP7kiw5Fk",  # Despacito
    ]
    
    for i, video_id in enumerate(test_videos):
        logger.info(f"\nTesting video {i+1}: {video_id}")
        
        # Check if we can make a request
        if extractor.rate_limiter.can_make_request():
            logger.info("✅ Rate limiter allows request")
            
            try:
                transcript = extractor.extract_transcript(video_id)
                if transcript:
                    logger.info(f"✅ Transcript extracted ({len(transcript)} characters)")
                    # Show first 100 characters
                    preview = transcript[:100].replace('\n', ' ')
                    logger.info(f"  Preview: {preview}...")
                else:
                    logger.info("❌ No transcript available")
            except Exception as e:
                logger.error(f"❌ Error extracting transcript: {str(e)}")
        else:
            logger.info("❌ Rate limited - would skip this video")
        
        # Show updated status
        status = extractor.rate_limiter.get_status()
        logger.info(f"  Rate limit status: {status}")
        
        # Add small delay between requests
        time.sleep(1)

def test_rate_limit_recovery():
    """Test rate limit recovery mechanism"""
    logger.info("\n=== Testing Rate Limit Recovery ===")
    
    extractor = TranscriptExtractor()
    
    # Try to trigger rate limiting with a video that might not have transcripts
    # This should trigger the rate limit recovery mechanism
    test_video = "nonexistent_video_id"
    
    logger.info(f"Testing with potentially problematic video: {test_video}")
    
    try:
        transcript = extractor.extract_transcript(test_video)
        if transcript:
            logger.info("✅ Transcript extracted")
        else:
            logger.info("❌ No transcript (expected)")
    except Exception as e:
        logger.info(f"❌ Error (expected): {str(e)}")
    
    # Check if rate limiter handled it properly
    status = extractor.rate_limiter.get_status()
    logger.info(f"Final rate limit status: {status}")

if __name__ == "__main__":
    logger.info("🚀 Starting Rate Limit Tests")
    
    try:
        # Test 1: Rate limiter directly
        test_rate_limiter()
        
        # Test 2: Transcript extraction with rate limits
        test_transcript_extraction()
        
        # Test 3: Rate limit recovery
        test_rate_limit_recovery()
        
        logger.info("\n✅ All rate limit tests completed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        sys.exit(1)