from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class ProcessedVideo(Base):
    __tablename__ = 'processed_videos'
    
    video_id = Column(String(50), primary_key=True)
    title = Column(String(500), nullable=False)
    channel_title = Column(String(200))
    published_at = Column(DateTime)
    processed_at = Column(DateTime, default=datetime.utcnow)
    transcript_extracted = Column(Boolean, default=False)
    summary_generated = Column(Boolean, default=False)
    notion_page_created = Column(Boolean, default=False)
    notion_page_id = Column(String(100))
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<ProcessedVideo(video_id='{self.video_id}', title='{self.title}')>"

class Database:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_processed_video(self, video_data: dict) -> ProcessedVideo:
        """Add a new processed video to the database or update existing."""
        try:
            # Check if video already exists
            existing = self.get_processed_video(video_data['video_id'])
            if existing:
                # Update existing video
                for key, value in video_data.items():
                    if key != 'video_id' and hasattr(existing, key):
                        if key == 'published_at' and isinstance(value, str):
                            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        setattr(existing, key, value)
                self.session.commit()
                return existing
            
            # Create new video
            video = ProcessedVideo(
                video_id=video_data['video_id'],
                title=video_data['title'],
                channel_title=video_data.get('channel_title'),
                published_at=datetime.fromisoformat(video_data['published_at'].replace('Z', '+00:00')),
                transcript_extracted=video_data.get('transcript_extracted', False),
                summary_generated=video_data.get('summary_generated', False),
                notion_page_created=video_data.get('notion_page_created', False),
                notion_page_id=video_data.get('notion_page_id'),
                error_message=video_data.get('error_message')
            )
            self.session.add(video)
            self.session.commit()
            return video
        except Exception as e:
            self.session.rollback()
            raise
    
    def get_processed_video(self, video_id: str) -> ProcessedVideo:
        """Get a processed video by ID."""
        return self.session.query(ProcessedVideo).filter_by(video_id=video_id).first()
    
    def is_video_processed(self, video_id: str) -> bool:
        """Check if a video has been processed."""
        video = self.get_processed_video(video_id)
        return video is not None and video.notion_page_created
    
    def update_video_status(self, video_id: str, **kwargs):
        """Update the status of a processed video."""
        try:
            video = self.get_processed_video(video_id)
            if video:
                for key, value in kwargs.items():
                    if hasattr(video, key):
                        setattr(video, key, value)
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise
    
    def get_all_processed_videos(self):
        """Get all processed videos."""
        return self.session.query(ProcessedVideo).all()
    
    def get_failed_videos(self):
        """Get videos that failed processing."""
        return self.session.query(ProcessedVideo).filter(
            ProcessedVideo.error_message.isnot(None)
        ).all()
    
    def close(self):
        """Close the database session."""
        self.session.close()