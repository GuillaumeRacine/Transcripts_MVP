#!/usr/bin/env python3
"""Demo script to test the full pipeline with a mock transcript"""

from src.config import settings
from src.notion.client import NotionClient
from src.summarizer.llm_summarizer import SummarizerFactory
from src.database.models import Database
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_single_video():
    """Demo the full pipeline with mock data"""
    
    # Mock video data
    video_info = {
        'video_id': 'DEMO123',
        'title': 'Demo Video: How To Build Amazing Apps',
        'channel_title': 'Tech Channel',
        'published_at': '2024-01-01T00:00:00Z',
        'description': 'A demo video about building apps'
    }
    
    # Mock transcript (since we're rate limited)
    mock_transcript = """
    Welcome to this amazing tutorial about building applications. Today we're going to learn about:
    
    1. Setting up your development environment
    2. Choosing the right frameworks
    3. Building scalable architecture
    4. Testing your application
    5. Deploying to production
    
    First, let's talk about setting up your development environment. This is crucial for any successful project.
    You need to ensure you have the right tools installed and configured properly.
    
    Next, we'll discuss framework selection. This decision will impact your entire project, so it's important
    to choose wisely based on your specific requirements and team expertise.
    
    When it comes to architecture, scalability should be a primary concern. Plan for growth from day one
    and design your systems to handle increased load gracefully.
    
    Testing is often overlooked but is absolutely essential. Implement automated testing early and
    maintain good test coverage throughout development.
    
    Finally, deployment should be automated and repeatable. Use CI/CD pipelines to ensure consistent
    and reliable deployments to production.
    
    Thank you for watching this tutorial. Don't forget to subscribe for more content!
    """
    
    print("🚀 Starting demo of the full pipeline...")
    
    try:
        # Initialize components
        print("📋 Initializing components...")
        notion_client = NotionClient(settings.notion_token, settings.notion_page_id)
        
        # Initialize LLM summarizer
        if settings.llm_provider == 'openai' and settings.openai_api_key:
            summarizer = SummarizerFactory.create_summarizer('openai', settings.openai_api_key)
        elif settings.llm_provider == 'anthropic' and settings.anthropic_api_key:
            summarizer = SummarizerFactory.create_summarizer('anthropic', settings.anthropic_api_key)
        else:
            raise ValueError("No valid LLM provider configured")
        
        db = Database(settings.database_url)
        
        # Test Notion connection
        print("🔗 Testing Notion connection...")
        notion_client.setup_page()
        
        # Check if demo video already exists
        video_id = video_info['video_id']
        if notion_client.check_if_video_exists(video_id):
            print(f"⚠️  Demo video {video_id} already exists in Notion")
            return
        
        if db.is_video_processed(video_id):
            print(f"⚠️  Demo video {video_id} already processed in database")
            return
        
        # Generate summary
        print("🤖 Generating AI summary...")
        summary = summarizer.summarize(
            transcript=mock_transcript,
            instructions=settings.summary_instructions,
            video_metadata=video_info
        )
        
        print("📄 Generated summary:")
        print("-" * 50)
        print(summary[:300] + "..." if len(summary) > 300 else summary)
        print("-" * 50)
        
        # Create Notion page
        print("📝 Creating Notion page...")
        page_title = f"{video_info['title']} [{video_id}]"
        notion_response = notion_client.create_page(
            title=page_title,
            content=summary,
            video_metadata=video_info
        )
        
        # Update database
        print("💾 Updating database...")
        db.add_processed_video({
            **video_info,
            'transcript_extracted': True,
            'summary_generated': True,
            'notion_page_created': True,
            'notion_page_id': notion_response['id']
        })
        
        print("✅ Demo completed successfully!")
        print(f"📖 Notion page created: {notion_response['url']}")
        
        # Cleanup
        db.close()
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        raise

if __name__ == "__main__":
    demo_single_video()