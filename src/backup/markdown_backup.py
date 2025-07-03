"""
Markdown backup system for video summaries when Notion integration fails.
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import re

logger = logging.getLogger(__name__)

class MarkdownBackup:
    """Handles creating markdown backups of video summaries."""
    
    def __init__(self, backup_dir: str = "markdown_backups"):
        """
        Initialize the markdown backup system.
        
        Args:
            backup_dir: Directory to store markdown backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        logger.info(f"Markdown backup directory: {self.backup_dir.absolute()}")
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to be safe for filesystem.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized
    
    def create_backup(self, video_info: Dict, summary: str, transcript: Optional[str] = None) -> str:
        """
        Create a markdown backup file for a video summary.
        
        Args:
            video_info: Dictionary containing video metadata
            summary: AI-generated summary
            transcript: Optional transcript text
            
        Returns:
            Path to the created backup file
        """
        try:
            # Create filename
            video_id = video_info.get('video_id', 'unknown')
            title = video_info.get('title', 'Unknown Title')
            safe_title = self.sanitize_filename(title)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{safe_title}_{video_id}.md"
            
            filepath = self.backup_dir / filename
            
            # Create markdown content
            content = self._create_markdown_content(video_info, summary, transcript)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created markdown backup: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating markdown backup: {str(e)}")
            raise
    
    def _create_markdown_content(self, video_info: Dict, summary: str, transcript: Optional[str] = None) -> str:
        """
        Create the markdown content for the backup file.
        
        Args:
            video_info: Video metadata
            summary: AI-generated summary
            transcript: Optional transcript
            
        Returns:
            Formatted markdown content
        """
        # Extract metadata
        title = video_info.get('title', 'Unknown Title')
        video_id = video_info.get('video_id', 'unknown')
        channel = video_info.get('channel_title', 'Unknown Channel')
        published = video_info.get('published_at', 'Unknown Date')
        description = video_info.get('description', '')
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Format published date
        try:
            if published and published != 'Unknown Date':
                published_dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                formatted_date = published_dt.strftime("%B %d, %Y")
            else:
                formatted_date = published
        except:
            formatted_date = published
        
        # Create markdown content
        content = f"""# {title}

## Video Information

- **Video ID:** {video_id}
- **Channel:** {channel}
- **Published:** {formatted_date}
- **YouTube URL:** [{youtube_url}]({youtube_url})
- **Backup Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

{summary}

## Video Description

{description[:500]}{'...' if len(description) > 500 else ''}

"""
        
        # Add transcript if available
        if transcript:
            content += f"""## Transcript

{transcript}

"""
        
        # Add footer
        content += """---

*This markdown file was created as a backup when the Notion integration failed.*
"""
        
        return content
    
    def list_backups(self) -> list:
        """
        List all backup files in the backup directory.
        
        Returns:
            List of backup file paths
        """
        try:
            backups = list(self.backup_dir.glob("*.md"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return [str(backup) for backup in backups]
        except Exception as e:
            logger.error(f"Error listing backups: {str(e)}")
            return []
    
    def get_backup_stats(self) -> Dict:
        """
        Get statistics about the backup directory.
        
        Returns:
            Dictionary with backup statistics
        """
        try:
            backups = self.list_backups()
            total_size = sum(Path(backup).stat().st_size for backup in backups)
            
            return {
                'total_backups': len(backups),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'backup_directory': str(self.backup_dir.absolute())
            }
        except Exception as e:
            logger.error(f"Error getting backup stats: {str(e)}")
            return {}
    
    def cleanup_old_backups(self, max_backups: int = 100) -> int:
        """
        Remove old backup files if there are too many.
        
        Args:
            max_backups: Maximum number of backups to keep
            
        Returns:
            Number of backups removed
        """
        try:
            backups = self.list_backups()
            
            if len(backups) <= max_backups:
                logger.info(f"No cleanup needed. Current backups: {len(backups)}")
                return 0
            
            # Remove oldest backups
            to_remove = backups[max_backups:]
            removed_count = 0
            
            for backup_path in to_remove:
                try:
                    os.remove(backup_path)
                    removed_count += 1
                    logger.info(f"Removed old backup: {backup_path}")
                except Exception as e:
                    logger.error(f"Error removing backup {backup_path}: {str(e)}")
            
            logger.info(f"Cleanup complete. Removed {removed_count} old backups.")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error during backup cleanup: {str(e)}")
            return 0