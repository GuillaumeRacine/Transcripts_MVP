#!/usr/bin/env python3
"""
Multi-part summarizer that generates comprehensive summaries using multiple AI calls.
"""

import logging
from typing import Optional, Dict, Any
from anthropic import Anthropic
import os
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MultiPartSummarizer:
    """Generates comprehensive summaries using multiple AI calls and saves as markdown."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", api_delay: float = 10.0):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.output_dir = "summaries"
        os.makedirs(self.output_dir, exist_ok=True)
        self.api_delay = api_delay  # Delay between API calls in seconds
        self.last_api_call_time = 0
        
        # Circuit breaker for overload protection
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.circuit_breaker_threshold = 3  # Open circuit after 3 consecutive failures
        self.circuit_breaker_timeout = 300  # 5 minutes before trying again
    
    def generate_comprehensive_summary(self, transcript: str, video_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate a comprehensive multi-part summary."""
        
        video_id = video_metadata.get('video_id', 'unknown') if video_metadata else 'unknown'
        title = video_metadata.get('title', 'Unknown Video') if video_metadata else 'Unknown Video'
        
        logger.info(f"Generating multi-part summary for: {title[:50]}...")
        
        # Part 1: Strategic Overview & Why This Matters
        part1 = self._generate_part1(transcript, video_metadata)
        
        # Part 2: Detailed Analysis & Key Takeaways  
        part2 = self._generate_part2(transcript, video_metadata)
        
        # Part 3: Implementation & Resources
        part3 = self._generate_part3(transcript, video_metadata)
        
        # Combine all parts into comprehensive summary
        full_summary = self._combine_parts(part1, part2, part3, video_metadata)
        
        # Save as markdown file
        self._save_markdown(full_summary, video_id, title)
        
        # Calculate estimated cost
        estimated_cost = self._calculate_cost(transcript, full_summary)
        
        logger.info(f"Generated comprehensive summary ({len(full_summary.split())} words) - Est. cost: ${estimated_cost:.3f}")
        return full_summary
    
    def _generate_part1(self, transcript: str, video_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate strategic overview and why this matters."""
        
        system_prompt = """You are an expert knowledge synthesizer. Generate Part 1 of a comprehensive analysis: Strategic Overview & Relevance.

Write 400-500 words covering:

**Why This Matters**: 
- Deeper implications and broader context
- Connection to current trends and developments  
- Strategic importance and timing
- Specific applications and use cases
- Real-world impact and consequences

**Strategic Context**:
- How this fits into the bigger picture
- Market/industry implications
- Future trajectory and potential
- Key stakeholders who should care

Write with sophisticated analysis and concrete examples. Be specific, detailed, and insightful."""

        user_prompt = self._build_user_prompt(transcript, video_metadata, "Part 1: Strategic Overview")
        
        return self._make_api_call(system_prompt, user_prompt, "Part 1")
    
    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker is open due to consecutive failures."""
        if self.consecutive_failures >= self.circuit_breaker_threshold:
            if self.last_failure_time:
                time_since_failure = time.time() - self.last_failure_time
                if time_since_failure < self.circuit_breaker_timeout:
                    remaining = self.circuit_breaker_timeout - time_since_failure
                    logger.warning(f"   ⚠️ Circuit breaker OPEN - too many consecutive failures. Wait {remaining:.0f}s before retry.")
                    return True
                else:
                    # Reset circuit breaker after timeout
                    logger.info(f"   🔄 Circuit breaker timeout expired - resetting failure count")
                    self.consecutive_failures = 0
                    self.last_failure_time = None
        return False

    def _make_api_call(self, system_prompt: str, user_prompt: str, part_name: str, max_retries: int = 6) -> str:
        """Make API call with circuit breaker and adaptive backoff for overloaded errors."""
        
        # Check circuit breaker
        if self._check_circuit_breaker():
            raise Exception(f"Circuit breaker open - API consistently overloaded")
        
        # Implement proactive rate limiting with adaptive delay based on recent failures
        current_time = time.time()
        adaptive_delay = self.api_delay + (self.consecutive_failures * 10)  # Add 10s per recent failure
        time_since_last_call = current_time - self.last_api_call_time
        
        if time_since_last_call < adaptive_delay:
            wait_time = adaptive_delay - time_since_last_call
            logger.info(f"   ⏱️  Adaptive rate limiting: waiting {wait_time:.1f}s (base: {self.api_delay}s + {self.consecutive_failures * 10}s for failures)...")
            time.sleep(wait_time)
        
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=0.3,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                
                # Success - reset circuit breaker
                self.consecutive_failures = 0
                self.last_failure_time = None
                
                logger.info(f"   ✅ {part_name} generated successfully")
                self.last_api_call_time = time.time()
                return response.content[0].text
                
            except Exception as e:
                if "overloaded" in str(e).lower() or "529" in str(e) or "rate" in str(e).lower():
                    # Ultra-conservative exponential backoff: 30, 60, 120, 240, 480, 960 seconds
                    wait_time = 30 * (2 ** attempt)
                    logger.warning(f"   ⚠️ {part_name} overloaded (attempt {attempt + 1}/{max_retries}), waiting {wait_time}s...")
                    
                    # If we're past attempt 3, suggest the user try later
                    if attempt >= 3:
                        logger.warning(f"   ⚠️ API severely overloaded - consider trying again in 30+ minutes")
                    
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"   ❌ {part_name} failed: {str(e)}")
                    raise
        
        # All retries failed - update circuit breaker
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        
        logger.error(f"   ❌ {part_name} failed after {max_retries} attempts - API severely overloaded")
        logger.error(f"   ❌ Consecutive failures: {self.consecutive_failures}/{self.circuit_breaker_threshold}")
        
        raise Exception(f"Claude API severely overloaded after {max_retries} attempts - try again later")
    
    def _generate_part2(self, transcript: str, video_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate detailed analysis and key takeaways."""
        
        system_prompt = """You are an expert knowledge synthesizer. Generate Part 2 of a comprehensive analysis: Detailed Analysis & Key Takeaways.

Write 600-700 words covering:

**Key Takeaways** (organize into 4-6 major themes):
For each theme:
- Rich context and background information
- Specific details, data points, examples mentioned
- Evidence and reasoning behind each point
- Connections to related concepts
- Nuanced insights showing deep understanding
- Counterintuitive or surprising elements

**Technical Details**:
- Methodologies, frameworks, or systems discussed
- Specific metrics, numbers, or measurements
- Step-by-step processes or workflows
- Tools, technologies, or platforms mentioned

Be comprehensive, detailed, and analytically rigorous. Include all specific examples and case studies mentioned."""

        user_prompt = self._build_user_prompt(transcript, video_metadata, "Part 2: Detailed Analysis")
        
        return self._make_api_call(system_prompt, user_prompt, "Part 2")
    
    def _generate_part3(self, transcript: str, video_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate implementation guidance and resources."""
        
        system_prompt = """You are an expert knowledge synthesizer. Generate Part 3 of a comprehensive analysis: Implementation & Resources.

Write 400-500 words covering:

**Actionable Implementation**:
- Step-by-step guidance for applying insights
- Specific tools, techniques, frameworks to use
- Common challenges and how to overcome them
- Success metrics and measurement approaches
- Timeline and sequencing considerations

**Comprehensive Resources**:
- Books (with specific quotes/concepts if mentioned)
- Research papers and studies (with key findings)
- Tools, software, platforms mentioned
- People mentioned (with credentials/relevance)
- Companies, organizations, case studies
- Specific data points, statistics, methodologies
- Related concepts for further exploration

**Next Steps**:
- Immediate actions to take
- Long-term development path
- Additional learning resources

Be practical, specific, and actionable. Focus on implementation wisdom."""

        user_prompt = self._build_user_prompt(transcript, video_metadata, "Part 3: Implementation")
        
        return self._make_api_call(system_prompt, user_prompt, "Part 3")
    
    def _build_user_prompt(self, transcript: str, video_metadata: Optional[Dict[str, Any]], part_name: str) -> str:
        """Build user prompt with video metadata."""
        
        user_prompt_parts = []
        
        if video_metadata:
            user_prompt_parts.append(f"=== {part_name} ===")
            user_prompt_parts.append("")
            user_prompt_parts.append("VIDEO INFORMATION:")
            user_prompt_parts.append(f"Title: {video_metadata.get('title', 'N/A')}")
            user_prompt_parts.append(f"Channel: {video_metadata.get('channel_title', 'N/A')}")
            user_prompt_parts.append(f"URL: {video_metadata.get('video_url', 'N/A')}")
            user_prompt_parts.append("")
        
        user_prompt_parts.append("TRANSCRIPT:")
        user_prompt_parts.append(transcript)
        
        return "\n".join(user_prompt_parts)
    
    def _combine_parts(self, part1: str, part2: str, part3: str, video_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Combine all parts into a comprehensive summary."""
        
        title = video_metadata.get('title', 'Unknown Video') if video_metadata else 'Unknown Video'
        channel = video_metadata.get('channel_title', 'Unknown Channel') if video_metadata else 'Unknown Channel'
        url = video_metadata.get('video_url', '#') if video_metadata else '#'
        published = video_metadata.get('published_at', 'Unknown') if video_metadata else 'Unknown'
        
        header = f"""# {title}

<aside>
📺 **Channel:** {channel}  
📅 **Published:** {published}  
🔗 **YouTube:** {url}
</aside>

---

"""
        
        # Clean up parts - remove any duplicate headers and format consistently
        part1_clean = self._clean_part_content(part1, "## 🎯 Strategic Overview & Why This Matters")
        part2_clean = self._clean_part_content(part2, "## 📊 Detailed Analysis & Key Takeaways")
        part3_clean = self._clean_part_content(part3, "## 🚀 Implementation Guide & Resources")
        
        combined = header + part1_clean + "\n\n" + part2_clean + "\n\n" + part3_clean
        
        # Add footer
        combined += f"\n\n---\n\n**📖 Source:** [{title}]({url})  \n**🤖 Generated:** {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} using Claude 3 Opus"
        
        return combined
    
    def _clean_part_content(self, content: str, expected_header: str) -> str:
        """Clean and format part content with consistent headers."""
        
        # Remove any existing similar headers
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that look like headers we're going to replace
            if line.startswith('##') and ('Strategic' in line or 'Analysis' in line or 'Implementation' in line or 'Takeaways' in line):
                continue
            if line.startswith('===') or line.startswith('Part'):
                continue
            cleaned_lines.append(line)
        
        # Add proper header and cleaned content
        result = expected_header + "\n\n" + '\n'.join(cleaned_lines).strip()
        
        return result
    
    def _save_markdown(self, content: str, video_id: str, title: str) -> str:
        """Save summary as markdown file."""
        
        # Clean filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        
        filename = f"{video_id}_{safe_title}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Saved markdown summary: {filepath}")
        return filepath
    
    def _calculate_cost(self, transcript: str, summary: str) -> float:
        """Calculate estimated cost for Claude 3 Opus API calls."""
        
        # Estimate tokens (rough approximation: 1 token ≈ 0.75 words)
        transcript_tokens = len(transcript.split()) / 0.75
        summary_tokens = len(summary.split()) / 0.75
        
        # 3 API calls with prompts (~500 tokens each)
        prompt_tokens = 500 * 3
        
        # Input cost: transcript + prompts for 3 calls
        input_tokens = (transcript_tokens + prompt_tokens) * 3
        input_cost = input_tokens * (15 / 1_000_000)  # $15 per 1M input tokens
        
        # Output cost: generated summary tokens
        output_cost = summary_tokens * (75 / 1_000_000)  # $75 per 1M output tokens
        
        return input_cost + output_cost