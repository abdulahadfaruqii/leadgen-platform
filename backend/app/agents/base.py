"""
Base agent class with common functionality.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.tools.ai_provider import get_ai_provider

logger = get_logger(__name__)


@dataclass
class AgentContext:
    """Shared context passed between agents in a workflow."""
    campaign_id: Optional[str] = None
    user_id: Optional[str] = None
    job_id: Optional[str] = None

    # Input parameters
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)

    # Accumulated data
    search_queries: List[str] = field(default_factory=list)
    businesses: List[Dict[str, Any]] = field(default_factory=list)
    analyzed_businesses: List[Dict[str, Any]] = field(default_factory=list)
    qualified_leads: List[Dict[str, Any]] = field(default_factory=list)
    outreach_messages: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    checkpoint: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agents."""

    name: str = "BaseAgent"
    description: str = "Base agent"

    def __init__(self):
        self.ai = get_ai_provider()
        self.logger = get_logger(f"agent.{self.name}")

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentContext:
        """Execute the agent's main logic."""
        pass

    async def _ai_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = False,
        temperature: float = 0.7,
    ) -> str:
        """Helper for AI chat completion."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await self.ai.chat_completion(
            messages=messages,
            json_mode=json_mode,
            temperature=temperature,
        )

    def _log_start(self, context: AgentContext):
        self.logger.info(
            f"Agent {self.name} started",
            campaign_id=context.campaign_id,
            job_id=context.job_id,
        )

    def _log_complete(self, context: AgentContext, result_count: int = 0):
        self.logger.info(
            f"Agent {self.name} completed",
            campaign_id=context.campaign_id,
            job_id=context.job_id,
            result_count=result_count,
        )

    def _log_error(self, context: AgentContext, error: Exception):
        self.logger.error(
            f"Agent {self.name} error",
            campaign_id=context.campaign_id,
            job_id=context.job_id,
            error=str(error),
        )
        context.errors.append(f"{self.name}: {str(error)}")
