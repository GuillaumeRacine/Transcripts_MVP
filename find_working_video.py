#!/usr/bin/env python3
"""Find a working video with transcripts"""

import time
from youtube_transcript_api import YouTubeTranscriptApi

# Test with some common video IDs that might have transcripts
test_videos = [
    "dQw4w9WgXcQ",  # Rick Roll (famous video, likely has transcripts)
    "kJQP7kiw5Fk",  # Luis Fonsi - Despacito 
    "fJ9rUzIMcZQ",  # Queen - Bohemian Rhapsody
    "9bZkp7q19f0",  # PSY - Gangnam Style
]

def test_video_transcript(video_id):
    """Test if a video has transcripts available"""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get English transcript
        try:
            transcript = transcript_list.find_transcript(['en'])
            transcript_data = transcript.fetch()
            
            # Get text from first few segments
            text_sample = ' '.join([segment.text for segment in transcript_data[:3]])
            
            return True, text_sample
        except:
            return False, "No English transcript"
            
    except Exception as e:
        return False, str(e)

def find_working_video():
    """Find a video that has working transcripts"""
    print("🔍 Testing videos for transcript availability...")
    
    for video_id in test_videos:
        print(f"\nTesting video: {video_id}")
        
        success, result = test_video_transcript(video_id)
        
        if success:
            print(f"✅ SUCCESS! Video {video_id} has transcripts")
            print(f"Sample: {result[:100]}...")
            return video_id
        else:
            print(f"❌ Failed: {result}")
            
        # Delay to avoid rate limiting
        time.sleep(2)
    
    print("\n❌ No working videos found with the test set")
    return None

if __name__ == "__main__":
    working_video = find_working_video()
    if working_video:
        print(f"\n🎉 Use this video ID for testing: {working_video}")
    else:
        print("\n💡 Try again later when YouTube rate limits reset")