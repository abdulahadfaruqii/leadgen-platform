# LeadGen AI - Architecture Documentation

## System Overview
Enterprise-grade Multi-Agent AI Lead Generation Platform with 10 specialized agents,
multi-provider AI fallback, async web scraping, and distributed task processing.

## Architecture Diagram

```
User Input (Country/State/City/Category)
    |
    v
FastAPI Gateway --> JWT Auth --> Rate Limiting
    |
    v
Campaign Service --> PostgreSQL (Campaigns, Users)
    |
    v
Celery Worker Queue --> Redis Broker
    |
    v
Workflow Orchestrator (10 Agents Pipeline)
    |
    +---> Agent 1: LocationResearch (Query Generation)
    +---> Agent 2: GoogleMaps (Business Discovery)
    +---> Agent 3: WebsiteResearch (Site Analysis)
    +---> Agent 4: SocialMediaDiscovery (Profile Finding)
    +---> Agent 5: ContactDiscovery (Email/Phone Extraction)
    +---> Agent 6: LeadQualification (Scoring 0-100)
    +---> Agent 7: ServiceRecommendation (18 Services)
    +---> Agent 8: PersonalisedOutreach (Email/LinkedIn/Sequence)
    +---> Agent 9: CRM (PostgreSQL Persistence)
    +---> Agent 10: Analytics (MongoDB Events)
    |
    v
PostgreSQL (Businesses, Leads, Contacts, Outreach)
MongoDB (Analytics Events, Scraped Content)
ChromaDB (Vector Memory)
```

## Database Strategy
| Database | Purpose | Data |
|----------|---------|------|
| PostgreSQL | Primary OLTP | Users, Campaigns, Businesses, Leads, Contacts, Outreach, Jobs |
| MongoDB | Analytics OLAP | Events, Scraped content, Logs |
| Redis | Queue/Cache | Celery broker, Rate limiting, Session cache |
| ChromaDB | Vector Store | AI memory, Embeddings |

## Agent Pipeline
1. **LocationResearchAgent**: Generates 100+ search query variations using templates + AI
2. **GoogleMapsAgent**: Discovers businesses via Google Places API / SERP API
3. **WebsiteResearchAgent**: Analyzes home/about/services/contact pages with Playwright
4. **SocialMediaDiscoveryAgent**: Finds LinkedIn, Facebook, Instagram, X profiles
5. **ContactDiscoveryAgent**: Extracts emails, phones, contact forms from websites
6. **LeadQualificationAgent**: 7-dimension weighted scoring (0-100) with priority tiers
7. **ServiceRecommendationAgent**: Matches 18 services against business gaps
8. **PersonalisedOutreachAgent**: Generates cold email, LinkedIn message, 2 follow-ups
9. **CRMAgent**: Deduplicates and persists all data to PostgreSQL
10. **AnalyticsAgent**: Tracks workflow metrics in MongoDB

## AI Provider Fallback Chain
OpenAI GPT-4o -> Anthropic Claude 3.5 Sonnet -> Google Gemini 1.5 Pro

## Scalability
- API: 3+ replicas via K8s HPA
- Workers: 5+ Celery workers with separate queues per stage
- Database: Read replicas for analytics
- Scraping: Proxy rotation, rate limiting (2 RPS), retry with backoff
