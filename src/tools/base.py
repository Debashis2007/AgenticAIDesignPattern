"""Tool abstraction and implementations for agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
import asyncio


@dataclass
class ToolResult:
    """Result from tool execution."""

    success: bool
    data: Any
    error: Optional[str] = None


class Tool(ABC):
    """Abstract base class for tools."""

    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        pass

    def get_schema(self) -> dict:
        """Return tool schema for LLM function calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": {}},
        }


class QueryDatabaseTool(Tool):
    """Tool for querying a database."""

    name = "query_database"
    description = "Execute a SQL query against the database"

    async def execute(self, query: str, **kwargs) -> ToolResult:
        """Execute database query."""
        try:
            # Simulated database query
            results = [
                {"id": 1, "name": "Alert 1", "severity": "high"},
                {"id": 2, "name": "Alert 2", "severity": "medium"},
            ]
            return ToolResult(success=True, data=results)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))


class SendNotificationTool(Tool):
    """Tool for sending notifications."""

    name = "send_notification"
    description = "Send a notification to users or systems"

    async def execute(self, channel: str, message: str, **kwargs) -> ToolResult:
        """Send notification."""
        try:
            # Simulated notification
            result = {"channel": channel, "message": message, "sent": True}
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))


class WebSearchTool(Tool):
    """Tool for searching the web."""

    name = "web_search"
    description = "Search the web for information"

    async def execute(self, query: str, **kwargs) -> ToolResult:
        """Search the web."""
        try:
            # Simulated web search
            results = [
                {"title": "Result 1", "url": "https://example.com/1"},
                {"title": "Result 2", "url": "https://example.com/2"},
            ]
            return ToolResult(success=True, data=results)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))


class GetSystemMetricsTool(Tool):
    """Tool for retrieving system metrics."""

    name = "get_system_metrics"
    description = "Get current system metrics like CPU and memory usage"

    async def execute(self, metric_type: str = "all", **kwargs) -> ToolResult:
        """Get system metrics."""
        try:
            # Simulated metrics
            metrics = {
                "cpu_percent": 45.2,
                "memory_percent": 62.1,
                "disk_percent": 78.5,
            }
            return ToolResult(success=True, data=metrics)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))


class ToolExecutor:
    """Executor for running tools."""

    def __init__(self, tools: list[Tool]):
        self.tools = {tool.name: tool for tool in tools}

    async def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        if tool_name not in self.tools:
            return ToolResult(
                success=False, data=None, error=f"Unknown tool: {tool_name}"
            )

        tool = self.tools[tool_name]
        return await tool.execute(**kwargs)

    def get_tools_schema(self) -> list[dict]:
        """Get schema for all tools."""
        return [tool.get_schema() for tool in self.tools.values()]
