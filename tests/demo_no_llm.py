#!/usr/bin/env python3
"""Demo script to test Notion integration without LLM"""

from src.config import settings
from src.notion.client import NotionClient
from src.database.models import Database
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_notion_only():
    """Demo the Notion integration with mock data"""
    
    # Mock video data
    video_info = {
        'video_id': 'DEMO456',
        'title': 'Demo Video: Complete Guide to Modern Development',
        'channel_title': 'Dev Academy',
        'published_at': '2024-01-01T00:00:00Z',
        'description': 'A comprehensive guide to modern development practices'
    }
    
    # Mock summary (what would come from LLM)
    mock_summary = """
# Video Summary: Complete Guide to Modern Development

## Key Topics Covered

### 1. Development Environment Setup
- Choosing the right IDE and tools
- Setting up version control with Git
- Configuring linting and formatting tools
- Managing dependencies effectively

### 2. Modern Framework Selection
- **Frontend Frameworks**: React, Vue, Angular comparison
- **Backend Frameworks**: Node.js, Python, Go options
- **Database Choices**: SQL vs NoSQL considerations
- **Cloud Services**: AWS, GCP, Azure overview

### 3. Best Practices
- Code organization and structure
- Testing strategies (unit, integration, e2e)
- Documentation standards
- Security considerations

### 4. DevOps and Deployment
- CI/CD pipeline setup
- Container technologies (Docker, Kubernetes)
- Monitoring and logging
- Performance optimization

## Key Takeaways
- Start with a solid foundation and proper tooling
- Choose technologies based on project requirements, not trends
- Implement testing and documentation from day one
- Automate deployment processes for reliability
- Monitor and iterate based on real-world usage

## Recommended Next Steps
1. Set up a sample project using the discussed tools
2. Practice implementing CI/CD pipelines
3. Learn about security best practices
4. Explore monitoring and observability tools
"""
    
    print("🚀 Starting Notion-only demo...")
    
    try:
        # Initialize components
        print("📋 Initializing Notion client...")
        notion_client = NotionClient(settings.notion_token, settings.notion_page_id)
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
        
        print("📄 Using mock summary:")
        print("-" * 50)
        print(mock_summary[:400] + "..." if len(mock_summary) > 400 else mock_summary)
        print("-" * 50)
        
        # Create Notion page
        print("📝 Creating Notion page...")
        page_title = f"{video_info['title']} [{video_id}]"
        notion_response = notion_client.create_page(
            title=page_title,
            content=mock_summary,
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
        print(f"📖 Notion page created with ID: {notion_response['id']}")
        
        # Show what was created
        print("\n📋 What was created:")
        print(f"   • Notion page: '{page_title}'")
        print(f"   • Video metadata included")
        print(f"   • Database record added")
        print(f"   • Video ID: {video_id}")
        
        # Cleanup
        db.close()
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        raise

if __name__ == "__main__":
    demo_notion_only()