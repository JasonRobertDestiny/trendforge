# TrendForge MVP - Complete Development Guide

## Project Overview

TrendForge is an automated content generation system that transforms trending topics into deep research articles for internal operations teams.

**Core Workflow**:
```
自动抓取trending → 自动筛选 → MetaGPT DR生成深度文章 → Git保存 → 自动部署到网站
```

## Specification Documents

All specifications are saved in `.claude/specs/trendforge-mvp/`:

1. **[00-repo-scan.md](./00-repo-scan.md)** - Initial repository analysis
2. **[01-product-requirements.md](./01-product-requirements.md)** - Complete PRD (Score: 94/100)
3. **[codex-prompt-phase1-backend-updated.md](./codex-prompt-phase1-backend-updated.md)** - Backend pipeline development
4. **[codex-prompt-phase2-frontend.md](./codex-prompt-phase2-frontend.md)** - Frontend website development
5. **[codex-prompt-phase3-cicd.md](./codex-prompt-phase3-cicd.md)** - CI/CD automation setup

## Development Phases for Codex

### Phase 1: Backend Pipeline (Week 1-2)
**File**: [codex-prompt-phase1-backend-updated.md](./codex-prompt-phase1-backend-updated.md)

**Key Components**:
- Trending crawlers (HackerNews, Reddit, News API)
- Auto-filter system (engagement thresholds, keyword matching)
- MetaGPT DR integration (generates 1000-1500 word articles)
- Git storage and commit automation

**Success Criteria**:
- [ ] Fetches 30+ trending topics daily
- [ ] Auto-filters to 5-10 relevant topics
- [ ] DR generates quality articles
- [ ] Automatically commits to Git

### Phase 2: Frontend Website (Week 2-3)
**File**: [codex-prompt-phase2-frontend.md](./codex-prompt-phase2-frontend.md)

**Key Components**:
- Next.js 14 static site
- Article listing and detail pages
- Search and filter functionality
- Mobile responsive design

**Success Criteria**:
- [ ] Loads in < 2 seconds
- [ ] Mobile responsive
- [ ] Search works correctly
- [ ] Deploys to Vercel automatically

### Phase 3: CI/CD Automation (Week 3-4)
**File**: [codex-prompt-phase3-cicd.md](./codex-prompt-phase3-cicd.md)

**Key Components**:
- GitLab CI daily schedule (6:00 AM)
- Automated pipeline execution
- Git push triggers Vercel deployment
- Error monitoring and notifications

**Success Criteria**:
- [ ] Runs daily without intervention
- [ ] Handles errors gracefully
- [ ] Sends notifications on failure
- [ ] 95% uptime over 30 days

## Quick Start Guide

### For Backend Development (Codex)

```bash
# 1. Setup Python environment
cd /mnt/d/gitlab_deepwisdom/trendforge
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements.txt
pip install git+ssh://git@gitlab.deepwisdomai.com/pub/MetaGPT.git@dr4run

# 3. Configure APIs
cp backend/config/api_config.yaml.template backend/config/api_config.yaml
# Edit api_config.yaml with actual keys

# 4. Setup MetaGPT
cp your_config.yaml ~/.metagpt/config2.yaml

# 5. Test pipeline
python backend/pipeline.py test
```

### For Frontend Development (Codex)

```bash
# 1. Setup Node environment
cd frontend
npm install

# 2. Configure environment
cp .env.example .env.local

# 3. Start development
npm run dev

# 4. Build for production
npm run build
```

### For CI/CD Setup (Codex)

```bash
# 1. Configure GitLab CI variables
# Go to Settings > CI/CD > Variables
# Add: OPENAI_API_KEY, NEWS_API_KEY, etc.

# 2. Setup schedule
# Go to CI/CD > Schedules
# Create: "Daily Pipeline" at 6:00 AM

# 3. Connect Vercel
vercel link
vercel --prod

# 4. Test locally
./scripts/local-ci.sh
```

## Key Technical Decisions

### Why These Choices?

1. **MetaGPT DR for content generation**
   - Generates comprehensive 1000+ word articles
   - Built-in research and fact-checking
   - No need for additional GPT-4 calls (cost savings)

