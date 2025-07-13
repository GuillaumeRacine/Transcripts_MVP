# Troubleshooting Guide

## Common Issues and Solutions

### 🔴 API Rate Limiting / Overload Errors

**Symptoms:**
- "Retrying request" messages
- HTTP 529 errors
- "API overloaded" warnings

**Solutions:**
1. **Wait it out**: API overload is temporary (30-60 minutes)
2. **Increase delays**: Add to `.env`:
   ```bash
   API_CALL_DELAY=15.0          # Increase from 10s to 15s
   VIDEO_PROCESSING_DELAY=120   # Increase from 60s to 120s
   ```
3. **Process smaller batches**: Use `--max-videos 3`
4. **Off-peak processing**: Run during nights/weekends

### 🟡 Circuit Breaker Activated

**Symptoms:**
- "Circuit breaker OPEN" messages
- Processing stops after multiple failures

**Solutions:**
1. **Wait for reset**: Circuit breaker resets after 5 minutes
2. **Check API health**: Run with health check disabled: `--once --no-health`
3. **Manual reset**: Restart the application

### 🔵 Missing Transcripts

**Symptoms:**
- "No transcript available" errors
- Videos marked as "Error" in Notion

**Root Causes:**
- Video has no auto-generated captions
- Private/restricted videos
- Very new videos (transcripts not ready)

**Solutions:**
1. **Wait and retry**: New videos may need time for transcript generation
2. **Manual transcripts**: Some videos only have manual captions
3. **Skip and continue**: Use `--once` to process available videos

### 🟢 Large Playlist Issues

**Symptoms:**
- Timeouts during playlist processing
- Memory issues with 100+ videos

**Solutions:**
1. **Automatic batching**: App limits to 15 videos per run
2. **Manual batching**: Process playlists in chunks:
   ```bash
   python main_database.py --playlist "URL" --max-videos 20
   ```
3. **Scheduled processing**: Let the 15-minute scheduler handle large batches

### 🟣 Notion Database Issues

**Symptoms:**
- "Database schema validation failed"
- Missing properties in Notion

**Solutions:**
1. **Check database structure**: Ensure required columns exist:
   - Video URL (URL)
   - Status (Select: "Pending", "Processing", "Completed", "Error")
   - Title (Title)
   - Processed Date (Date)
2. **Recreate database**: Use the schema from README.md
3. **Check permissions**: Notion integration needs full access

### 🔶 Environment Configuration

**Symptoms:**
- "Configuration must be provided" errors
- Authentication failures

**Solutions:**
1. **Check `.env` file**:
   ```bash
   # Required variables
   NOTION_TOKEN=ntn_...
   NOTION_DATABASE_ID=...
   ANTHROPIC_API_KEY=sk-ant-...
   
   # YouTube (one of these)
   YOUTUBE_API_KEY=...
   # OR
   YOUTUBE_SERVICE_ACCOUNT_FILE=./youtube_service_account.json
   ```
2. **Verify API keys**: Test keys in their respective platforms
3. **Check file paths**: Ensure service account file exists

## 🛠️ Debugging Commands

### Check Application Logs
```bash
tail -f transcripts_app.log
```

### Verify Database Status
```bash
python scripts/debug_database.py
```

### Test API Health
```bash
python main_database.py --once  # Includes health check
```

### Process Single Video (Testing)
```bash
python main_database.py --once --max-videos 1
```

### Clear Failed Videos for Retry
```bash
python scripts/clear_database.py
```

## 📊 Performance Optimization

### For High-Volume Processing
1. **Increase delays during peak hours**:
   ```bash
   API_CALL_DELAY=20.0
   VIDEO_PROCESSING_DELAY=180
   ```

2. **Use scheduled processing**:
   ```bash
   # Process continuously with 30-minute intervals
   python main_database.py --interval 30
   ```

3. **Monitor resource usage**:
   - Memory: ~100MB per video
   - Disk: ~1KB per transcript
   - Network: ~2MB per video (API calls)

### For Reliability
1. **Ultra-conservative settings**:
   ```bash
   API_CALL_DELAY=15.0
   VIDEO_PROCESSING_DELAY=300     # 5 minutes between videos
   ERROR_BACKOFF_MULTIPLIER=60    # 1 minute per error
   ```

2. **Enable comprehensive logging**:
   ```bash
   # Add to main_database.py startup
   logging.getLogger().setLevel(logging.DEBUG)
   ```

## 🆘 When All Else Fails

### Reset Everything
1. **Clear local database**:
   ```bash
   rm transcripts.db
   python scripts/clear_database.py
   ```

2. **Reset Notion status**:
   - Manually change all "Processing" to "Pending"
   - Clear error messages

3. **Test with minimal setup**:
   ```bash
   python main_database.py --once --max-videos 1
   ```

### Contact Support Checklist
Before seeking help, gather:
- Last 50 lines of `transcripts_app.log`
- Your `.env` configuration (redacted)
- Specific error messages
- Number of videos being processed
- Time of day when errors occur

## 📈 Monitoring Health

### Key Metrics to Watch
- **Success rate**: Should be >95%
- **Processing time**: ~60-120s per video
- **API response time**: <3s for health checks
- **Memory usage**: <500MB total

### Warning Signs
- Multiple consecutive failures
- API response times >10s
- Processing times >300s per video
- Memory usage >1GB

### Recovery Actions
1. **Immediate**: Stop processing, wait 30 minutes
2. **Short-term**: Increase delays, reduce batch sizes
3. **Long-term**: Adjust schedule to off-peak hours