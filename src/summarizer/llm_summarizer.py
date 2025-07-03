from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
from openai import OpenAI
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class BaseSummarizer(ABC):
    @abstractmethod
    def summarize(self, transcript: str, instructions: str, video_metadata: Optional[Dict[str, Any]] = None) -> str:
        pass

class OpenAISummarizer(BaseSummarizer):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def summarize(self, transcript: str, instructions: str, video_metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Summarize transcript using OpenAI's GPT models.
        
        Args:
            transcript: The full transcript text
            instructions: Custom instructions for summarization
            video_metadata: Optional metadata about the video
            
        Returns:
            Summarized content
        """
        try:
            # Prepare the prompt
            system_prompt = f"""You are an expert at summarizing video transcripts. 
            Follow these instructions carefully: {instructions}
            
            Format your response in Markdown with clear sections and bullet points where appropriate."""
            
            user_prompt = f"Video Transcript:\n{transcript}"
            
            if video_metadata:
                metadata_str = f"\n\nVideo Information:\n"
                metadata_str += f"- Title: {video_metadata.get('title', 'N/A')}\n"
                metadata_str += f"- Channel: {video_metadata.get('channel_title', 'N/A')}\n"
                metadata_str += f"- Published: {video_metadata.get('published_at', 'N/A')}\n"
                user_prompt = metadata_str + "\n" + user_prompt
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            summary = response.choices[0].message.content
            logger.info("Successfully generated summary using OpenAI")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {str(e)}")
            raise

class AnthropicSummarizer(BaseSummarizer):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def summarize(self, transcript: str, instructions: str, video_metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Summarize transcript using Anthropic's Claude models.
        
        Args:
            transcript: The full transcript text
            instructions: Custom instructions for summarization
            video_metadata: Optional metadata about the video
            
        Returns:
            Summarized content
        """
        try:
            # Prepare the prompt
            system_prompt = f"""You are an expert at summarizing video transcripts. 
            Follow these instructions carefully: {instructions}
            
            Format your response in Markdown with clear sections and bullet points where appropriate."""
            
            user_prompt = f"Video Transcript:\n{transcript}"
            
            if video_metadata:
                metadata_str = f"\n\nVideo Information:\n"
                metadata_str += f"- Title: {video_metadata.get('title', 'N/A')}\n"
                metadata_str += f"- Channel: {video_metadata.get('channel_title', 'N/A')}\n"
                metadata_str += f"- Published: {video_metadata.get('published_at', 'N/A')}\n"
                user_prompt = metadata_str + "\n" + user_prompt
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            summary = response.content[0].text
            logger.info("Successfully generated summary using Anthropic")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary with Anthropic: {str(e)}")
            raise

class SummarizerFactory:
    @staticmethod
    def create_summarizer(provider: str, api_key: str, model: Optional[str] = None) -> BaseSummarizer:
        """
        Factory method to create appropriate summarizer based on provider.
        
        Args:
            provider: LLM provider ('openai' or 'anthropic')
            api_key: API key for the provider
            model: Optional model override
            
        Returns:
            Summarizer instance
        """
        if provider.lower() == 'openai':
            return OpenAISummarizer(api_key, model) if model else OpenAISummarizer(api_key)
        elif provider.lower() == 'anthropic':
            return AnthropicSummarizer(api_key, model) if model else AnthropicSummarizer(api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")