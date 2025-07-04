# YouTube Playlist Processing Guide

The YouTube to Notion Transcript Processor now supports importing entire YouTube playlists directly into your Notion database for automated processing.

## ✨ Features

- **Bulk Import**: Add all videos from a YouTube playlist to your Notion database at once
- **Smart Deduplication**: Automatically skips videos that already exist in your database
- **Configurable Limits**: Optionally limit the number of videos to import
- **Progress Tracking**: Clear progress indicators and summary statistics
- **Seamless Integration**: Works with existing processing workflows

## 🚀 Quick Start

### Basic Usage

```bash
# Import all videos from a playlist
python main_database.py --playlist "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"

# Import only the first 10 videos
python main_database.py --playlist "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" --max-videos 10
```

### Complete Workflow

```bash
# Step 1: Import playlist videos to Notion database
python main_database.py --playlist "https://www.youtube.com/playlist?list=PLU9jW31vWD03JHBlzrMdVmqDW_sNn0JUL" --max-videos 5

# Step 2: Process the imported videos
python main_database.py --once

# Step 3: Set up continuous monitoring for new videos
python main_database.py --interval 60
```

## 📝 Command Reference

### Main Command
```bash
python main_database.py --playlist <URL> [OPTIONS]
```

### Options
- `--playlist <URL>`: YouTube playlist URL to process
- `--max-videos <NUMBER>`: Maximum number of videos to import (optional)

### Supported URL Formats
```bash
# Standard playlist URL
https://www.youtube.com/playlist?list=PLU9jW31vWD03JHBlzrMdVmqDW_sNn0JUL

# Short form
https://youtube.com/playlist?list=PLU9jW31vWD03JHBlzrMdVmqDW_sNn0JUL

# With additional parameters (will extract just the playlist ID)
https://www.youtube.com/watch?v=VIDEO_ID&list=PLU9jW31vWD03JHBlzrMdVmqDW_sNn0JUL&index=1
```

## 💡 Usage Examples

### Example 1: Educational Content
```bash
# Import educational videos from a course playlist
python main_database.py --playlist "https://www.youtube.com/playlist?list=PLU9jW31vWD03JHBlzrMdVmqDW_sNn0JUL"
```

### Example 2: Podcast Episodes
```bash
# Import latest 20 podcast episodes
python main_database.py --playlist "https://www.youtube.com/playlist?list=PODCAST_PLAYLIST_ID" --max-videos 20
```

### Example 3: Conference Talks
```bash
# Import conference talks for analysis
python main_database.py --playlist "https://www.youtube.com/playlist?list=CONFERENCE_PLAYLIST_ID" --max-videos 50
```

## 📊 Sample Output

```
YouTube to Notion Transcript Processor
----------------------------------------

Processing YouTube playlist...
Processing playlist: https://www.youtube.com/playlist?list=PLU9jW31vWD03JHBlzrMdVmqDW_sNn0JUL
Extracted playlist ID: PLU9jW31vWD03JHBlzrMdVmqDW_sNn0JUL
   Fetching playlist information...
   Playlist: Notion_Transcripts
   Channel: Guillaume Racine
   Total videos: 28
   Fetching videos from playlist...
   Limiting to first 5 videos
   Found 5 videos to process
   Adding videos to Notion database...
   Added: Nick Lane: Origin of Life, Evolution, Aliens, Biol...
   Added: Gregory Aldrete: The Roman Empire - Rise and Fall ...
   Added: Michio Kaku: Future of Humans, Aliens, Space Trave...
   Skipping: Andrew Huberman: Neuroscience of Optimal Perfor... (already exists)
   Added: Sean Carroll: The Nature of Reality, Time, and Con...
   Playlist processing complete!
   Added: 4, Skipped: 1, Total: 5

Playlist processing completed successfully!
Added 4 new videos to database
Skipped 1 existing videos
Total videos in playlist: 5

Playlist: Notion_Transcripts
Channel: Guillaume Racine

Next steps:
Run 'python main_database.py --once' to process the new videos
```

## 🛠️ How It Works

