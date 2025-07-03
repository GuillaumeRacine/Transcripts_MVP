from notion_client import Client
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NotionClient:
    def __init__(self, token: str, page_id: str):
        self.client = Client(auth=token)
        self.page_id = page_id
    
    def create_page(self, 
                   title: str, 
                   content: str, 
                   video_metadata: Dict[str, Any],
                   transcript_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new page in Notion database.
        
        Args:
            title: Page title (video title)
            content: Markdown content (summary)
            video_metadata: Video metadata including video_id, channel, etc.
            transcript_url: Optional URL to full transcript
            
        Returns:
            Created page information
        """
        try:
            # Convert markdown content to Notion blocks
            blocks = self._markdown_to_notion_blocks(content, video_metadata)
            
            # Prepare properties for the database
            properties = {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Video ID": {
                    "rich_text": [
                        {
                            "text": {
                                "content": video_metadata.get('video_id', '')
                            }
                        }
                    ]
                },
                "Channel": {
                    "rich_text": [
                        {
                            "text": {
                                "content": video_metadata.get('channel_title', '')
                            }
                        }
                    ]
                },
                "Published Date": {
                    "date": {
                        "start": video_metadata.get('published_at', datetime.now().isoformat())
                    }
                },
                "YouTube URL": {
                    "url": f"https://www.youtube.com/watch?v={video_metadata.get('video_id', '')}"
                },
                "Processed Date": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            }
            
            # Add transcript URL if provided
            if transcript_url:
                properties["Transcript URL"] = {"url": transcript_url}
            
            # Create the page as a child of the specified page
            response = self.client.pages.create(
                parent={"page_id": self.page_id},
                properties={
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                children=blocks
            )
            
            logger.info(f"Successfully created Notion page for video: {title}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating Notion page: {str(e)}")
            raise
    
    def check_if_video_exists(self, video_id: str) -> bool:
        """
        Check if a video has already been processed and added to Notion.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            True if video exists as child page, False otherwise
        """
        try:
            # Get all child pages of the parent page
            response = self.client.blocks.children.list(block_id=self.page_id)
            
            # Check if any child page title contains the video ID
            for block in response.get('results', []):
                if block.get('type') == 'child_page':
                    # Check if video ID is in the page title
                    page_title = block.get('child_page', {}).get('title', '')
                    if video_id in page_title:
                        return True
                    
                    # Quick check of the first few blocks of content only
                    page_id = block['id']
                    try:
                        page_content = self.client.blocks.children.list(block_id=page_id, page_size=5)
                        for content_block in page_content.get('results', []):
                            if self._block_contains_video_id(content_block, video_id):
                                return True
                    except:
                        continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if video exists: {str(e)}")
            return False
    
    def _block_contains_video_id(self, block: dict, video_id: str) -> bool:
        """Helper method to check if a block contains the video ID."""
        try:
            if block.get('type') == 'paragraph':
                rich_text = block.get('paragraph', {}).get('rich_text', [])
                for text_obj in rich_text:
                    if video_id in text_obj.get('text', {}).get('content', ''):
                        return True
            return False
        except:
            return False
    
    def _markdown_to_notion_blocks(self, markdown_content: str, video_metadata: dict = None) -> List[Dict[str, Any]]:
        """
        Convert markdown content to Notion blocks.
        This is a simplified version - you may want to use a proper markdown parser.
        
        Args:
            markdown_content: Markdown formatted content
            video_metadata: Video metadata to include
            
        Returns:
            List of Notion blocks
        """
        blocks = []
        
        # Add video metadata at the top
        if video_metadata:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"🎥 Video ID: {video_metadata.get('video_id', '')}"},
                        "annotations": {"code": True}
                    }]
                }
            })
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"📺 Channel: {video_metadata.get('channel_title', '')}"}
                    }]
                }
            })
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"🔗 "},
                        "href": f"https://www.youtube.com/watch?v={video_metadata.get('video_id', '')}"
                    }, {
                        "type": "text", 
                        "text": {"content": "Watch on YouTube"},
                        "href": f"https://www.youtube.com/watch?v={video_metadata.get('video_id', '')}"
                    }]
                }
            })
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        
        lines = markdown_content.split('\n')
        
        current_list_items = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Empty line - end any current list
                if in_list and current_list_items:
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": item}}]
                        }
                    } for item in current_list_items)
                    current_list_items = []
                    in_list = False
                continue
            
            # Headers
            if line.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })
            elif line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                    }
                })
            # Bullet points
            elif line.startswith('- ') or line.startswith('* '):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
            # Bold text (simplified)
            elif line.startswith('**') and line.endswith('**'):
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": line[2:-2]},
                            "annotations": {"bold": True}
                        }]
                    }
                })
            # Regular paragraph
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line}}]
                    }
                })
        
        return blocks
    
    def setup_page(self) -> None:
        """
        Verify the Notion page exists and is accessible.
        This should be called during initial setup.
        """
        try:
            # Try to retrieve the page to verify access
            page = self.client.pages.retrieve(page_id=self.page_id)
            logger.info(f"Successfully connected to Notion page: {page.get('properties', {}).get('title', {})}")
                
        except Exception as e:
            logger.error(f"Error accessing Notion page: {str(e)}")
            raise