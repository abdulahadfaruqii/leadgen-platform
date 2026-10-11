"""
Agent 7: Service Recommendation Agent
Determines which services best fit each business.
"""
import json
from typing import Dict, List

from app.agents.base import BaseAgent, AgentContext


class ServiceRecommendationAgent(BaseAgent):
    """Recommends specific services based on business analysis."""

    name = "ServiceRecommendation"
    description = "Determines optimal service recommendations for each lead"

    AVAILABLE_SERVICES = {
        "website_redesign": {
            "name": "Website Redesign",
            "description": "Complete website overhaul with modern design",
            "indicators": ["old ui", "poor design", "outdated website", "slow loading"],
        },
        "react_website": {
            "name": "React.js Website",
            "description": "Modern interactive web application",
            "indicators": ["needs interactivity", "dynamic content", "spa needed"],
        },
        "nextjs_website": {
            "name": "Next.js Website",
            "description": "SEO-optimized React website with SSR",
            "indicators": ["seo issues", "poor performance", "needs ssr"],
        },
        "react_native_app": {
            "name": "React Native Mobile App",
            "description": "Cross-platform mobile application",
            "indicators": ["no mobile app", "needs mobile presence", "customer app"],
        },
        "backend_api": {
            "name": "Backend API Development",
            "description": "RESTful or GraphQL API development",
            "indicators": ["needs api", "backend migration", "system integration"],
        },
        "node_migration": {
            "name": "Node.js Migration",
            "description": "Migrate existing backend to Node.js",
            "indicators": ["legacy backend", "slow api", "scalability issues"],
        },
        "booking_system": {
            "name": "Online Booking System",
            "description": "Appointment and reservation platform",
            "indicators": ["no booking system", "phone only bookings", "scheduling"],
        },
        "customer_dashboard": {
            "name": "Customer Dashboard",
            "description": "Client portal with account management",
            "indicators": ["no customer portal", "client management", "self-service"],
        },
        "crm": {
            "name": "CRM System",
            "description": "Customer relationship management platform",
            "indicators": ["no crm", "spreadsheet tracking", "customer management"],
        },
        "admin_panel": {
            "name": "Admin Panel",
            "description": "Internal management dashboard",
            "indicators": ["manual processes", "admin tools", "internal dashboard"],
        },
        "payment_gateway": {
            "name": "Payment Gateway Integration",
            "description": "Online payment processing setup",
            "indicators": ["no online payments", "payment processing", "e-commerce"],
        },
        "analytics": {
            "name": "Analytics & Reporting",
            "description": "Business intelligence and analytics setup",
            "indicators": ["no analytics", "data insights", "reporting needs"],
        },
        "seo_optimization": {
            "name": "SEO Optimization",
            "description": "Search engine ranking improvements",
            "indicators": ["seo issues", "poor ranking", "search visibility"],
        },
        "performance": {
            "name": "Performance Optimization",
            "description": "Speed and performance improvements",
            "indicators": ["slow loading", "performance issues", "page speed"],
        },
        "ai_chatbot": {
            "name": "AI Chatbot",
            "description": "Intelligent customer service chatbot",
            "indicators": ["no chatbot", "customer support", "automation"],
        },
        "ai_automation": {
            "name": "AI Automation",
            "description": "Business process automation with AI",
            "indicators": ["manual processes", "workflow automation", "efficiency"],
        },
        "custom_software": {
            "name": "Custom Software Development",
            "description": "Bespoke software solution",
            "indicators": ["unique requirements", "custom solution", "specialized needs"],
        },
    }

    async def execute(self, context: AgentContext) -> AgentContext:
        self._log_start(context)

        for lead in context.qualified_leads:
            try:
                recommendations = await self._generate_recommendations(lead, context)
                lead["recommended_services"] = recommendations
            except Exception as e:
                self._log_error(context, e)
                lead["recommended_services"] = []

        context.metrics["recommendations_generated"] = sum(
            len(l.get("recommended_services", [])) for l in context.qualified_leads
        )

        self._log_complete(context, len(context.qualified_leads))
        return context

    async def _generate_recommendations(self, lead: Dict, context: AgentContext) -> List[Dict]:
        """Generate service recommendations for a lead."""
        business = lead["business_data"]
        recommendations = []

        # Rule-based recommendations
        for service_id, service in self.AVAILABLE_SERVICES.items():
            score = self._score_service_fit(service, business, lead)
            if score > 40:  # Minimum relevance threshold
                recommendations.append({
                    "service_id": service_id,
                    "service_name": service["name"],
                    "description": service["description"],
                    "fit_score": round(score, 1),
                    "reasons": self._get_service_reasons(service, business),
                    "estimated_impact": self._estimate_impact(service_id, business),
                })

        # Sort by fit score
        recommendations.sort(key=lambda x: x["fit_score"], reverse=True)

        # AI-enhanced top recommendations
        if recommendations:
            ai_enhanced = await self._ai_enhance_recommendations(business, recommendations[:5])
            for i, enhanced in enumerate(ai_enhanced):
                if i < len(recommendations):
                    recommendations[i]["ai_insight"] = enhanced.get("insight")
                    recommendations[i]["pitch_angle"] = enhanced.get("pitch_angle")

        return recommendations[:8]  # Cap at 8 recommendations

    def _score_service_fit(self, service: Dict, business: Dict, lead: Dict) -> float:
        """Score how well a service fits a business."""
        score = 30.0  # Base score

        missing = [m.lower() for m in business.get("missing_features", [])]
        issues = [i.lower() for i in business.get("website_issues", [])]
        indicators = [ind.lower() for ind in service["indicators"]]

        # Check against missing features
        for indicator in indicators:
            if any(indicator in m for m in missing):
                score += 15
            if any(indicator in issue for issue in issues):
                score += 10

        # Category-specific boosts
        category = business.get("_target_category", "").lower()
        if service["name"] == "Online Booking System" and category in ["dentists", "salons", "medical clinics"]:
            score += 20
        if service["name"] == "React Native Mobile App" and category in ["restaurants", "gyms", "hotels"]:
            score += 15

        # Lead score correlation
        if lead["overall_score"] > 70:
            score += 10

        return min(100, score)

    def _get_service_reasons(self, service: Dict, business: Dict) -> List[str]:
        reasons = []
        missing = business.get("missing_features", [])

        for indicator in service["indicators"]:
            if any(indicator.lower() in m.lower() for m in missing):
                reasons.append(f"Missing: {indicator}")

        if not reasons:
            reasons.append(f"Strategic fit for {business.get('_target_category', 'business')}")

        return reasons

    def _estimate_impact(self, service_id: str, business: Dict) -> str:
        impacts = {
            "website_redesign": "High - Improved conversions and brand perception",
            "react_website": "High - Better user engagement and performance",
            "nextjs_website": "High - SEO boost and faster load times",
            "react_native_app": "Very High - Direct customer engagement channel",
            "booking_system": "High - Reduced admin time, 24/7 bookings",
            "crm": "High - Better customer retention and sales tracking",
            "ai_chatbot": "Medium-High - 24/7 support, reduced costs",
        }
        return impacts.get(service_id, "Medium - Operational improvement")

    async def _ai_enhance_recommendations(self, business: Dict, recommendations: List[Dict]) -> List[Dict]:
        """Use AI to enhance top recommendations with insights."""
        system_prompt = """You are a senior sales consultant. For each service recommendation, provide a brief insight and pitch angle.
        Return JSON array of objects with 'insight' and 'pitch_angle' fields."""

        user_prompt = f"""Business: {business.get('name')} ({business.get('_target_category')})
        Website: {business.get('website', 'None')}
        Issues: {json.dumps(business.get('missing_features', []))}

        Recommendations:
        {json.dumps([{'service': r['service_name'], 'score': r['fit_score']} for r in recommendations])}

        Return insights for each recommendation."""

        try:
            response = await self._ai_chat(system_prompt, user_prompt, json_mode=True, temperature=0.7)
            return json.loads(response)
        except Exception:
            return []
