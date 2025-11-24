# TrendForge CI/CD Integration - Development Prompt for Codex

## Project Context

You are setting up the CI/CD pipeline for TrendForge, automating the entire workflow from trending collection to website deployment. This is Phase 3 of the MVP development.

**Goal**: Create a fully automated pipeline that runs daily without manual intervention.

## Automation Architecture

```
GitLab CI (Daily Schedule)
    ↓
Backend Pipeline (Python)
    ↓
Git Commit (Articles)
    ↓
Vercel Auto-Deploy (Frontend)
    ↓
Live Website Updates
```

## Implementation Requirements

### 1. GitLab CI Configuration

Create `.gitlab-ci.yml` in project root:

```yaml
# TrendForge Automated Pipeline
# Runs daily at 6:00 AM Beijing Time

stages:
  - setup
  - generate
  - deploy
  - notify

variables:
  PYTHON_VERSION: "3.10"
  TZ: "Asia/Shanghai"
  GIT_STRATEGY: clone
  GIT_DEPTH: 1

# Cache dependencies
cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - backend/venv/
    - frontend/node_modules/
    - .cache/pip

# Setup Python environment
setup:python:
  stage: setup
  image: python:${PYTHON_VERSION}
  script:
    - echo "Setting up Python environment..."
    - cd backend
    - python -m venv venv
    - source venv/bin/activate
    - pip install --upgrade pip
    - pip install -r requirements.txt
    # Install MetaGPT
    - pip install git+ssh://git@gitlab.deepwisdomai.com/pub/MetaGPT.git@dr4run
  artifacts:
    paths:
      - backend/venv/
    expire_in: 1 week
  only:
    - schedules
    - main

# Daily content generation
generate:content:
  stage: generate
  image: python:${PYTHON_VERSION}
  dependencies:
    - setup:python
  before_script:
    # Setup environment
    - cd backend
    - source venv/bin/activate
    # Configure API keys from CI variables
    - |
      cat > config/api_config.yaml << EOF
      openai:
        api_key: "${OPENAI_API_KEY}"
      newsapi:
        api_key: "${NEWS_API_KEY}"
      reddit:
        client_id: "${REDDIT_CLIENT_ID}"
        client_secret: "${REDDIT_CLIENT_SECRET}"
      EOF
    # Setup MetaGPT config
    - mkdir -p ~/.metagpt
    - echo "${METAGPT_CONFIG}" > ~/.metagpt/config2.yaml
  script:
    # Run the main pipeline
    - echo "Starting daily content generation at $(date)"
    - python pipeline.py full

    # Check if new content was generated
    - |
      if [ -n "$(git status --porcelain content/)" ]; then
        echo "New content generated successfully"
        ARTICLES_COUNT=$(ls -1 content/blog/*.md 2>/dev/null | wc -l)
        echo "Total articles: $ARTICLES_COUNT"
      else
        echo "No new content generated today"
        exit 0
      fi

    # Configure Git
    - git config user.email "trendforge-bot@example.com"
    - git config user.name "TrendForge Bot"

    # Commit new content
    - git add content/
    - git add data/
    - |
      COMMIT_MSG="feat: daily content generation - $(date +%Y-%m-%d)

      Generated $(ls -1 content/blog/*$(date +%Y-%m-%d)*.md 2>/dev/null | wc -l) new articles
      Total articles in library: $(ls -1 content/blog/*.md | wc -l)"
    - git commit -m "${COMMIT_MSG}"

    # Push to trigger Vercel deployment
    - git push https://oauth2:${GITLAB_TOKEN}@${CI_SERVER_HOST}/${CI_PROJECT_PATH}.git HEAD:main
  artifacts:
    paths:
      - content/blog/
      - data/processed/
    expire_in: 7 days
  only:
    - schedules
    - main

# Build frontend (optional - if not using Vercel)
build:frontend:
  stage: deploy
  image: node:18
  dependencies:
    - generate:content
  script:
    - cd frontend
    - npm ci
    - npm run build
    - echo "Frontend built successfully"
  artifacts:
    paths:
      - frontend/out/
    expire_in: 1 week
  only:
    - schedules
    - main
  when: manual  # Only run if Vercel is not configured

# Deploy to GitLab Pages (backup option)
pages:
  stage: deploy
  dependencies:
    - build:frontend
  script:
    - mkdir -p public
    - cp -r frontend/out/* public/
  artifacts:
    paths:
      - public
  only:
    - main
  when: manual

# Send notification
notify:success:
  stage: notify
  image: alpine:latest
  dependencies:
    - generate:content
  before_script:
    - apk add --no-cache curl
  script:
    # Count today's articles
    - ARTICLES_TODAY=$(ls -1 content/blog/*$(date +%Y-%m-%d)*.md 2>/dev/null | wc -l || echo "0")
    - ARTICLES_TOTAL=$(ls -1 content/blog/*.md 2>/dev/null | wc -l || echo "0")

    # Send notification (example: Webhook)
    - |
      if [ -n "${NOTIFICATION_WEBHOOK}" ]; then
        curl -X POST ${NOTIFICATION_WEBHOOK} \
          -H "Content-Type: application/json" \
          -d "{
            \"text\": \"TrendForge Daily Report\",
            \"articles_generated\": ${ARTICLES_TODAY},
            \"total_articles\": ${ARTICLES_TOTAL},
            \"date\": \"$(date +%Y-%m-%d)\",
            \"status\": \"success\"
          }"
      fi

    # Send email notification (using GitLab's email feature)
    - echo "Daily generation complete. Generated ${ARTICLES_TODAY} articles." > report.txt
    - echo "View at: https://trendforge.example.com" >> report.txt
  artifacts:
    reports:
      dotenv: report.txt
  only:
    - schedules
  when: on_success

# Error notification
notify:failure:
  stage: notify
  image: alpine:latest
  before_script:
    - apk add --no-cache curl
  script:
    - |
      if [ -n "${NOTIFICATION_WEBHOOK}" ]; then
        curl -X POST ${NOTIFICATION_WEBHOOK} \
          -H "Content-Type: application/json" \
          -d "{
            \"text\": \"⚠️ TrendForge Pipeline Failed\",
            \"date\": \"$(date +%Y-%m-%d)\",
            \"job\": \"${CI_JOB_NAME}\",
            \"status\": \"failed\"
          }"
      fi
  only:
    - schedules
  when: on_failure
```

