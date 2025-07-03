#!/usr/bin/env python3
"""Test script to process a single video"""

from src.transcript.extractor import TranscriptExtractor
from src.config import settings

def test_single_video():
    extractor = TranscriptExtractor()
    
    # Test with a known video ID from the playlist
    test_video_id = "tOtdJcco3YM"  # Nick Lane video from logs
    
    print(f"Testing transcript extraction for video: {test_video_id}")
    
    transcript = extractor.extract_transcript(test_video_id)
    
    if transcript:
        print(f"Success! Transcript length: {len(transcript)} characters")
        print(f"First 200 characters: {transcript[:200]}...")
        return True
    else:
        print("Failed to extract transcript")
        return False

if __name__ == "__main__":
    test_single_video()