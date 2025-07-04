# Cloud Deployment Guide for YouTube Transcript Processor

This guide covers deploying the YouTube Transcript Processor to various cloud platforms for continuous operation.

## Overview

Running the processor in the cloud allows it to continuously monitor your Notion database for new videos without requiring your local machine to be always on.

## Option 1: Heroku (Simplest)

### Prerequisites
- Heroku account (free tier works)
- Heroku CLI installed

### Steps

1. Create a `Procfile` in your project root:
```
worker: python main_database.py --interval 30
```

2. Create `runtime.txt` to specify Python version:
```
python-3.11.0
```

3. Deploy to Heroku:
```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-transcript-processor

# Set environment variables
heroku config:set YOUTUBE_API_KEY="your-key"
heroku config:set NOTION_TOKEN="your-token"
heroku config:set NOTION_DATABASE_ID="your-database-id"
heroku config:set ANTHROPIC_API_KEY="your-key"
heroku config:set LLM_PROVIDER="anthropic"

# Deploy
git push heroku main

# Scale the worker
heroku ps:scale worker=1

# View logs
heroku logs --tail
```

## Option 2: Railway (Modern Alternative)

### Steps

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Deploy:
```bash
# Login
railway login

# Initialize project
railway init

# Add environment variables via dashboard or CLI
railway variables set YOUTUBE_API_KEY="your-key"
railway variables set NOTION_TOKEN="your-token"
# ... add all other variables

# Deploy
railway up

# The app will automatically run based on Procfile
```

## Option 3: DigitalOcean Apps

### Steps

1. Create `app.yaml`:
```yaml
name: transcript-processor
services:
- name: worker
  github:
    branch: main
    repo: your-username/your-repo
  run_command: python main_database.py --interval 30
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: YOUTUBE_API_KEY
    value: "your-key"
    type: SECRET
  - key: NOTION_TOKEN
    value: "your-token"
    type: SECRET
  # Add other environment variables
```

2. Deploy via DigitalOcean dashboard or CLI

## Option 4: AWS EC2 (Free Tier)

### Steps

1. Launch EC2 instance (t2.micro for free tier)
2. SSH into instance and setup:

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and git
sudo apt-get install python3.11 python3-pip git -y

# Clone repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Install dependencies
pip3 install -r requirements.txt

# Create environment file
cat > .env << EOL
YOUTUBE_API_KEY=your-key
NOTION_TOKEN=your-token
NOTION_DATABASE_ID=your-database-id
ANTHROPIC_API_KEY=your-key
LLM_PROVIDER=anthropic
EOL

# Setup systemd service
sudo cat > /etc/systemd/system/transcript-processor.service << EOL
[Unit]
Description=YouTube Transcript Processor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/your-repo
ExecStart=/usr/bin/python3 /home/ubuntu/your-repo/main_database.py --interval 30
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Enable and start service
sudo systemctl enable transcript-processor
sudo systemctl start transcript-processor

# Check status
sudo systemctl status transcript-processor
```

## Option 5: Google Cloud Run Jobs (Serverless)

### Steps

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main_database.py", "--once"]
```

2. Deploy as Cloud Run Job:
```bash
# Build and push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/transcript-processor

# Create Cloud Run Job
gcloud run jobs create transcript-processor \
  --image gcr.io/YOUR_PROJECT_ID/transcript-processor \
  --set-env-vars YOUTUBE_API_KEY=your-key,NOTION_TOKEN=your-token \
  --schedule="*/30 * * * *"  # Run every 30 minutes
```

## Docker Deployment (Any Cloud)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run the application
CMD ["python", "main_database.py", "--interval", "30"]
```

Build and run:
```bash
# Build image
docker build -t transcript-processor .

# Run container
docker run -d \
  --name transcript-processor \
  --restart unless-stopped \
  -e YOUTUBE_API_KEY="your-key" \
  -e NOTION_TOKEN="your-token" \
  -e NOTION_DATABASE_ID="your-database-id" \
  -e ANTHROPIC_API_KEY="your-key" \
  -e LLM_PROVIDER="anthropic" \
  transcript-processor
```

## Environment Variables

All deployments require these environment variables:

```bash
# Required
YOUTUBE_API_KEY=your-youtube-api-key
NOTION_TOKEN=your-notion-token
NOTION_DATABASE_ID=your-database-id

# LLM Provider (choose one)
OPENAI_API_KEY=your-openai-key      # If using OpenAI
ANTHROPIC_API_KEY=your-anthropic-key # If using Anthropic
LLM_PROVIDER=anthropic               # or "openai"

# Optional
NOTION_SUMMARIES_PARENT_PAGE_ID=parent-page-id
CHECK_INTERVAL_HOURS=1               # Default check interval
YOUTUBE_SERVICE_ACCOUNT_FILE=path/to/service-account.json
```

## Monitoring

### View Logs

- **Heroku**: `heroku logs --tail`
- **Railway**: `railway logs`
- **DigitalOcean**: View in dashboard
- **AWS EC2**: `sudo journalctl -u transcript-processor -f`
- **Docker**: `docker logs -f transcript-processor`

### Health Checks

Consider adding a simple health check endpoint if you need monitoring:

```python
# Add to main_database.py
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK', 200

# Run Flask in a separate thread
def run_health_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if not args.once:
    health_thread = threading.Thread(target=run_health_server)
    health_thread.daemon = True
    health_thread.start()
```

## Cost Considerations

- **Heroku**: Free tier includes 550 dyno hours/month
- **Railway**: $5 credit/month on free tier
- **DigitalOcean**: $5/month for basic droplet
- **AWS EC2**: t2.micro free for 12 months
- **Google Cloud Run**: Pay per execution, very cost-effective

## Best Practices

1. **Use Environment Variables**: Never hardcode API keys
2. **Set Reasonable Intervals**: 30-60 minutes is usually sufficient
3. **Monitor Costs**: Keep an eye on API usage (YouTube, Notion, LLM)
4. **Enable Logging**: Use cloud logging services for debugging
5. **Set Up Alerts**: Configure alerts for errors or high usage

## Troubleshooting

### Common Issues

1. **Rate Limits**: Increase check interval if hitting limits
2. **Memory Issues**: Use larger instance sizes if needed
3. **Connection Timeouts**: Ensure proper network configuration
4. **Missing Dependencies**: Update requirements.txt regularly

### Debug Commands

```bash
# Test locally with production config
export $(cat .env | xargs) && python main_database.py --once

# Check environment variables
printenv | grep -E "(YOUTUBE|NOTION|ANTHROPIC|OPENAI)"

# Test database connection
python -c "from src.database.models import Database; db = Database('sqlite:///./transcripts.db'); print('DB OK')"
```

## Security Notes

1. Use secrets management services when available
2. Restrict API permissions to minimum required
3. Enable 2FA on all cloud accounts
4. Regularly rotate API keys
5. Use VPC/private networks where possible