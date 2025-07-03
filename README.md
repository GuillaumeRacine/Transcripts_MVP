# YouTube Transcripts to Notion MVP

Automatically extract transcripts from YouTube playlist videos, summarize them using LLMs, and create Notion pages. The app checks for new videos every 24 hours.

## Features

- ✅ Fetch videos from YouTube playlists
- ✅ Extract transcripts automatically with smart rate limiting
- ✅ AI-powered summarization (OpenAI/Anthropic)
- ✅ Create Notion pages with summaries
- ✅ Track processed videos in database
- ✅ Scheduled 24-hour checks for new videos
- ✅ Support for both one-time runs and continuous scheduling
- ✅ Intelligent rate limiting to avoid API blocks
- ✅ Automatic retry with exponential backoff

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required configurations:
- `YOUTUBE_API_KEY`: Your YouTube Data API v3 key
- `NOTION_TOKEN`: Your Notion integration token
- `NOTION_PAGE_ID`: The Notion page ID where you want to add sub-pages
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: Your LLM provider API key
- `YOUTUBE_PLAYLIST_ID`: The playlist ID (already set to your playlist)

### 3. Setup APIs

#### YouTube API
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Copy the API key to your `.env` file

#### Notion API
1. Go to [Notion Developers](https://developers.notion.com)
2. Create a new integration
3. Copy the Internal Integration Token to your `.env` file
4. Share your Notion page with the integration
5. Copy the page ID from the URL to your `.env` file

#### LLM Provider (OpenAI or Anthropic)
- **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com)
- **Anthropic**: Get API key from [Anthropic Console](https://console.anthropic.com)

## Usage

### Run Once
Process all videos in the playlist once and exit:
```bash
python main.py --once
```

### Scheduled Mode (Default)
Run continuously, checking every 24 hours:
```bash
python main.py
# or
python main.py --schedule
```

### Rate Limiting Management
Check current rate limiter status:
```bash
python rate_limit_status.py
```

Reset rate limits (for testing):
```bash
python rate_limit_status.py --reset
```

Reset only failures and backoff:
```bash
python rate_limit_status.py --reset-failures
```

## Configuration Options

Edit `.env` file to customize:

- `CHECK_INTERVAL_HOURS`: Hours between playlist checks (default: 24)
- `LLM_PROVIDER`: Choose 'openai' or 'anthropic'
- `SUMMARY_INSTRUCTIONS`: Custom instructions for AI summarization
- `DATABASE_URL`: SQLite database location

## Project Structure

```
src/
├── youtube/          # YouTube playlist fetching
├── transcript/       # Transcript extraction
├── summarizer/       # LLM summarization
├── notion/          # Notion integration
├── scheduler/       # Task scheduling
├── database/        # Video tracking database
└── config.py        # Configuration management
```

## Troubleshooting

### Common Issues

1. **YouTube Transcript Rate Limiting**
   - **Issue**: "429 Too Many Requests" errors
   - **Solution**: App automatically handles this with smart rate limiting
   - **Manual check**: Run `python rate_limit_status.py` to see current status
   - **Reset if needed**: Use `python rate_limit_status.py --reset-failures`

2. **YouTube API Quota Exceeded**
   - YouTube Data API has 10,000 units/day default quota
   - Playlist fetching uses ~1 unit per request
   - Consider requesting quota increase for production use

3. **No Transcripts Available**
   - Some videos don't have transcripts enabled
   - App will skip these and log warnings
   - Check video settings on YouTube

4. **Notion Page Creation Fails**
   - Verify integration has access to the page
   - Check page ID is correct in `.env` file

5. **LLM API Errors**
   - Check API key validity
   - Monitor API usage limits
   - Verify sufficient credits/quota

### Debug Mode

Enable debug logging by modifying the logging level in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Database

The app uses SQLite to track processed videos and avoid duplicates. Database file: `transcripts.db`

View processed videos:
```python
from src.database.models import Database
db = Database("sqlite:///./transcripts.db")
videos = db.get_all_processed_videos()
```

## Logs

Application logs are saved to `transcripts_app.log` and displayed in console.

## License

MIT License