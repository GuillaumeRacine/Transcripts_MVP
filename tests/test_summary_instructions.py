#!/usr/bin/env python3
"""Test script to verify summary instructions are being passed correctly."""

from src.config import settings
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

def test_summary_instructions():
    print("\n🔍 Testing Summary Instructions Configuration\n")
    print("=" * 80)
    
    # Check if settings are loaded
    print("📋 Summary Instructions from .env file:")
    print("-" * 80)
    print(settings.summary_instructions)
    print("-" * 80)
    
    # Check length
    print(f"\n📏 Instructions length: {len(settings.summary_instructions)} characters")
    
    # Check for key phrases
    key_phrases = [
        "1,000-1.500 words",
        "So what",
        "Important ideas",
        "relevant resources",
        "source url in hyperlink"
    ]
    
    print("\n✅ Checking for key phrases:")
    for phrase in key_phrases:
        if phrase in settings.summary_instructions:
            print(f"   ✓ Found: '{phrase}'")
        else:
            print(f"   ✗ Missing: '{phrase}'")
    
    # Test with actual summarizer
    print("\n🤖 Testing with Anthropic Summarizer...")
    try:
        from src.summarizer.llm_summarizer import SummarizerFactory
        
        if settings.anthropic_api_key:
            summarizer = SummarizerFactory.create_summarizer('anthropic', settings.anthropic_api_key)
            
            # Create a test transcript
            test_transcript = """
            This is a test transcript about important topics.
            The speaker mentions the book 'Atomic Habits' by James Clear.
            They also reference research papers on habit formation.
            The main points are about building better habits and breaking bad ones.
            """
            
            test_metadata = {
                'title': 'Test Video',
                'channel_title': 'Test Channel',
                'published_at': '2024-01-01',
                'video_url': 'https://www.youtube.com/watch?v=test123'
            }
            
            print("\n📝 Generating test summary...")
            summary = summarizer.summarize(
                transcript=test_transcript,
                instructions=settings.summary_instructions,
                video_metadata=test_metadata
            )
            
            print("\n📄 Generated Summary Preview:")
            print("-" * 80)
            print(summary[:500] + "..." if len(summary) > 500 else summary)
            print("-" * 80)
            
            # Check word count
            word_count = len(summary.split())
            print(f"\n📊 Summary word count: {word_count} words")
            
        else:
            print("   ⚠️  No Anthropic API key configured")
            
    except Exception as e:
        print(f"   ❌ Error testing summarizer: {str(e)}")

if __name__ == "__main__":
    test_summary_instructions()