### 2. GitHub Actions Alternative

If using GitHub instead of GitLab, create `.github/workflows/daily-pipeline.yml`:

```yaml
name: TrendForge Daily Pipeline

on:
  schedule:
    # Run at 6:00 AM Beijing Time (22:00 UTC)
    - cron: '0 22 * * *'
  workflow_dispatch:  # Allow manual trigger

env:
  PYTHON_VERSION: '3.10'
  NODE_VERSION: '18'

jobs:
  generate-content:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
      with:
        token: ${{ secrets.GITHUB_TOKEN }}

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Cache Python dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}

    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install git+ssh://git@gitlab.deepwisdomai.com/pub/MetaGPT.git@dr4run

    - name: Configure API keys
      run: |
        cd backend
        cat > config/api_config.yaml << EOF
        openai:
          api_key: "${{ secrets.OPENAI_API_KEY }}"
        newsapi:
          api_key: "${{ secrets.NEWS_API_KEY }}"
        reddit:
          client_id: "${{ secrets.REDDIT_CLIENT_ID }}"
          client_secret: "${{ secrets.REDDIT_CLIENT_SECRET }}"
        EOF

        mkdir -p ~/.metagpt
        echo "${{ secrets.METAGPT_CONFIG }}" > ~/.metagpt/config2.yaml

    - name: Run content generation
      run: |
        cd backend
        python pipeline.py full

    - name: Commit and push changes
      run: |
        git config --global user.name 'TrendForge Bot'
        git config --global user.email 'bot@trendforge.com'

        git add content/ data/

        if git diff --staged --quiet; then
          echo "No new content to commit"
        else
          ARTICLES_TODAY=$(ls -1 content/blog/*$(date +%Y-%m-%d)*.md 2>/dev/null | wc -l)
          git commit -m "feat: daily content - $(date +%Y-%m-%d) - ${ARTICLES_TODAY} articles"
          git push
        fi

    - name: Trigger Vercel deployment
      if: success()
      run: |
        # Vercel will auto-deploy on push to main
        echo "Vercel deployment triggered by git push"
```

### 3. Vercel Configuration

Create `vercel.json` in frontend directory:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "out",
  "framework": "nextjs",
  "installCommand": "npm install",

  "github": {
    "enabled": true,
    "autoAlias": true
  },

  "git": {
    "deploymentEnabled": {
      "main": true,
      "master": false
    }
  },

  "functions": {
    "app/api/revalidate.ts": {
      "maxDuration": 60
    }
  },

  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "SAMEORIGIN"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ],

  "redirects": [],

  "rewrites": [
    {
      "source": "/blog/:slug",
      "destination": "/blog/[slug]"
    }
  ]
}
```

### 4. Environment Variables Setup

#### GitLab CI Variables

Set in GitLab Project Settings > CI/CD > Variables:

```bash
# API Keys (Masked & Protected)
OPENAI_API_KEY=sk-...
NEWS_API_KEY=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...

