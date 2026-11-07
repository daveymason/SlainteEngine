"""Base abstractions for the SlainteTech AI Security Labs 11-Agent Fleet."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AgentExecutionResult(BaseModel):
    agent_id: str
    status: str = Field(description="'pass', 'warning', 'fail', or 'success'")
    summary: str
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    telemetry: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))


class BaseAgent(ABC):
    """Abstract Base Class for all autonomous Governance and Clinical Agents."""
    id: str
    number: str
    code: str
    name: str
    fleet: str  # 'governance' or 'clinical'

    @abstractmethod
    def run(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> AgentExecutionResult:
        """Execute the agent's deterministic rules, verification sweep, or model synthesis."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify endpoints, tools, and prerequisites required by this agent."""
        pass
