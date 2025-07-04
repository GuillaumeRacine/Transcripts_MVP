# YouTube to Notion Transcript Processor

A streamlined Python application that automatically monitors your Notion database for YouTube videos and generates AI-powered summaries using Claude or GPT models.

## ✨ Features

### Core Functionality
- **Automatic Video Processing**: Monitors Notion database for new YouTube videos
- **AI-Powered Summaries**: Generates detailed 1,000-1,500 word summaries using Claude (Anthropic) or GPT (OpenAI)
- **Smart Caching**: Stores transcripts locally to avoid re-extraction
- **Continuous Monitoring**: Runs in the background, checking for new videos at configurable intervals
- **Error Handling**: Robust error handling with automatic retries and fallback options

### Advanced Features
- **Reprocessing Support**: Force reprocess videos with `--reprocess` flag
- **Custom Summary Instructions**: Configurable AI prompts via environment variables
- **Rate Limiting**: Built-in YouTube API rate limiting to respect quotas
- **Markdown Backup**: Automatic fallback to markdown files if Notion fails
- **Cloud Ready**: Easy deployment to Heroku, Railway, DigitalOcean, AWS, or any cloud platform

### Clean User Experience
- **Simplified Logging**: Clean, emoji-free output with progress indicators
- **Real-time Status**: Shows processing steps and word counts for generated summaries
- **Flexible Scheduling**: Support for minute-level intervals (e.g., every 30 minutes)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- YouTube API key or Service Account
- Notion API token and database
- OpenAI or Anthropic API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Transcripts_MVP
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Set up your Notion database**
   - Create a database in Notion with the required schema (see DATABASE_SETUP.md)
   - Add YouTube video URLs to the database

4. **Run the application**
   ```bash
   # Process videos once and exit
   python main_database.py --once
   
   # Run continuously (checks every hour by default)
   python main_database.py
   
   # Run continuously with custom interval (every 30 minutes)
   python main_database.py --interval 30
   
   # Force reprocess all videos
   python main_database.py --once --reprocess
   ```

## 📋 Configuration

### Required Environment Variables
```bash
# Notion Configuration
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_database_id

# YouTube API (choose one)
YOUTUBE_API_KEY=your_youtube_api_key
# OR
YOUTUBE_SERVICE_ACCOUNT_FILE=path/to/service-account.json

# AI Provider (choose one)
ANTHROPIC_API_KEY=your_anthropic_key
LLM_PROVIDER=anthropic
# OR
OPENAI_API_KEY=your_openai_key
LLM_PROVIDER=openai
```

### Optional Configuration
```bash
# Summary customization
SUMMARY_INSTRUCTIONS=Your custom instructions for AI summaries

# Scheduling
CHECK_INTERVAL_HOURS=24

# Notion organization
NOTION_SUMMARIES_PARENT_PAGE_ID=parent_page_for_summaries

# Database
DATABASE_URL=sqlite:///./transcripts.db
```

## 🏗️ Project Structure

```
Transcripts_MVP/
├── main_database.py              # Main application entry point
├── src/                          # Core application modules
│   ├── config.py                 # Configuration management
│   ├── youtube/                  # YouTube API integration
│   ├── transcript/               # Transcript extraction
│   ├── summarizer/               # AI summarization
│   ├── notion/                   # Notion API integration
│   ├── database/                 # Local database models
│   ├── scheduler/                # Task scheduling
│   ├── backup/                   # Markdown backup system
│   └── utils/                    # Utility functions
├── scripts/                      # Management utilities
│   ├── migrate_database.py       # Database migrations
│   ├── clear_database.py         # Database cleanup
│   └── debug_database.py         # Database debugging
├── tests/                        # Test files and demos
├── legacy/                       # Deprecated files
└── docs/                         # Documentation
    ├── DATABASE_SETUP.md         # Database setup guide
    ├── CLOUD_DEPLOYMENT.md       # Cloud deployment guide
    └── RATE_LIMITING_GUIDE.md    # API rate limiting info
```

## 📊 Usage Examples

