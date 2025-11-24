
# Product Requirements Document: TrendForge MVP

## Executive Summary

TrendForge is an automated content pipeline designed to streamline the production of tech and current affairs blog content for internal operations teams. The system automatically aggregates trending topics from multiple sources, enables manual curation by operations staff, generates high-quality 1000-word blog posts using MetaGPT's Deep Research (DR) capabilities, and publishes them to a static website.

**Quality Score: 94/100**

## Business Objectives

### Problem Statement
Internal operations teams face significant challenges in content production:
1. Time-intensive manual monitoring of trending topics across multiple platforms
2. Labor-intensive content creation process (2-3 hours per article)
3. Manual deployment creates publication delays
4. Cannot scale without proportional headcount growth

### Success Metrics
- **Content Velocity**: Generate 5+ high-quality articles per day
- **Time Savings**: Reduce per-article time from 2-3 hours to 15 minutes (90% reduction)
- **System Reliability**: 95% uptime for daily pipeline
- **Cost Efficiency**: Monthly costs under $200 (primarily API calls)
- **Editorial Quality**: 90%+ articles approved without major revision

### Expected ROI
- Operations team time savings: 10-15 hours per week
- Content output increase: 3x current production rate
- Infrastructure cost avoidance: ~$200/month vs traditional CMS

## User Personas

### Primary: Operations Content Curator (运营内容策划)
- **Goals**: Identify high-value trending topics, ensure quality standards, maximize output
- **Pain Points**: Information overload, time spent writing vs strategic planning
- **Technical Proficiency**: Medium (comfortable with web interfaces, basic Git)
- **Daily Workflow**:
  - Morning: Review trending (15 min)
  - Select topics for generation (10 min)
  - Review/approve drafts (30 min)

### Secondary: Technical Operations Lead
- **Goals**: Ensure reliability, monitor quality, scale efficiently
- **Technical Proficiency**: High (debugging, configuration, analysis)

## Core User Journey

1. **6:00 AM**: Automated trending aggregation from HackerNews, Reddit, News API
2. **9:00 AM**: Operations curator reviews ~30 deduplicated trending topics
3. **9:10 AM**: Curator selects 5-10 topics, triggers generation
4. **9:30 AM**: MetaGPT DR generates 1000-word articles
5. **10:00 AM**: Curator reviews drafts, approves for publication
6. **10:05 AM**: Approved articles auto-deploy to public website
7. **Result**: 5 high-quality articles published with 45 minutes total effort

## Technical Architecture

### System Components
```
Daily Cron → Trending Aggregation (Python)
     ↓
Git Storage (/data/trending/YYYY-MM-DD.json)
     ↓
Admin Interface (Next.js) → Manual Curation
     ↓
Content Generation (MetaGPT DR) → Markdown Articles
     ↓
Git Push → Vercel Auto-Deploy → Public Website
```

### Technology Stack
- **Backend**: Python 3.10+ (trending aggregation, DR integration)
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Storage**: Git repository + Markdown files (no database)
- **Deployment**: Vercel (free tier)
- **APIs**: HackerNews, Reddit, News API, MetaGPT DR

### Key Design Decisions
1. **Git-based storage** instead of database: Zero cost, version control built-in
2. **Manual curation** preserves editorial control while automating repetitive work
3. **Static site generation** for public website: Fast, secure, zero server costs
4. **Batch processing** instead of real-time: Simpler architecture, lower complexity

## Functional Requirements (5 Epics)

### Epic 1: Trending Topic Aggregation
- Multi-source collection (HackerNews, Reddit, News API)
- Intelligent deduplication (85% similarity threshold)
- Engagement-based ranking with recency boost

### Epic 2: Manual Curation Interface
- Web dashboard for topic review at `/admin/trending`
- Multi-select and batch generation trigger
- Historical archive with 90-day retention

### Epic 3: Automated Content Generation
- MetaGPT DR integration for deep research
- 1000-word article generation (3-5 minutes per article)
- Parallel processing queue (up to 3 concurrent)

### Epic 4: Draft Review & Publishing
- Side-by-side review interface at `/admin/drafts`
- Quick edit capability with Markdown editor
- One-click approval triggers auto-deployment

### Epic 5: Public Content Library
- Homepage with recent articles
- Full article pages with SEO optimization
- Search, filter, and RSS feed functionality

## Non-Functional Requirements

### Performance
- Trending aggregation: < 2 minutes
- Article generation: 3-5 minutes each
- Page load times: < 2 seconds
- Deployment: < 2 minutes

### Security
- Admin authentication (HTTP Basic Auth)
- API keys as environment variables
- HTTPS enforced
- Input sanitization for XSS prevention

### Reliability
- 95% uptime target
- Graceful degradation on API failures
- Git serves as automatic backup

## Project Scope & Timeline

### MVP (Weeks 1-4)
- Core pipeline: trending → curation → generation → publishing
- Basic admin interface
- Static public website
- Git-based storage
- Vercel deployment

### Phase 2 (Month 2)
- Rich text editor
- Advanced filtering
- Quality scoring
- Analytics dashboard

### Phase 3 (Months 3-4)
- ML-powered recommendations
- Multi-language support
- Webhook integrations
- Image generation

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| MetaGPT DR instability | Medium | High | Fallback to GPT-4, retry logic |
| API rate limits | Low | Medium | Caching, prioritize free APIs |
| Content quality issues | Medium | High | Manual review, prompt iteration |
| Git repo size growth | Medium | Low | Archive old content |

## Dependencies

### External
- MetaGPT DR module (Week 1 requirement)
- API keys (HackerNews free, Reddit free, News API)
- Vercel account (Week 2)

### Internal
- Operations team training (Week 4)
- Content guidelines document

## Success Criteria
- 5-10 articles generated daily
- < 10 minutes manual work per day
- > 90% DR generation success rate
- < $200/month total costs
- Operations team satisfaction: "saves time" and "easy to use"

---
*Version 1.0 | Date: 2025-11-24*