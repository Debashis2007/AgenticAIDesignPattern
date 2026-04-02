"""Agent base classes and implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
import json
import asyncio


@dataclass
class AgentState:
    """State passed between agents."""

    data: dict[str, Any]
    agent_name: str
    timestamp: str
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "data": self.data,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp,
            "errors": self.errors,
        }


class Agent(ABC):
    """Abstract base class for agents."""

    name: str

    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """Process state and return updated state."""
        pass


class SimpleClassifierAgent(Agent):
    """Simple rule-based classifier agent."""

    name = "simple_classifier"

    async def process(self, state: AgentState) -> AgentState:
        """Classify alerts based on simple rules."""
        try:
            alert = state.data.get("alert", {})
            severity = alert.get("severity", "unknown")

            # Simple classification rules
            if severity in ["critical", "emergency"]:
                classification = "escalate_immediately"
            elif severity == "high":
                classification = "escalate_soon"
            else:
                classification = "monitor"

            state.data["classification"] = classification
            state.data["classified"] = True

        except Exception as e:
            state.errors.append(f"Classification error: {str(e)}")

        return state


class AnalysisAgent(Agent):
    """Agent for analyzing data."""

    name = "analysis_agent"

    async def process(self, state: AgentState) -> AgentState:
        """Analyze state data."""
        try:
            data = state.data
            analysis = {
                "input_size": len(json.dumps(data)),
                "alert_count": len(data.get("alerts", [])),
                "has_errors": len(state.errors) > 0,
            }

            state.data["analysis"] = analysis

        except Exception as e:
            state.errors.append(f"Analysis error: {str(e)}")

        return state


class AgentPipeline:
    """Execute agents in sequence."""

    def __init__(self, agents: list[Agent]):
        self.agents = agents

    async def execute(self, initial_state: AgentState) -> AgentState:
        """Execute all agents in sequence."""
        state = initial_state
        for agent in self.agents:
            state = await agent.process(state)
        return state
