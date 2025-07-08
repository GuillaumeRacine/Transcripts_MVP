# YouTube to Notion Transcript Processor

An automated Python application that monitors your Notion database for YouTube videos and generates comprehensive AI-powered summaries using Claude 3 Opus. Perfect for creating detailed knowledge bases from video content.

## ✨ Key Features

- **Comprehensive AI Summaries**: Generates 1,200-1,500 word detailed summaries using Claude 3 Opus
- **Multi-Part Analysis**: Strategic overview, detailed insights, and implementation guidance
- **24/7 Automation**: Runs scheduled jobs to process new videos continuously  
- **Smart Batching**: Cloud-optimized processing to prevent timeouts
- **Cost Tracking**: Shows estimated costs for each video processed (~$0.86-$1.19 per video)
- **Playlist Support**: Automatically detects and expands YouTube playlists
- **Robust Error Handling**: Exponential backoff and retry logic for API overloads

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- YouTube API service account or API key
- Notion API token and database
- Anthropic API key (Claude 3 Opus)

### Installation

1. **Clone and install**
   ```bash
   git clone <repository-url>
   cd Transcripts_MVP
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   # Required environment variables
   NOTION_TOKEN=your_notion_integration_token
   NOTION_DATABASE_ID=your_database_id
   ANTHROPIC_API_KEY=your_anthropic_api_key
   YOUTUBE_SERVICE_ACCOUNT_FILE=./youtube_service_account.json
   ```

3. **Run the application**
   ```bash
   # Process videos once
   python main_database.py --once
   
   # Run continuously (24 hour intervals)
   python main_database.py
   ```

## 🏗️ Architecture

```
Transcripts_MVP/
├── main_database.py              # Main application entry point
├── src/
│   ├── config.py                 # Simplified configuration
│   ├── youtube/                  # YouTube API integration
│   ├── transcript/               # Transcript extraction
│   ├── summarizer/
│   │   └── multi_part_summarizer.py  # Claude 3 Opus summarizer
│   ├── notion/                   # Notion database client
│   ├── database/                 # SQLite caching
│   ├── handlers/                 # Playlist processing
│   └── backup/                   # Markdown fallback
├── Dockerfile                    # Container configuration
└── scripts/                      # Utility scripts
```

## 📊 Sample Output

```
YouTube to Notion Transcript Processor
----------------------------------------

Checking for new videos in Notion...

Found 45 videos to process

⚠️  Large batch detected (45 videos)
Processing first 15 videos to prevent timeout...
Remaining videos will be processed in next scheduled run

[1/15] How An Extreme Surfer Turns Chaos into Calm
Processing: How An Extreme Surfer Turns Chaos into Calm...
   Fetching video details...
   Extracting transcript...
   Generating comprehensive AI summary...
Generating multi-part summary for: Why Overthinking Was Killing My Surfing...
   ✅ Strategic Overview generated successfully
   ✅ Detailed Analysis generated successfully  
   ✅ Implementation Guide generated successfully
   Generated 1,347 word comprehensive summary
   Estimated cost: $0.92
   Creating Notion page...
   Summary page created!
Completed: How An Extreme Surfer Turns Chaos into Calm

Summary: 15 processed, 0 errors, 0 skipped
```

## ☁️ Cloud Deployment (Google Cloud Run Jobs)

Deployed for 24/7 automated processing with the following configuration:

- **Platform**: Google Cloud Run Jobs
- **Schedule**: Daily at 2 AM UTC  
- **Timeout**: 60 minutes
- **Memory**: 1Gi
- **Batch Limit**: 15 videos per run (prevents timeouts)
- **Auto-retry**: Built-in exponential backoff for API overloads

### Deployment Commands
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/transcripts-464518/transcript-processor
gcloud run jobs create transcript-processor \
  --image gcr.io/transcripts-464518/transcript-processor \
  --region us-central1 \
  --max-retries 1 \
  --parallelism 1 \
  --task-timeout 3600 \
  --memory 1Gi \
  --cpu 1

# Set environment variables
gcloud run jobs update transcript-processor \
  --set-env-vars="NOTION_TOKEN=...,ANTHROPIC_API_KEY=...,NOTION_DATABASE_ID=..."

# Schedule daily runs
gcloud scheduler jobs create http transcript-processor-scheduler \
  --schedule="0 2 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/transcripts-464518/jobs/transcript-processor:run" \
  --http-method=POST
```

## 🤖 AI Summary Format

Each video generates a comprehensive 3-part summary:

### Part 1: Strategic Overview (400-500 words)
- Core thesis and key insights
- Why this content matters
- Strategic implications

### Part 2: Detailed Analysis (600-700 words) 
- Specific strategies and frameworks
- Data, examples, and case studies
- Tactical implementation details

### Part 3: Implementation Guide (300-400 words)
- Actionable next steps
- Resources and tools mentioned
- Practical application guidance

**Total**: ~1,200-1,500 words per video
**Cost**: ~$0.86-$1.19 per video (Claude 3 Opus)

## 🔧 Configuration

### Required Environment Variables
```bash
NOTION_TOKEN=ntn_...                    # Notion integration token
NOTION_DATABASE_ID=...                  # Target database ID
ANTHROPIC_API_KEY=sk-ant-...           # Claude 3 Opus API key
YOUTUBE_SERVICE_ACCOUNT_FILE=./youtube_service_account.json
```

### Optional Variables
```bash
NOTION_SUMMARIES_PARENT_PAGE_ID=...    # Parent page for summaries
CHECK_INTERVAL_HOURS=24                # Scheduling interval
DATABASE_URL=sqlite:///./transcripts.db
```

## 📈 Management

### Database Operations
```bash
python scripts/clear_database.py      # Clear processed videos
python scripts/debug_database.py      # View database contents  
python scripts/rate_limit_status.py   # Check API usage
```

### Testing
```bash
python tests/test_single_video.py     # Test single video
python tests/test_notion_only.py      # Test Notion connection
python tests/test_integration.py      # Full integration test
```

## 🔍 Monitoring

- **Logs**: `transcripts_app.log` contains detailed processing logs
- **Rate Limiting**: Built-in YouTube API quota management
- **Error Handling**: Failed videos marked in Notion with error details
- **Cost Tracking**: Real-time cost estimation per video
- **Backup**: Automatic markdown files if Notion fails

## 🆘 Troubleshooting

### Common Issues
1. **API Overloads**: Built-in retry logic with exponential backoff
2. **Large Batches**: Automatic batching limits to 15 videos per run
3. **Missing Transcripts**: Some videos lack auto-generated captions
4. **Rate Limits**: Smart request spacing and caching

### Getting Help
1. Check logs: `tail -f transcripts_app.log`
2. Verify setup: Run test scripts in `tests/`
3. Review documentation in `docs/`

---

**Status**: Production-ready with automated cloud deployment. Successfully processing 45+ videos with comprehensive Claude 3 Opus summaries.