1. **URL Parsing**: Extracts the playlist ID from various YouTube URL formats
2. **Playlist Fetching**: Uses YouTube Data API to get playlist information and video list
3. **Deduplication**: Checks existing videos in Notion database to avoid duplicates
4. **Batch Import**: Creates new Notion database entries for each unique video
5. **Summary Report**: Provides detailed statistics on import results

## ⚙️ Configuration

### Database Schema Requirements
Your Notion database must have these properties:
- **Video URL** (URL type): For storing YouTube video links
- **Title** (Title type): For video titles
- **Status** (Select type): For tracking processing status

### Optional Properties
You can add these properties to your database for enhanced functionality:
- **Playlist** (Text type): To track which playlist videos came from
- **Channel** (Text type): To store channel information
- **Duration** (Text type): Video duration
- **Published Date** (Date type): Video publication date

## 🔍 Troubleshooting

### Common Issues

1. **"Could not extract playlist ID"**
   - Check that the URL is a valid YouTube playlist URL
   - Ensure the playlist is public or unlisted (not private)

2. **"No videos found in playlist"**
   - Verify the playlist exists and has videos
   - Check if you have access to view the playlist

3. **"Failed to add videos"**
   - Verify your Notion database schema matches requirements
   - Check Notion API permissions and integration setup

4. **Rate Limiting** ⚠️
   - The YouTube API has quotas (10,000 units/day by default)
   - Large playlists (15+ videos) are automatically limited to prevent rate limits
   - If you see "429 Too Many Requests", wait 10-15 minutes before continuing
   - Use automatic batching or wait between processing sessions for large playlists

### Debug Mode
Enable detailed logging to troubleshoot issues:
```bash
# Run with verbose output (check transcripts_app.log)
python main_database.py --playlist "YOUR_URL" --max-videos 5
tail -f transcripts_app.log
```

## 🎯 Best Practices

### 1. Automatic Playlist Detection ⭐ NEW
```bash
# Simply add the playlist URL to your Notion database
# The system automatically detects and expands playlists!
# No manual commands needed - just paste the URL in Notion
```

### 2. Handling Large Playlists (15+ videos)
```bash
# For playlists with 15+ videos, the system automatically limits to 15 videos
# to prevent YouTube rate limits. This is the recommended approach:

# Step 1: Add playlist URL to Notion (automatic detection)
# Step 2: Process the first batch
python main_database.py --once

# Step 3: Wait 10-15 minutes, then run again for more videos
python main_database.py --once

# Alternative: Use batch processing mode
python main_database.py --once --interval 30  # Process in 30-minute sessions
```

### 3. Manual Playlist Import (if needed)
```bash
# Import specific number of videos manually
python main_database.py --playlist "URL" --max-videos 10

# Process the imported videos
python main_database.py --once
```

### 4. Rate Limit Management
```bash
# The system includes intelligent rate limiting:
# - Automatic delays between videos in large batches
# - Progressive backoff when hitting limits
# - Smart batching for playlists over 15 videos

# If you hit rate limits, wait 10-15 minutes before continuing
```

## 📚 Integration with Existing Workflows

### Automated Processing Pipeline
```bash
#!/bin/bash
# Complete automation script

# 1. Import new videos from playlist
python main_database.py --playlist "$PLAYLIST_URL" --max-videos 20

# 2. Process all new videos
python main_database.py --once

# 3. Start continuous monitoring
python main_database.py --interval 120  # Check every 2 hours
```

### Scheduled Imports
```bash
# Add to crontab for daily playlist checks
0 9 * * * cd /path/to/app && python main_database.py --playlist "URL" --max-videos 5
```

## 🔗 Related Features

- **Reprocessing**: Use `--reprocess` to update summaries for imported videos
- **Continuous Monitoring**: Set up `--interval` for ongoing video discovery
- **Cloud Deployment**: Deploy to cloud for 24/7 playlist monitoring
- **Custom Summaries**: Configure `SUMMARY_INSTRUCTIONS` for domain-specific content

## 💰 Cost Considerations

- **YouTube API**: 1-3 units per video (10,000 units/day free)
- **Notion API**: No rate limits for personal use
- **AI Processing**: Varies by provider (Anthropic/OpenAI)

For large playlists (500+ videos), consider:
- Requesting increased YouTube API quota
- Processing in smaller batches
- Using cloud deployment for distributed processing