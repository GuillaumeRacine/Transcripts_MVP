"""
Notion database client for managing video processing workflow.
"""
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from notion_client import Client
from notion_client.errors import RequestTimeoutError, HTTPResponseError

logger = logging.getLogger(__name__)

class NotionDatabaseClient:
    """Handles Notion database operations for video processing."""
    
    def __init__(self, token: str, database_id: str):
        """
        Initialize the Notion database client.
        
        Args:
            token: Notion integration token
            database_id: ID of the Notion database
        """
        self.client = Client(auth=token)
        self.database_id = database_id
        logger.info(f"Initialized Notion database client for database: {database_id}")
    
    def extract_video_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID or None if not found
        """
        if not url:
            return None
        
        # YouTube URL patterns
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'  # Just the video ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_unprocessed_videos(self) -> List[Dict[str, Any]]:
        """
        Get all videos from the database that haven't been processed yet.
        
        Returns:
            List of unprocessed video records
        """
        try:
            # Query for videos where Status is not "Completed"
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "or": [
                        {
                            "property": "Status",
                            "select": {
                                "does_not_equal": "Completed"
                            }
                        },
                        {
                            "property": "Status",
                            "select": {
                                "is_empty": True
                            }
                        }
                    ]
                },
                sorts=[
                    {
                        "timestamp": "created_time",
                        "direction": "ascending"
                    }
                ]
            )
            
            unprocessed = []
            
            for page in response.get("results", []):
                properties = page.get("properties", {})
                
                # Extract video URL
                video_url_prop = properties.get("Video URL", {})
                video_url = None
                
                if video_url_prop.get("type") == "url":
                    video_url = video_url_prop.get("url")
                elif video_url_prop.get("type") == "rich_text":
                    rich_text = video_url_prop.get("rich_text", [])
                    if rich_text:
                        video_url = rich_text[0].get("plain_text", "")
                
                if not video_url:
                    logger.warning(f"No video URL found in page {page['id']}")
                    continue
                
                # Extract video ID
                video_id = self.extract_video_id_from_url(video_url)
                if not video_id:
                    logger.warning(f"Could not extract video ID from URL: {video_url}")
                    continue
                
                # Extract title if provided
                title_prop = properties.get("Title", {})
                title = None
                if title_prop.get("type") == "title":
                    title_texts = title_prop.get("title", [])
                    if title_texts:
                        title = title_texts[0].get("plain_text", "")
                
                # Extract status
                status_prop = properties.get("Status", {})
                status = None
                if status_prop.get("type") == "select":
                    status_select = status_prop.get("select")
                    if status_select:
                        status = status_select.get("name")
                
                unprocessed.append({
                    "page_id": page["id"],
                    "video_url": video_url,
                    "video_id": video_id,
                    "title": title,
                    "status": status,
                    "created_time": page.get("created_time"),
                    "last_edited_time": page.get("last_edited_time")
                })
            
            logger.info(f"Found {len(unprocessed)} unprocessed videos")
            return unprocessed
            
        except Exception as e:
            logger.error(f"Error querying database: {str(e)}")
            return []
    
    def update_video_status(self, page_id: str, status: str, **kwargs) -> bool:
        """
        Update a video's processing status and other fields.
        
        Args:
            page_id: Notion page ID
            status: New status value
            **kwargs: Additional properties to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            properties = {
                "Status": {
                    "select": {
                        "name": status
                    }
                }
            }
            
            # Add optional fields
            if "title" in kwargs and kwargs["title"]:
                properties["Title"] = {
                    "title": [
                        {
                            "text": {
                                "content": kwargs["title"]
                            }
                        }
                    ]
                }
            
            if "video_id" in kwargs and kwargs["video_id"]:
                properties["Video ID"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": kwargs["video_id"]
                            }
                        }
                    ]
                }
            
            if "channel" in kwargs and kwargs["channel"]:
                properties["Channel"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": kwargs["channel"]
                            }
                        }
                    ]
                }
            
            if "duration" in kwargs and kwargs["duration"]:
                properties["Duration"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": kwargs["duration"]
                            }
                        }
                    ]
                }
            
            if "summary_page_id" in kwargs and kwargs["summary_page_id"]:
                properties["Summary Page"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": kwargs["summary_page_id"]
                            }
                        }
                    ]
                }
            
            if "error_message" in kwargs and kwargs["error_message"]:
                properties["Error"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": str(kwargs["error_message"])[:2000]  # Notion limit
                            }
                        }
                    ]
                }
            
            if "processed_date" in kwargs:
                properties["Processed Date"] = {
                    "date": {
                        "start": kwargs["processed_date"].isoformat() if kwargs["processed_date"] else None
                    }
                }
            
            self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            logger.info(f"Updated video status to '{status}' for page {page_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating video status: {str(e)}")
            return False
    
    def create_summary_page(self, title: str, content: str, video_metadata: Dict, parent_page_id: Optional[str] = None) -> Optional[Dict]:
        """
        Create a summary page for the video.
        
        Args:
            title: Page title
            content: Markdown content
            video_metadata: Video metadata
            parent_page_id: Optional parent page ID
            
        Returns:
            Created page response or None
        """
        try:
            # Convert markdown to Notion blocks
            blocks = self._markdown_to_blocks(content, video_metadata)
            
            # Use provided parent page ID, or fall back to database
            if parent_page_id:
                parent = {"type": "page_id", "page_id": parent_page_id}
            else:
                parent = {"type": "database_id", "database_id": self.database_id}
            
            response = self.client.pages.create(
                parent=parent,
                properties={
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                },
                children=blocks
            )
            
            logger.info(f"Created summary page: {title}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating summary page: {str(e)}")
            return None
    
    def _markdown_to_blocks(self, markdown_content: str, video_metadata: Dict) -> List[Dict]:
        """
        Convert markdown content to Notion blocks.
        
        Args:
            markdown_content: Markdown formatted content
            video_metadata: Video metadata
            
        Returns:
            List of Notion blocks
        """
        blocks = []
        
        # Add video metadata at the top
        video_id = video_metadata.get('video_id', 'unknown')
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Video info block
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"🎥 Channel: {video_metadata.get('channel_title', 'Unknown')}\n"
                                     f"📅 Published: {video_metadata.get('published_at', 'Unknown')}\n"
                                     f"🔗 YouTube: {youtube_url}",
                        }
                    }
                ],
                "icon": {
                    "type": "emoji",
                    "emoji": "📺"
                }
            }
        })
        
        # Process markdown content
        lines = markdown_content.split('\n')
        current_text = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if current_text:
                    # Add paragraph block
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": '\n'.join(current_text)
                                    }
                                }
                            ]
                        }
                    })
                    current_text = []
                continue
            
            # Headers
            if line.startswith('# '):
                if current_text:
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": '\n'.join(current_text)
                                    }
                                }
                            ]
                        }
                    })
                    current_text = []
                
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": line[2:]
                                }
                            }
                        ]
                    }
                })
            elif line.startswith('## '):
                if current_text:
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": '\n'.join(current_text)
                                    }
                                }
                            ]
                        }
                    })
                    current_text = []
                
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": line[3:]
                                }
                            }
                        ]
                    }
                })
            elif line.startswith('### '):
                if current_text:
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": '\n'.join(current_text)
                                    }
                                }
                            ]
                        }
                    })
                    current_text = []
                
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": line[4:]
                                }
                            }
                        ]
                    }
                })
            else:
                current_text.append(line)
        
        # Add remaining text
        if current_text:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": '\n'.join(current_text)
                            }
                        }
                    ]
                }
            })
        
        return blocks
    
    def setup_database_schema(self) -> bool:
        """
        Verify and setup the database schema with required properties.
        
        Returns:
            True if schema is correct, False otherwise
        """
        try:
            response = self.client.databases.retrieve(database_id=self.database_id)
            properties = response.get("properties", {})
            
            required_properties = {
                "Title": "title",
                "Video URL": "url", 
                "Video ID": "rich_text",
                "Status": "select",
                "Channel": "rich_text",
                "Duration": "rich_text",
                "Processed Date": "date",
                "Summary Page": "rich_text",
                "Error": "rich_text"
            }
            
            missing_properties = []
            for prop_name, prop_type in required_properties.items():
                if prop_name not in properties:
                    missing_properties.append(f"{prop_name} ({prop_type})")
                else:
                    actual_type = properties[prop_name].get("type")
                    if actual_type != prop_type:
                        missing_properties.append(f"{prop_name} (expected {prop_type}, got {actual_type})")
            
            if missing_properties:
                logger.warning(f"Database schema incomplete. Missing/incorrect properties: {missing_properties}")
                logger.info("Please add these properties to your Notion database:")
                for prop in missing_properties:
                    logger.info(f"  - {prop}")
                return False
            
            logger.info("✅ Database schema is correctly configured")
            return True
            
        except Exception as e:
            logger.error(f"Error checking database schema: {str(e)}")
            return False
    
    def get_processed_videos(self) -> List[Dict[str, Any]]:
        """
        Get all processed videos from the database.
        
        Returns:
            List of processed video records
        """
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Status",
                    "select": {
                        "equals": "Completed"
                    }
                }
            )
            
            processed_videos = []
            for page in response.get('results', []):
                video_record = self._extract_video_info(page)
                if video_record:
                    processed_videos.append(video_record)
            
            return processed_videos
            
        except Exception as e:
            logger.error(f"Error fetching processed videos: {str(e)}")
            return []
    
    def create_page(self, properties: Dict) -> Optional[Dict]:
        """
        Create a new page in the Notion database.
        
        Args:
            properties: Page properties dictionary
            
        Returns:
            Created page response or None if failed
        """
        try:
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            return response
            
        except Exception as e:
            logger.error(f"Error creating page: {str(e)}")
            return None
    
    def _extract_video_info(self, page) -> Optional[Dict]:
        """
        Extract video information from a Notion page.
        
        Args:
            page: Notion page object
            
        Returns:
            Dictionary with video information or None if invalid
        """
        try:
            properties = page.get('properties', {})
            
            # Extract video URL
            video_url_prop = properties.get('Video URL', {})
            if video_url_prop.get('type') == 'url':
                video_url = video_url_prop.get('url')
                if not video_url:
                    return None
            else:
                return None
            
            # Extract video ID from URL
            video_id = self.extract_video_id_from_url(video_url)
            if not video_id:
                return None
            
            # Extract title
            title_prop = properties.get('Title', {})
            title = 'Untitled'
            if title_prop.get('type') == 'title':
                title_array = title_prop.get('title', [])
                if title_array and len(title_array) > 0:
                    title = title_array[0].get('text', {}).get('content', 'Untitled')
            
            return {
                'page_id': page['id'],
                'video_id': video_id,
                'video_url': video_url,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"Error extracting video info from page: {str(e)}")
            return None