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
            # Prepare the prompt with clearer formatting
            system_prompt = f"""You are an expert at summarizing video transcripts. 

CRITICAL REQUIREMENT: Your response MUST be 1,000-1,500 words. This is non-negotiable. Write detailed, comprehensive content that reaches this word count.

IMPORTANT INSTRUCTIONS:
{instructions}

FORMATTING REQUIREMENTS:
Use this exact markdown structure for your response:

## 🎯 Why This Matters
[Brief explanation of relevance and importance]

## 📋 Key Takeaways

### [Topic 1 Name]
- [Key point 1]
- [Key point 2]
- [Key point 3]

### [Topic 2 Name]
- [Key point 1]
- [Key point 2]
- [Key point 3]

### [Topic 3 Name] 
- [Key point 1]
- [Key point 2]
- [Key point 3]

## 💡 Actionable Insights
- [Practical takeaway 1]
- [Practical takeaway 2]
- [Practical takeaway 3]

## 📚 Resources & References

### Books/Articles
- [Resource 1]
- [Resource 2]

### Organizations/Tools
- [Organization 1]
- [Organization 2]

### Key Concepts
- **[Concept 1]**: [Brief definition]
- **[Concept 2]**: [Brief definition]

Use clear headings, bullet points, and bold text for emphasis. Keep sections well-organized and scannable."""
            
            # Build user prompt with video info first
            user_prompt_parts = []
            
            if video_metadata:
                user_prompt_parts.append("VIDEO INFORMATION:")
                user_prompt_parts.append(f"Title: {video_metadata.get('title', 'N/A')}")
                user_prompt_parts.append(f"Channel: {video_metadata.get('channel_title', 'N/A')}")
                user_prompt_parts.append(f"Published: {video_metadata.get('published_at', 'N/A')}")
                user_prompt_parts.append(f"URL: {video_metadata.get('video_url', 'N/A')}")
                user_prompt_parts.append("")
                user_prompt_parts.append("TRANSCRIPT:")
            
            user_prompt_parts.append(transcript)
            user_prompt = "\n".join(user_prompt_parts)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=6000  # Increased for 1000-1500 word summaries
            )
            
            summary = response.choices[0].message.content
            logger.info("Successfully generated summary using OpenAI")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {str(e)}")
            raise

class AnthropicSummarizer(BaseSummarizer):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
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
            # Prepare the prompt with clearer formatting
            system_prompt = f"""You are an expert at summarizing video transcripts. 

CRITICAL REQUIREMENT: Your response MUST be 1,000-1,500 words. This is non-negotiable. Write detailed, comprehensive content that reaches this word count.

IMPORTANT INSTRUCTIONS:
{instructions}

FORMATTING REQUIREMENTS:
Use this exact markdown structure for your response:

## 🎯 Why This Matters
[Brief explanation of relevance and importance]

## 📋 Key Takeaways

### [Topic 1 Name]
- [Key point 1]
- [Key point 2]
- [Key point 3]

### [Topic 2 Name]
- [Key point 1]
- [Key point 2]
- [Key point 3]

### [Topic 3 Name] 
- [Key point 1]
- [Key point 2]
- [Key point 3]

## 💡 Actionable Insights
- [Practical takeaway 1]
- [Practical takeaway 2]
- [Practical takeaway 3]

## 📚 Resources & References

### Books/Articles
- [Resource 1]
- [Resource 2]

### Organizations/Tools
- [Organization 1]
- [Organization 2]

### Key Concepts
- **[Concept 1]**: [Brief definition]
- **[Concept 2]**: [Brief definition]

Use clear headings, bullet points, and bold text for emphasis. Keep sections well-organized and scannable."""
            
            # Build user prompt with video info first
            user_prompt_parts = []
            
            if video_metadata:
                user_prompt_parts.append("VIDEO INFORMATION:")
                user_prompt_parts.append(f"Title: {video_metadata.get('title', 'N/A')}")
                user_prompt_parts.append(f"Channel: {video_metadata.get('channel_title', 'N/A')}")
                user_prompt_parts.append(f"Published: {video_metadata.get('published_at', 'N/A')}")
                user_prompt_parts.append(f"URL: {video_metadata.get('video_url', 'N/A')}")
                user_prompt_parts.append("")
                user_prompt_parts.append("TRANSCRIPT:")
            
            user_prompt_parts.append(transcript)
            user_prompt = "\n".join(user_prompt_parts)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,  # Claude Opus maximum
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