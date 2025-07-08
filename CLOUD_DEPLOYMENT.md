# Cloud Deployment Guide

This guide covers deploying the YouTube Transcript Processor for 24/7 automated operation.

## ☁️ Google Cloud Run Jobs (Recommended)

### Overview
- **Cost**: ~$5-10/month for daily processing
- **Timeout**: 60 minutes per execution
- **Batch Size**: 15 videos per run (prevents timeouts)
- **Schedule**: Daily at 2 AM UTC
- **Auto-scaling**: Scales to zero when not running

### Prerequisites
- Google Cloud Project with billing enabled
- gcloud CLI installed and authenticated
- Docker/Cloud Build enabled

### Deployment Steps

1. **Set up Google Cloud project**
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
```

2. **Build and push Docker image**
```bash
# Build image using Cloud Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/transcript-processor

# Or build locally (if Docker available)
docker build -t gcr.io/YOUR_PROJECT_ID/transcript-processor .
docker push gcr.io/YOUR_PROJECT_ID/transcript-processor
```

3. **Create Cloud Run Job**
```bash
gcloud run jobs create transcript-processor \
  --image gcr.io/YOUR_PROJECT_ID/transcript-processor \
  --region us-central1 \
  --max-retries 1 \
  --parallelism 1 \
  --task-timeout 3600 \
  --memory 1Gi \
  --cpu 1
```

4. **Set environment variables**
```bash
gcloud run jobs update transcript-processor \
  --region us-central1 \
  --set-env-vars="NOTION_TOKEN=your_token,NOTION_DATABASE_ID=your_db_id,ANTHROPIC_API_KEY=your_key,YOUTUBE_SERVICE_ACCOUNT_FILE=/app/youtube_service_account.json"
```

5. **Create scheduler (optional)**
```bash
# Daily at 2 AM UTC
gcloud scheduler jobs create http transcript-processor-scheduler \
  --schedule="0 2 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/YOUR_PROJECT_ID/jobs/transcript-processor:run" \
  --http-method=POST \
  --oauth-service-account-email="YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com"
```

6. **Test execution**
```bash
# Manual execution
gcloud run jobs execute transcript-processor --region us-central1

# Check logs
gcloud logging read "resource.labels.job_name=transcript-processor" --limit=20
```

### Cost Estimation
- **Cloud Run Jobs**: ~$0.10 per hour of execution
- **Daily run (1 hour)**: ~$3/month
- **Storage**: ~$1/month for container images
- **Claude 3 Opus**: ~$0.86-$1.19 per video processed

## 🚀 Alternative: Heroku

### Simple Heroku Deployment
```bash
# Create app
heroku create your-transcript-processor

# Set environment variables
heroku config:set NOTION_TOKEN="your-token"
heroku config:set NOTION_DATABASE_ID="your-database-id"
heroku config:set ANTHROPIC_API_KEY="your-key"
heroku config:set YOUTUBE_SERVICE_ACCOUNT_FILE="./youtube_service_account.json"

# Deploy
git push heroku main

# Scale worker (paid plan required for continuous)
heroku ps:scale worker=1
```

**Cost**: ~$7/month for basic plan

## 🐳 Docker Deployment

### Build and run locally
```bash
# Build image
docker build -t transcript-processor .

# Run with environment file
docker run -d --env-file .env transcript-processor

# View logs
docker logs -f <container_id>
```

### Deploy to any cloud provider
- **AWS ECS/Fargate**: Container service
- **Azure Container Instances**: Serverless containers  
- **DigitalOcean App Platform**: Simple container deployment

## 📊 Monitoring & Management

### Cloud Run Jobs Monitoring
```bash
# List executions
gcloud run jobs executions list --job=transcript-processor

# Get execution details
gcloud run jobs executions describe EXECUTION_NAME

# View logs
gcloud logging read "resource.labels.job_name=transcript-processor"

# Update job configuration
gcloud run jobs update transcript-processor --memory=2Gi
```

### Health Checks
The application automatically:
- Validates configuration on startup
- Handles API rate limits with exponential backoff
- Limits batch size to prevent timeouts
- Creates markdown backups if Notion fails
- Logs detailed processing information

### Troubleshooting
1. **Check logs**: Review Cloud Run execution logs
2. **Verify environment**: Ensure all required environment variables are set
3. **Test locally**: Run `python main_database.py --once` locally first
4. **Resource limits**: Increase memory/timeout if needed
5. **API quotas**: Monitor YouTube and Anthropic API usage

## 🔄 Scheduling Options

### Cloud Scheduler (Google Cloud)
```bash
# Every 6 hours
--schedule="0 */6 * * *"

# Every day at 2 AM UTC  
--schedule="0 2 * * *"

# Every weekday at 9 AM
--schedule="0 9 * * 1-5"
```

### Cron Jobs (Linux/Unix)
```bash
# Edit crontab
crontab -e

# Add daily execution at 2 AM
0 2 * * * cd /path/to/project && python main_database.py --once
```

## ⚡ Performance Optimization

### Batch Processing
- **Cloud Run**: 15 videos per execution (optimized for 60-minute timeout)
- **Heroku**: 5-10 videos per batch (shorter dyno limits)
- **Local/VPS**: No limit (depends on available resources)

### Memory Usage
- **Minimum**: 1Gi (recommended)
- **Large batches**: 2Gi+ for processing many videos
- **Transcript caching**: Reduces memory usage for re-processing

### Cost Optimization
- Use **Cloud Run Jobs** for scheduled processing (pay per execution)
- Set appropriate batch sizes to prevent timeouts
- Monitor Claude 3 Opus costs (~$0.86 per video)
- Cache transcripts locally to avoid re-extraction

---

**Recommended Setup**: Google Cloud Run Jobs with daily scheduling provides the best balance of cost, reliability, and ease of management for automated video processing.