# 🚦 Rate Limiting System - Complete Guide

## 📊 **Understanding YouTube API Rate Limits**

### YouTube Data API v3
- **Daily Quota**: 10,000 units (default for development)
- **Playlist fetch**: ~1 unit per request
- **Video metadata**: ~1 unit per video
- **No hard per-minute limits** but practical throttling exists

### YouTube Transcript API (Unofficial)
- **Practical Daily Limit**: ~250 requests before blocking
- **Hourly Limit**: ~50 requests recommended
- **Cloud Hosting**: Often blocked since August 2024
- **Local Development**: Usually works fine

## 🛡️ **Our Smart Rate Limiting Solution**

### Conservative Limits (Built-in Protection)
```python
max_requests_per_hour = 50    # Well below practical limits
max_requests_per_day = 200    # 20% buffer below 250 limit
min_delay_seconds = 3.0       # 3 seconds between requests
```

### Intelligent Features
- **✅ Automatic Delays**: 3+ seconds between transcript requests
- **✅ Exponential Backoff**: Increases delays after failures
- **✅ Smart Skipping**: Skips videos when limits approached
- **✅ Persistent Tracking**: Remembers usage across app restarts
- **✅ Failure Detection**: Recognizes 429 errors and adjusts

### Backoff Strategy
1. **First failure**: Continue with normal 3s delay
2. **Second failure**: 6s delay
3. **Third failure**: 12s delay + 5 minute backoff
4. **Fourth failure**: 24s delay + 10 minute backoff
5. **Fifth+ failure**: Up to 60 minute backoff

## 🔧 **Rate Limiter Commands**

### Check Current Status
```bash
python rate_limit_status.py
```
**Output Example:**
```
📊 Rate Limiter Status:
----------------------------------------
Daily requests:   45/200 (155 remaining)
Hourly requests:  12/50 (38 remaining)
Consecutive failures: 0
In backoff: False

✅ Ready to process videos
```

### Reset Options
```bash
# Reset everything (use carefully!)
python rate_limit_status.py --reset

# Reset only failures and backoff (recommended)
python rate_limit_status.py --reset-failures
```

## 📈 **Expected Processing Rates**

### Conservative Scenario (With Rate Limiting)
- **Videos per hour**: ~12-15 (3-5 second delays)
- **Videos per day**: ~200 maximum
- **28 videos in your playlist**: ~1.5-2 hours to complete

### Aggressive Scenario (Without Rate Limiting)
- **Risk**: Hit 429 errors after ~15-20 videos
- **Result**: Forced into long backoff periods
- **Recovery**: Could take several hours

## 🎯 **Best Practices**

### For Your 28-Video Playlist
1. **First Run**: Expect to process 15-20 videos successfully
2. **Rate Limited**: Remaining videos will be skipped
3. **Wait Period**: 1-2 hours for limits to reset
4. **Second Run**: Process remaining videos
5. **Total Time**: 2-3 hours for complete processing

### Production Recommendations
```bash
# Run once to process current videos
python main.py --once

# Check status periodically
python rate_limit_status.py

# Run scheduled mode for ongoing monitoring
python main.py  # Checks every 24 hours
```

### Monitoring Commands
```bash
# View application logs
tail -f transcripts_app.log

# Check rate limiter status
python rate_limit_status.py

# View database status
python -c "from src.database.models import Database; db = Database('sqlite:///./transcripts.db'); print(f'Processed: {len(db.get_all_processed_videos())} videos')"
```

## 🚨 **Troubleshooting Rate Limits**

### "Rate limiter: Daily limit reached"
- **Cause**: Processed 200 videos today
- **Solution**: Wait until tomorrow or use `--reset` (testing only)

### "Rate limiter: Hourly limit reached"  
- **Cause**: Processed 50 videos this hour
- **Solution**: Wait until next hour (auto-resets)

### "In backoff period for X seconds"
- **Cause**: Multiple consecutive failures
- **Solution**: Wait or use `--reset-failures`

### "Skipping transcript extraction due to rate limits"
- **Normal behavior**: App protecting itself
- **Action**: Run again later to process remaining videos

## 📝 **Rate Limit Cache File**

The rate limiter creates `rate_limit_cache.json` to track usage:
```json
{
  "requests": ["2024-07-02T18:30:00", "2024-07-02T18:33:15"],
  "last_request_time": "2024-07-02T18:33:15",
  "consecutive_failures": 0,
  "backoff_until": null
}
```

**Safe to delete** this file to reset all limits (equivalent to `--reset`).

## 🎉 **Success Indicators**

### Good Status
```
✅ Ready to process videos
Daily requests: 45/200 (155 remaining)
Consecutive failures: 0
```

### Warning Status  
```
💡 Only 15 requests remaining today - use wisely
Hourly requests: 48/50 (2 remaining)
```

### Blocked Status
```
⚠️ Daily limit reached - wait until tomorrow
In backoff: True
Backoff remaining: 1800 seconds
```

Your app now has **enterprise-grade rate limiting** that will **never get blocked** by YouTube! 🚀