2. **Git/Markdown storage instead of database**
   - Zero infrastructure cost
   - Version control built-in
   - Works perfectly with static site generation

3. **Auto-filtering instead of manual curation**
   - Fully automated workflow
   - Configurable rules in YAML
   - Operations team only needs to read, not operate

4. **Next.js + Vercel deployment**
   - Free hosting for MVP scale
   - Auto-deploy on Git push
   - Excellent performance with SSG

5. **GitLab CI for automation**
   - Native integration with repository
   - Free CI minutes sufficient for daily runs
   - Easy secret management

## Configuration Files

### Backend Configuration

```yaml
# backend/config/filter_rules.yaml
engagement_thresholds:
  hackernews: 100      # Minimum upvotes
  reddit: 500          # Minimum karma
  newsapi: 5000        # Minimum shares

topic_keywords:
  tech: [AI, GPT, blockchain, cloud, database]
  news: [announces, releases, launches, funding]

daily_limit: 10        # Max articles per day
recency_hours: 24      # Only recent trending
```

### API Keys Required

```yaml
# backend/config/api_config.yaml
openai:
  api_key: "sk-..."    # Optional, not needed if only using DR

newsapi:
  api_key: "..."       # Required for news trending

reddit:                # Optional, works without auth
  client_id: ""
  client_secret: ""

# MetaGPT config at ~/.metagpt/config2.yaml
```

## Cost Analysis

### Monthly Costs

```
MetaGPT DR API calls: ~$150 (10 articles/day)
News API: $0 (free tier sufficient)
Vercel hosting: $0 (free tier)
GitLab CI: $0 (400 minutes free)

Total: ~$150/month
```

### ROI

```
Time saved: 2 hours/day × 30 days = 60 hours/month
Content output: 300 articles/month (vs ~50 manual)
Operational efficiency: 90% reduction in manual work
```

## Success Metrics

### Technical Metrics
- Pipeline success rate > 95%
- Page load time < 2 seconds
- Daily generation < 60 minutes
- Zero manual intervention required

### Business Metrics
- 5-10 quality articles daily
- < 10 minutes operations team time daily
- $150/month total cost
- 3x content output increase

## Troubleshooting Guide

### Common Issues

1. **MetaGPT DR timeout**
   - Increase timeout in pipeline.py
   - Reduce batch size to 2-3 articles

2. **No trending topics pass filter**
   - Lower engagement thresholds
   - Expand keyword list
   - Check API connectivity

3. **Git push fails**
   - Verify token permissions
   - Check branch protection rules
   - Ensure proper Git config

4. **Vercel build fails**
   - Check Node version compatibility
   - Verify all dependencies installed
   - Review build logs in Vercel dashboard

## Development Timeline

### Week 1: Backend Foundation
- Day 1-2: Setup environment, crawlers
- Day 3-4: Auto-filter, deduplication
- Day 5: MetaGPT DR integration

### Week 2: Backend Completion + Frontend Start
- Day 1-2: Pipeline testing, Git integration
- Day 3-5: Frontend article pages, search

### Week 3: Frontend Completion + CI/CD
- Day 1-2: Frontend polish, responsive design
- Day 3-4: GitLab CI setup
- Day 5: Vercel deployment

### Week 4: Testing & Launch
- Day 1-2: End-to-end testing
- Day 3: Operations team training
- Day 4-5: Production launch, monitoring

## Contact for Development

When using Codex for development:
1. Provide the relevant prompt file from this directory
2. Specify the working directory: `/mnt/d/gitlab_deepwisdom/trendforge`
3. Reference this summary for context

## Final Notes

This MVP is designed to be:
- **Simple**: No unnecessary complexity
- **Automated**: Runs without human intervention
- **Scalable**: Easy to add features later
- **Cost-effective**: ~$150/month total cost

The system follows Linus's principles:
1. Solves a real problem (content bottleneck)
2. Uses simplest approach (batch processing, static site)
3. Breaks nothing (new system, no legacy code)

---

*Generated by Claude Code for TrendForge MVP*
*Date: 2025-11-24*