### Basic Usage
```bash
# Check for new videos and process them once
python main_database.py --once

# Start continuous monitoring (default: every 24 hours)
python main_database.py
```

### Advanced Usage
```bash
# Monitor every 30 minutes
python main_database.py --interval 30

# Reprocess existing videos (useful for testing new summary prompts)
python main_database.py --once --reprocess

# One-time reprocessing with custom interval monitoring
python main_database.py --reprocess --interval 60
```

### Sample Output
```
YouTube to Notion Transcript Processor
----------------------------------------

Checking for new videos in Notion...

Found 3 videos to process

[1/3] Understanding & Conquering Depression | Huberman Lab Essenti
Processing: Understanding & Conquering Depression | Huberman L...
   Fetching video details...
   Extracting transcript...
   Generating AI summary...
   Generated 1247 word summary
   Creating Notion page...
   Summary page created!
Completed: Understanding & Conquering Depression | Huberman L

[2/3] How to Manage Your Emotions [SOLVED PODCAST]
Processing: How to Manage Your Emotions [SOLVED PODCAST]...
   Fetching video details...
   Using cached transcript
   Generating AI summary...
   Generated 1189 word summary
   Creating Notion page...
   Summary page created!
Completed: How to Manage Your Emotions [SOLVED PODCAST]

Summary: 2 processed, 0 errors, 0 skipped
```

## ☁️ Cloud Deployment

Deploy to the cloud for 24/7 automated processing:

### Heroku (Recommended for beginners)
```bash
# Install Heroku CLI, then:
heroku create your-app-name
heroku config:set NOTION_TOKEN="your-token"
heroku config:set NOTION_DATABASE_ID="your-id"
heroku config:set ANTHROPIC_API_KEY="your-key"
heroku config:set LLM_PROVIDER="anthropic"
git push heroku main
```

### Railway
```bash
railway login
railway init
# Set environment variables in dashboard
railway up
```

### Docker
```bash
docker build -t transcript-processor .
docker run -d --env-file .env transcript-processor
```

See [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) for detailed deployment instructions for all major cloud platforms.

## 🔧 Management

### Database Operations
```bash
# Migrate database schema
python scripts/migrate_database.py

# Clear all processed videos
python scripts/clear_database.py

# Debug database contents
python scripts/debug_database.py

# Check API rate limit status
python scripts/rate_limit_status.py
```

### Testing
```bash
# Run integration tests
python tests/test_integration.py

# Test single video processing
python tests/test_single_video.py

# Test Notion connectivity
python tests/test_notion_only.py
```

## 🤖 AI Summary Customization

The application generates detailed summaries based on your custom instructions. The default prompt creates summaries with:

1. **"So What" Section**: Why the content matters to you personally
2. **Important Ideas**: Key insights, surprising findings, and actionable takeaways
3. **Resources**: Books, papers, tools, and links mentioned in the video
4. **Source Link**: Direct link to the original video

Customize the summary format by setting the `SUMMARY_INSTRUCTIONS` environment variable.

## 📈 Monitoring & Maintenance

- **Logs**: Check `transcripts_app.log` for detailed processing logs
- **Database**: SQLite database stores processed videos and transcripts locally
- **Rate Limits**: Built-in YouTube API rate limiting (200 requests/day, 50/hour)
- **Error Handling**: Failed videos are marked with error status in Notion
- **Backup**: Automatic markdown backup if Notion API fails

## 🆘 Troubleshooting

### Common Issues

1. **Unicode Errors**: Fixed in latest version with proper encoding
2. **Rate Limits**: Adjust `--interval` to reduce API calls
3. **Missing Transcripts**: Some videos don't have auto-generated transcripts
4. **Notion Errors**: Check database schema and permissions

### Getting Help

1. Check the logs: `tail -f transcripts_app.log`
2. Verify configuration: `python tests/test_integration.py`
3. Test individual components: Files in `tests/` directory
4. Review documentation: `docs/` directory

## 📝 License

This project is open source. See LICENSE file for details.

## 🙏 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests for any improvements.

---

**Latest Update**: Refactored codebase with improved error handling, cleaner logging, and simplified architecture. Ready for production deployment.