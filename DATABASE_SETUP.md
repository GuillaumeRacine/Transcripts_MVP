# Database-Driven Workflow Setup

This guide will help you set up the new database-driven workflow where you can add individual YouTube video URLs to a Notion database and the app will automatically process them.

## 1. Create a Notion Database

1. Open Notion and create a new database
2. Add the following properties with these exact names and types:

| Property Name | Type | Description |
|---------------|------|-------------|
| **Title** | Title | Video title (auto-filled) |
| **Video URL** | URL | YouTube video URL you paste |
| **Video ID** | Text | Extracted video ID (auto-filled) |
| **Status** | Select | Processing status |
| **Channel** | Text | YouTube channel name (auto-filled) |
| **Duration** | Text | Video duration (auto-filled) |
| **Processed Date** | Date | When processing completed |
| **Summary Page** | Text | Link to generated summary |
| **Error** | Text | Error messages if any |

### Status Select Options
Create these options in the Status select property:
- `Processing` (yellow)
- `Completed` (green)
- `Error` (red)
- `Rate Limited` (orange)

## 2. Get Your Database ID

1. Open your database in Notion
2. Click "Share" in the top right
3. Copy the database URL
4. Extract the database ID from the URL:
   ```
   https://www.notion.so/your-workspace/DATABASE_ID?v=...
   ```
   The DATABASE_ID is the long string of characters (32 characters with dashes)

## 3. Configure Environment Variables

Add to your `.env` file:
```env
# Notion Configuration
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_database_id_here

# Other existing config...
YOUTUBE_SERVICE_ACCOUNT_FILE=./youtube_service_account.json
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
```

## 4. Test the Setup

Run the test script:
```bash
python test_database_workflow.py
```

This will:
- Verify your database schema
- Check for unprocessed videos
- Test URL parsing

## 5. Add Videos and Process

### Add Videos
1. Open your Notion database
2. Add a new row
3. Paste a YouTube URL in the "Video URL" column
4. Leave other fields blank (they'll be auto-filled)

### Process Videos
Run the processor:
```bash
# Process once
python main_database.py --once

# Run continuously (checks every hour)
python main_database.py
```

## 6. How It Works

1. **Add URL**: You paste a YouTube URL into the database
2. **Auto-Detection**: App detects new videos (Status is empty or not "Completed")
3. **Processing**: App updates Status to "Processing" and fills in video metadata
4. **Transcript**: Extracts transcript using YouTube API (with rate limiting)
5. **Summary**: Generates AI summary using your LLM provider
6. **Save**: Creates a summary page and updates Status to "Completed"
7. **Backup**: If Notion fails, creates markdown backup

## 7. Supported URL Formats

The app can extract video IDs from these formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `VIDEO_ID` (just the ID itself)

## 8. Troubleshooting

### Schema Validation Failed
Make sure all properties exist with exact names and correct types.

### No Videos Found
Check that:
- Videos have empty Status or Status ≠ "Completed"
- Video URLs are valid YouTube links

### Rate Limiting
The app will automatically handle YouTube rate limits and mark videos as "Rate Limited". Run again later to process them.

### Errors
Check the "Error" column in your database for specific error messages.

## 9. Advantages Over Playlist Workflow

- ✅ **Selective Processing**: Only process videos you choose
- ✅ **Mixed Sources**: Videos from different channels/playlists
- ✅ **Manual Control**: Add videos one by one as needed
- ✅ **Status Tracking**: See processing status for each video
- ✅ **Error Handling**: Clear error messages per video
- ✅ **Flexible**: Easy to reprocess failed videos