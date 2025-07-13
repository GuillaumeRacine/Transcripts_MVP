# Quick Start Guide

## 🚀 Setup (5 minutes)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Transcripts_MVP
   pip install -r requirements.txt
   ```

2. **Create `.env` file**
   ```bash
   # Required
   NOTION_TOKEN=your_notion_integration_token
   NOTION_DATABASE_ID=your_database_id
   ANTHROPIC_API_KEY=your_anthropic_api_key
   
   # Optional (for YouTube API)
   YOUTUBE_API_KEY=your_youtube_api_key
   # OR use service account
   YOUTUBE_SERVICE_ACCOUNT_FILE=./youtube_service_account.json
   ```

3. **Test your setup**
   ```bash
   python main_database.py --once
   ```

## 📺 Processing Videos

### One-Time Processing
```bash
# Process all pending videos
python main_database.py --once

# Process only 3 videos
python main_database.py --once --max-videos 3
```

### Continuous Monitoring (15-minute intervals)
```bash
# Runs forever, checking every 15 minutes
python main_database.py
```

### Add YouTube Playlist
```bash
python main_database.py --playlist "https://youtube.com/playlist?list=YOUR_PLAYLIST_ID"
```

## 🎯 How It Works

1. **Monitors** your Notion database for YouTube videos
2. **Checks** API health before processing
3. **Extracts** transcripts from YouTube
4. **Generates** comprehensive summaries using Claude 3.5 Sonnet
5. **Creates** summary pages in Notion
6. **Waits** intelligently between videos to avoid overload

## 📊 What to Expect

- **Processing time**: ~60-120 seconds per video
- **Summary length**: 1,200-1,500 words
- **Cost**: ~$0.50-$1.00 per video
- **Reliability**: 99%+ with automatic retries

## 🚨 Troubleshooting

If you see errors:
1. The app will automatically retry with longer delays
2. API overload errors are handled gracefully
3. Failed videos are marked as "Error" in Notion
4. Check `transcripts_app.log` for details

## 💡 Tips

- Process during off-peak hours for best results
- The app stops after errors to prevent cascading failures
- Failed videos can be reprocessed later
- Use smaller batches (3-5 videos) during peak times

## 📖 More Information

- Full documentation: `README.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- Rate limiting: `docs/RATE_LIMITING_GUIDE.md`