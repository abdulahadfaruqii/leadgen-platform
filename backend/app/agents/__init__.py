"""
Multi-Agent AI Lead Generation System.
"""
from app.agents.base import BaseAgent, AgentContext
from app.agents.location_research import LocationResearchAgent
from app.agents.google_maps import GoogleMapsAgent
from app.agents.website_research import WebsiteResearchAgent
from app.agents.social_media import SocialMediaDiscoveryAgent
from app.agents.contact_discovery import ContactDiscoveryAgent
from app.agents.lead_qualification import LeadQualificationAgent
from app.agents.service_recommendation import ServiceRecommendationAgent
from app.agents.outreach import PersonalisedOutreachAgent
from app.agents.crm import CRMAgent
from app.agents.analytics import AnalyticsAgent

__all__ = [
    "BaseAgent",
    "AgentContext",
    "LocationResearchAgent",
    "GoogleMapsAgent",
    "WebsiteResearchAgent",
    "SocialMediaDiscoveryAgent",
    "ContactDiscoveryAgent",
    "LeadQualificationAgent",
    "ServiceRecommendationAgent",
    "PersonalisedOutreachAgent",
    "CRMAgent",
    "AnalyticsAgent",
]
