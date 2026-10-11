"""
Agent 6: Lead Qualification Agent
Scores and qualifies businesses as leads.
"""
import json
from typing import Dict, List

from app.agents.base import BaseAgent, AgentContext


class LeadQualificationAgent(BaseAgent):
    """Scores businesses and qualifies them as leads."""

    name = "LeadQualification"
    description = "Scores businesses based on multiple criteria and qualifies leads"

    # Scoring weights
    WEIGHTS = {
        "website_quality": 0.20,
        "digital_presence": 0.15,
        "technology": 0.15,
        "social_activity": 0.10,
        "reviews": 0.15,
        "growth_signals": 0.10,
        "opportunity": 0.15,
    }

    async def execute(self, context: AgentContext) -> AgentContext:
        self._log_start(context)

        qualified_leads = []

        for business in context.analyzed_businesses:
            try:
                lead = await self._qualify_business(business, context)
                if lead["overall_score"] >= 30:  # Minimum threshold
                    qualified_leads.append(lead)
            except Exception as e:
                self._log_error(context, e)

        # Sort by score descending
        qualified_leads.sort(key=lambda x: x["overall_score"], reverse=True)

        context.qualified_leads = qualified_leads
        context.metrics["leads_qualified"] = len(qualified_leads)

        self._log_complete(context, len(qualified_leads))
        return context

    async def _qualify_business(self, business: Dict, context: AgentContext) -> Dict:
        """Qualify a single business."""

        # Calculate individual scores
        website_score = self._score_website(business)
        digital_score = self._score_digital_presence(business)
        tech_score = self._score_technology(business)
        social_score = self._score_social(business)
        review_score = self._score_reviews(business)
        growth_score = self._score_growth(business)
        opportunity_score = self._score_opportunity(business)

        # Weighted overall score
        overall = (
            website_score * self.WEIGHTS["website_quality"] +
            digital_score * self.WEIGHTS["digital_presence"] +
            tech_score * self.WEIGHTS["technology"] +
            social_score * self.WEIGHTS["social_activity"] +
            review_score * self.WEIGHTS["reviews"] +
            growth_score * self.WEIGHTS["growth_signals"] +
            opportunity_score * self.WEIGHTS["opportunity"]
        )

        # Determine priority
        priority = "low"
        if overall >= 75:
            priority = "high"
        elif overall >= 50:
            priority = "medium"

        # Generate qualification reasons
        reasons = self._generate_reasons(business, {
            "website": website_score,
            "digital": digital_score,
            "technology": tech_score,
            "social": social_score,
            "reviews": review_score,
            "growth": growth_score,
            "opportunity": opportunity_score,
        })

        return {
            "business_id": business.get("id"),
            "business_data": business,
            "overall_score": round(overall, 1),
            "website_quality_score": round(website_score, 1),
            "digital_presence_score": round(digital_score, 1),
            "technology_score": round(tech_score, 1),
            "social_activity_score": round(social_score, 1),
            "review_score": round(review_score, 1),
            "growth_score": round(growth_score, 1),
            "opportunity_score": round(opportunity_score, 1),
            "qualification_reasons": reasons,
            "priority": priority,
            "campaign_id": context.campaign_id,
        }

    def _score_website(self, business: Dict) -> float:
        score = 50.0  # Base score

        if not business.get("website"):
            score -= 30  # No website is a major issue
        else:
            quality = business.get("website_quality_score")
            if quality is not None:
                score = quality

            if business.get("mobile_responsive") is False:
                score -= 15
            if business.get("page_speed_score", 100) < 50:
                score -= 10
            if business.get("seo_score", 100) < 50:
                score -= 10

        return max(0, min(100, score))

    def _score_digital_presence(self, business: Dict) -> float:
        score = 50.0

        social = business.get("social_profiles", {})
        if social:
            score += len(social) * 10

        if business.get("google_rating"):
            score += business["google_rating"] * 5

        if business.get("google_review_count", 0) > 50:
            score += 10

        return max(0, min(100, score))

    def _score_technology(self, business: Dict) -> float:
        score = 50.0
        techs = business.get("detected_technologies", [])

        # Modern tech stack is good, but missing key features is bad
        if any(t in techs for t in ["React", "Next.js", "Vue.js"]):
            score += 15
        elif any(t in techs for t in ["WordPress", "Wix", "Squarespace"]):
            score += 5

        # Missing features indicate opportunity
        missing = business.get("missing_features", [])
        if missing:
            score += min(len(missing) * 3, 20)  # Cap at 20

        return max(0, min(100, score))

    def _score_social(self, business: Dict) -> float:
        score = 50.0
        social = business.get("social_profiles", {})
        score += len(social) * 8
        return max(0, min(100, score))

    def _score_reviews(self, business: Dict) -> float:
        rating = business.get("google_rating", 0)
        count = business.get("google_review_count", 0)

        if count == 0:
            return 30.0  # Unknown

        score = rating * 15  # 5 stars = 75 base
        if count > 100:
            score += 15
        elif count > 20:
            score += 10

        return min(100, score)

    def _score_growth(self, business: Dict) -> float:
        score = 50.0
        if business.get("hiring_active"):
            score += 20
        signals = business.get("growth_signals", [])
        score += len(signals) * 5
        return min(100, score)

    def _score_opportunity(self, business: Dict) -> float:
        """Score based on how well our services match their needs."""
        score = 50.0

        missing = business.get("missing_features", [])
        issues = business.get("website_issues", [])

        # More issues = more opportunity
        score += len(missing) * 4
        score += len(issues) * 3

        # Specific high-value missing features
        high_value = ["booking system", "crm", "mobile app", "chatbot", "analytics"]
        for feature in high_value:
            if any(feature in m.lower() for m in missing):
                score += 8

        # No website = massive opportunity
        if not business.get("website"):
            score += 25

        return min(100, score)

    def _generate_reasons(self, business: Dict, scores: Dict[str, float]) -> List[str]:
        reasons = []

        if not business.get("website"):
            reasons.append("No website detected - high opportunity for web development")
        elif business.get("website_quality_score", 100) < 50:
            reasons.append("Poor website quality - redesign opportunity")

        if business.get("mobile_responsive") is False:
            reasons.append("Website not mobile responsive")

        if not business.get("has_booking_system"):
            reasons.append("No online booking system")

        if not business.get("has_crm"):
            reasons.append("No CRM system detected")

        if not business.get("has_chatbot"):
            reasons.append("No AI chatbot or live chat")

        if scores["opportunity"] > 70:
            reasons.append("High service fit - multiple improvement opportunities identified")

        if business.get("hiring_active"):
            reasons.append("Actively hiring - indicates growth and budget")

        if business.get("google_rating", 0) >= 4.5 and business.get("google_review_count", 0) > 50:
            reasons.append("Well-reviewed business with established reputation")

        return reasons
