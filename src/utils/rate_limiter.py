import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class RateLimiter:
    """Smart rate limiter to avoid hitting YouTube API limits"""
    
    def __init__(self, 
                 max_requests_per_hour: int = 200,
                 max_requests_per_day: int = 250,
                 min_delay_seconds: float = 2.0,
                 backoff_multiplier: float = 2.0,
                 cache_file: str = "rate_limit_cache.json"):
        """
        Initialize rate limiter
        
        Args:
            max_requests_per_hour: Maximum transcript requests per hour
            max_requests_per_day: Maximum transcript requests per day  
            min_delay_seconds: Minimum delay between requests
            backoff_multiplier: Multiplier for exponential backoff
            cache_file: File to persist rate limit data
        """
        self.max_requests_per_hour = max_requests_per_hour
        self.max_requests_per_day = max_requests_per_day
        self.min_delay_seconds = min_delay_seconds
        self.backoff_multiplier = backoff_multiplier
        self.cache_file = cache_file
        
        # Load existing data
        self.data = self._load_cache()
        
        # Initialize tracking
        if 'requests' not in self.data:
            self.data['requests'] = []
        if 'last_request_time' not in self.data:
            self.data['last_request_time'] = None
        if 'consecutive_failures' not in self.data:
            self.data['consecutive_failures'] = 0
        if 'backoff_until' not in self.data:
            self.data['backoff_until'] = None
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cached rate limit data"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_cache(self):
        """Save rate limit data to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save rate limit cache: {str(e)}")
    
    def _clean_old_requests(self):
        """Remove request timestamps older than 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        self.data['requests'] = [
            req_time for req_time in self.data['requests']
            if datetime.fromisoformat(req_time) > cutoff
        ]
    
    def can_make_request(self) -> tuple[bool, Optional[str]]:
        """
        Check if we can make a request now
        
        Returns:
            (can_make_request, reason_if_not)
        """
        now = datetime.now()
        
        # Check if we're in backoff period
        if self.data['backoff_until']:
            backoff_until = datetime.fromisoformat(self.data['backoff_until'])
            if now < backoff_until:
                remaining = (backoff_until - now).total_seconds()
                return False, f"In backoff period for {remaining:.0f} more seconds"
        
        # Clean old requests
        self._clean_old_requests()
        
        # Check daily limit
        daily_requests = len(self.data['requests'])
        if daily_requests >= self.max_requests_per_day:
            return False, f"Daily limit reached ({daily_requests}/{self.max_requests_per_day})"
        
        # Check hourly limit
        one_hour_ago = now - timedelta(hours=1)
        hourly_requests = len([
            req_time for req_time in self.data['requests']
            if datetime.fromisoformat(req_time) > one_hour_ago
        ])
        if hourly_requests >= self.max_requests_per_hour:
            return False, f"Hourly limit reached ({hourly_requests}/{self.max_requests_per_hour})"
        
        # Check minimum delay
        if self.data['last_request_time']:
            last_request = datetime.fromisoformat(self.data['last_request_time'])
            time_since_last = (now - last_request).total_seconds()
            
            # Calculate delay based on consecutive failures
            required_delay = self.min_delay_seconds * (
                self.backoff_multiplier ** self.data['consecutive_failures']
            )
            
            if time_since_last < required_delay:
                remaining = required_delay - time_since_last
                return False, f"Must wait {remaining:.1f} more seconds (min delay)"
        
        return True, None
    
    def wait_if_needed(self) -> bool:
        """
        Wait if necessary before making a request
        
        Returns:
            True if can proceed, False if should skip
        """
        can_request, reason = self.can_make_request()
        
        if not can_request:
            if "backoff period" in reason or "Daily limit" in reason:
                logger.warning(f"Rate limiter: {reason}")
                return False
            elif "Must wait" in reason:
                # Extract wait time from reason
                wait_time = float(reason.split("wait ")[1].split(" more")[0])
                if wait_time > 60:  # Don't wait more than 1 minute
                    logger.warning(f"Rate limiter: Would need to wait {wait_time:.1f}s, skipping")
                    return False
                logger.info(f"Rate limiter: Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            elif "Hourly limit" in reason:
                logger.warning(f"Rate limiter: {reason}")
                # Wait until next hour
                next_hour = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                wait_seconds = (next_hour - datetime.now()).total_seconds()
                if wait_seconds > 300:  # Don't wait more than 5 minutes
                    logger.warning(f"Would need to wait {wait_seconds/60:.1f} minutes for hourly reset, skipping")
                    return False
                logger.info(f"Waiting {wait_seconds/60:.1f} minutes for hourly limit reset...")
                time.sleep(wait_seconds)
        
        return True
    
    def record_request(self, success: bool = True):
        """
        Record a request and its outcome
        
        Args:
            success: Whether the request was successful
        """
        now = datetime.now()
        
        # Record the request
        self.data['requests'].append(now.isoformat())
        self.data['last_request_time'] = now.isoformat()
        
        if success:
            # Reset failure count on success
            self.data['consecutive_failures'] = 0
            self.data['backoff_until'] = None
        else:
            # Increment failure count
            self.data['consecutive_failures'] += 1
            
            # Set backoff period for repeated failures
            if self.data['consecutive_failures'] >= 3:
                backoff_minutes = min(60, 5 * (2 ** (self.data['consecutive_failures'] - 3)))
                backoff_until = now + timedelta(minutes=backoff_minutes)
                self.data['backoff_until'] = backoff_until.isoformat()
                logger.warning(f"Rate limiter: Setting {backoff_minutes} minute backoff after {self.data['consecutive_failures']} failures")
        
        # Save cache
        self._save_cache()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limiter status"""
        self._clean_old_requests()
        
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        daily_requests = len(self.data['requests'])
        hourly_requests = len([
            req_time for req_time in self.data['requests']
            if datetime.fromisoformat(req_time) > one_hour_ago
        ])
        
        status = {
            'daily_requests': daily_requests,
            'daily_limit': self.max_requests_per_day,
            'daily_remaining': self.max_requests_per_day - daily_requests,
            'hourly_requests': hourly_requests,
            'hourly_limit': self.max_requests_per_hour,
            'hourly_remaining': self.max_requests_per_hour - hourly_requests,
            'consecutive_failures': self.data['consecutive_failures'],
            'in_backoff': bool(self.data['backoff_until'] and 
                             datetime.fromisoformat(self.data['backoff_until']) > now)
        }
        
        if status['in_backoff']:
            backoff_until = datetime.fromisoformat(self.data['backoff_until'])
            status['backoff_remaining_seconds'] = (backoff_until - now).total_seconds()
        
        return status
    
    def reset_failures(self):
        """Reset failure count and backoff (useful for testing)"""
        self.data['consecutive_failures'] = 0
        self.data['backoff_until'] = None
        self._save_cache()
        logger.info("Rate limiter: Reset failure count and backoff")