# MetaGPT Config (File type variable)
METAGPT_CONFIG=(contents of config2.yaml)

# Git Token for pushing
GITLAB_TOKEN=glpat-...

# Notification Webhook (Optional)
NOTIFICATION_WEBHOOK=https://hooks.slack.com/...

# Vercel (if using Vercel CLI)
VERCEL_TOKEN=...
VERCEL_ORG_ID=...
VERCEL_PROJECT_ID=...
```

#### GitHub Secrets

Set in GitHub Repository Settings > Secrets:

```bash
OPENAI_API_KEY
NEWS_API_KEY
REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET
METAGPT_CONFIG
VERCEL_TOKEN
```

### 5. Local Development CI Script

Create `scripts/local-ci.sh` for testing CI locally:

```bash
#!/bin/bash

# Local CI testing script
set -e

echo "==================================="
echo "TrendForge Local CI Test"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check environment
echo -e "${YELLOW}Checking environment...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python $(python3 --version)${NC}"
else
    echo -e "${RED}✗ Python not found${NC}"
    exit 1
fi

# Check Node
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node $(node --version)${NC}"
else
    echo -e "${RED}✗ Node not found${NC}"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    echo -e "${GREEN}✓ Git $(git --version)${NC}"
else
    echo -e "${RED}✗ Git not found${NC}"
    exit 1
fi

# Run backend pipeline
echo ""
echo -e "${YELLOW}Running backend pipeline...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Test configuration
if [ ! -f "config/api_config.yaml" ]; then
    echo -e "${RED}✗ config/api_config.yaml not found${NC}"
    echo "Please create config/api_config.yaml from template"
    exit 1
fi

# Run pipeline in test mode
echo -e "${YELLOW}Running pipeline test...${NC}"
python pipeline.py test

