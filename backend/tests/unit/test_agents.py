"""
Unit tests for agent logic.
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.agents.base import AgentContext
from app.agents.location_research import LocationResearchAgent
from app.agents.lead_qualification import LeadQualificationAgent


@pytest.mark.asyncio
async def test_location_research_agent():
    agent = LocationResearchAgent()
    context = AgentContext(
        country="United States",
        state="Texas",
        city="Houston",
        categories=["Dentists"],
    )

    with patch.object(agent, "_ai_chat", new_callable=AsyncMock) as mock_ai:
        mock_ai.return_value = '["best dentists Houston", "top dental clinics Texas"]'
        result = await agent.execute(context)

    assert len(result.search_queries) > 0
    assert any("Dentists" in q for q in result.search_queries)
    assert any("Houston" in q for q in result.search_queries)


@pytest.mark.asyncio
async def test_lead_qualification_scoring():
    agent = LeadQualificationAgent()

    business = {
        "id": "test-1",
        "name": "Test Dental",
        "website": "https://test.com",
        "website_quality_score": 30.0,
        "mobile_responsive": False,
        "google_rating": 4.5,
        "google_review_count": 120,
        "missing_features": ["booking system", "crm", "chatbot"],
        "_target_category": "dentists",
    }

    score = agent._score_website(business)
    assert score < 50

    opp_score = agent._score_opportunity(business)
    assert opp_score > 60


@pytest.mark.asyncio
async def test_lead_qualification_overall():
    agent = LeadQualificationAgent()

    business = {
        "id": "test-1",
        "name": "Test Dental",
        "website": "https://test.com",
        "website_quality_score": 60.0,
        "mobile_responsive": True,
        "google_rating": 4.5,
        "google_review_count": 120,
        "missing_features": ["booking system"],
        "social_profiles": {"linkedin": "https://linkedin.com/company/test"},
        "hiring_active": True,
        "_target_category": "dentists",
        "_target_city": "Houston",
        "_target_state": "Texas",
    }

    lead_data = {
        "business_data": business,
        "overall_score": 0,
    }

    result = await agent._qualify_business(business, AgentContext())
    assert result["overall_score"] > 0
    assert result["priority"] in ["low", "medium", "high"]
    assert len(result["qualification_reasons"]) > 0
