#!/usr/bin/env python3
"""Check and manage rate limiter status"""

from src.utils.rate_limiter import RateLimiter
import argparse
import json

def show_status():
    """Show current rate limiter status"""
    rate_limiter = RateLimiter()
    status = rate_limiter.get_status()
    
    print("📊 Rate Limiter Status:")
    print("-" * 40)
    print(f"Daily requests:   {status['daily_requests']}/{status['daily_limit']} ({status['daily_remaining']} remaining)")
    print(f"Hourly requests:  {status['hourly_requests']}/{status['hourly_limit']} ({status['hourly_remaining']} remaining)")
    print(f"Consecutive failures: {status['consecutive_failures']}")
    print(f"In backoff: {status['in_backoff']}")
    
    if status['in_backoff']:
        print(f"Backoff remaining: {status['backoff_remaining_seconds']:.0f} seconds")
    
    # Show recommendation
    if status['daily_remaining'] <= 0:
        print("\n⚠️  Daily limit reached - wait until tomorrow")
    elif status['hourly_remaining'] <= 0:
        print("\n⚠️  Hourly limit reached - wait until next hour")
    elif status['in_backoff']:
        print(f"\n⏳ In backoff period - wait {status['backoff_remaining_seconds']:.0f} more seconds")
    elif status['daily_remaining'] < 10:
        print(f"\n💡 Only {status['daily_remaining']} requests remaining today - use wisely")
    else:
        print("\n✅ Ready to process videos")

def reset_limits():
    """Reset rate limiter (for testing)"""
    rate_limiter = RateLimiter()
    rate_limiter.reset_failures()
    
    # Clear request history (be careful with this!)
    rate_limiter.data['requests'] = []
    rate_limiter._save_cache()
    
    print("✅ Rate limiter reset - all limits cleared")

def main():
    parser = argparse.ArgumentParser(description='Rate Limiter Management')
    parser.add_argument('--reset', action='store_true', help='Reset rate limiter (clears all limits)')
    parser.add_argument('--reset-failures', action='store_true', help='Reset only failures and backoff')
    
    args = parser.parse_args()
    
    if args.reset:
        reset_limits()
    elif args.reset_failures:
        rate_limiter = RateLimiter()
        rate_limiter.reset_failures()
        print("✅ Reset failures and backoff period")
    else:
        show_status()

if __name__ == "__main__":
    main()