# Check for generated content
if ls ../content/blog/*.md 1> /dev/null 2>&1; then
    echo -e "${GREEN}✓ Content generated successfully${NC}"
    ARTICLE_COUNT=$(ls -1 ../content/blog/*.md | wc -l)
    echo "  Found ${ARTICLE_COUNT} articles"
else
    echo -e "${YELLOW}⚠ No articles found${NC}"
fi

# Test frontend build
echo ""
echo -e "${YELLOW}Testing frontend build...${NC}"
cd ../frontend

if [ ! -d "node_modules" ]; then
    npm install
fi

npm run build

if [ -d "out" ]; then
    echo -e "${GREEN}✓ Frontend build successful${NC}"
else
    echo -e "${RED}✗ Frontend build failed${NC}"
    exit 1
fi

echo ""
echo "==================================="
echo -e "${GREEN}Local CI test completed!${NC}"
echo "==================================="
```

### 6. Schedule Configuration

#### GitLab Schedule

1. Go to Project > CI/CD > Schedules
2. Click "New Schedule"
3. Configure:
   - Description: "Daily Content Generation"
   - Interval Pattern: `0 6 * * *` (6:00 AM)
   - Timezone: Asia/Shanghai
   - Target Branch: main
   - Variables (optional):
     - `DAILY_LIMIT`: 10
     - `DEBUG`: false

#### Cron Job Alternative

If not using CI/CD, setup system cron:

```bash
# Edit crontab
crontab -e

# Add daily job (6:00 AM)
0 6 * * * cd /path/to/trendforge && /path/to/trendforge/scripts/run-pipeline.sh >> /var/log/trendforge.log 2>&1
```

Create `scripts/run-pipeline.sh`:

```bash
#!/bin/bash

# Production pipeline runner
cd /path/to/trendforge

# Load environment
source backend/venv/bin/activate
export $(cat .env | xargs)

# Run pipeline
python backend/pipeline.py full

# Check result
if [ $? -eq 0 ]; then
    echo "[$(date)] Pipeline completed successfully"

    # Optional: Send notification
    curl -X POST $WEBHOOK_URL \
      -d "text=TrendForge: Daily generation complete"
else
    echo "[$(date)] Pipeline failed"

    # Send error notification
    curl -X POST $WEBHOOK_URL \
      -d "text=⚠️ TrendForge: Pipeline failed"
fi
```

### 7. Monitoring & Alerts

#### Health Check Script

Create `scripts/health-check.py`:

```python
#!/usr/bin/env python3
"""
Health check for TrendForge pipeline
Runs every hour to ensure system is working
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import requests
import sys

def check_recent_content():
    """Check if content was generated today"""
    content_dir = Path('../content/blog')
    today = datetime.now().strftime('%Y-%m-%d')

    today_files = list(content_dir.glob(f'*{today}*.md'))

    if not today_files:
        return False, "No content generated today"

    return True, f"Found {len(today_files)} articles from today"

def check_website_status():
    """Check if website is accessible"""
    try:
        response = requests.get('https://trendforge.example.com', timeout=10)
        if response.status_code == 200:
            return True, "Website is up"
        else:
            return False, f"Website returned {response.status_code}"
    except Exception as e:
        return False, f"Website check failed: {e}"

def check_api_limits():
    """Check API usage limits"""
    # This would check actual API usage
    # For now, return mock data
    return True, "API limits OK"

def send_alert(message):
    """Send alert via webhook"""
    webhook_url = os.getenv('ALERT_WEBHOOK')
    if webhook_url:
        requests.post(webhook_url, json={"text": message})

def main():
    checks = [
        ("Recent Content", check_recent_content),
        ("Website Status", check_website_status),
        ("API Limits", check_api_limits),
    ]

    all_ok = True
    report = []

    for name, check_func in checks:
        status, message = check_func()
        report.append(f"{name}: {'✓' if status else '✗'} {message}")

        if not status:
            all_ok = False

    # Send alert if issues found
    if not all_ok:
        alert_message = "⚠️ TrendForge Health Check Failed\n" + "\n".join(report)
        send_alert(alert_message)
        print(alert_message)
        sys.exit(1)
    else:
        print("All health checks passed")
        print("\n".join(report))

if __name__ == "__main__":
    main()
```

### 8. Rollback Script

Create `scripts/rollback.sh` for emergency rollback:

```bash
#!/bin/bash

# Emergency rollback script
echo "==================================="
echo "TrendForge Emergency Rollback"
echo "==================================="

# Get the last known good commit
LAST_GOOD_COMMIT=$(git log --format="%H" -n 2 | tail -1)

echo "Rolling back to commit: $LAST_GOOD_COMMIT"

# Create backup branch
git branch backup-$(date +%Y%m%d-%H%M%S)

# Rollback
git reset --hard $LAST_GOOD_COMMIT

# Remove today's content
TODAY=$(date +%Y-%m-%d)
rm -f content/blog/*${TODAY}*.md

# Commit rollback
git add .
git commit -m "rollback: revert to previous state due to issues"
git push --force

echo "Rollback complete"
echo "Backup branch created"
```

## Setup Instructions

### 1. Initial Setup

```bash
# 1. Configure CI/CD variables in GitLab/GitHub
# 2. Connect Vercel to repository
# 3. Test locally first
./scripts/local-ci.sh

# 4. Enable CI/CD schedule
# GitLab: Project Settings > CI/CD > Schedules
# GitHub: Actions tab > Enable workflow
```

### 2. Vercel Setup

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Link project
cd frontend
vercel link

# Configure for production
vercel --prod
```

### 3. First Run Checklist

- [ ] All API keys configured in CI/CD variables
- [ ] MetaGPT config uploaded
- [ ] Git token has push permissions
- [ ] Vercel connected to repository
- [ ] Schedule configured (6:00 AM daily)
- [ ] Notification webhook setup (optional)
- [ ] Test run successful

## Troubleshooting

### Common Issues

1. **Pipeline fails at MetaGPT step**:
   - Check MetaGPT config is correctly formatted
   - Ensure SSH keys are configured for GitLab
   - Verify pip can access private GitLab repo

2. **Git push fails**:
   - Check GITLAB_TOKEN has write permissions
   - Ensure main branch is not protected
   - Verify git email/name are configured

3. **Vercel doesn't deploy**:
   - Check Vercel is connected to repository
   - Verify build command is correct
   - Check for build errors in Vercel dashboard

4. **No content generated**:
   - Check trending APIs are accessible
   - Verify filter rules aren't too strict
   - Check logs for API rate limits

## Success Metrics

- [ ] Pipeline runs daily at 6:00 AM automatically
- [ ] 5-10 articles generated per day
- [ ] Website updates within 5 minutes of generation
- [ ] No manual intervention required
- [ ] Error notifications sent on failure
- [ ] Success rate > 95% over 30 days

## Maintenance Tasks

### Weekly
- Review generated content quality
- Check API usage and costs
- Monitor error logs

### Monthly
- Update filter rules based on content performance
- Review and optimize CI/CD pipeline
- Clean up old artifacts
- Archive old content (> 90 days)