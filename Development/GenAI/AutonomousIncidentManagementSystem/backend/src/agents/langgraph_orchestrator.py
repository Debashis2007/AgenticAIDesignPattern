"""
LangGraph-based Multi-Agent Orchestration for Incident Management
"""

from typing import TypedDict, Optional, List
from datetime import datetime
import logging
import json
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)


class AlertState(TypedDict):
    """Shared state between agents"""
    raw_alert: dict
    normalized_alert: Optional[dict]
    alert_id: Optional[str]
    similar_alerts: List[dict]
    incident_id: Optional[str]
    root_cause: Optional[str]
    confidence: float
    recommendations: List[str]
    execution_log: List[str]


class AlertIngestionAgent:
    """Normalize and deduplicate alerts"""
    
    async def __call__(self, state: AlertState) -> dict:
        alert = state["raw_alert"]
        normalized = {
            "id": f"alert_{hash(str(alert))}",
            "timestamp": alert.get("timestamp"),
            "source": alert.get("source"),
            "severity": alert.get("severity", "medium"),
            "message": alert.get("message", ""),
        }
        
        log_msg = f"✓ Ingested alert from {alert.get('source')}"
        return {
            "normalized_alert": normalized,
            "alert_id": normalized["id"],
            "execution_log": state.get("execution_log", []) + [log_msg],
        }


class CorrelationAgent:
    """Find similar alerts and create incidents"""
    
    async def __call__(self, state: AlertState) -> dict:
        alert = state["normalized_alert"]
        similar = [alert] if alert else []
        incident_id = f"incident_{hash(alert.get('message', ''))}" if alert else None
        
        log_msg = f"✓ Found {len(similar)} related alerts, incident: {incident_id}"
        return {
            "similar_alerts": similar,
            "incident_id": incident_id,
            "execution_log": state.get("execution_log", []) + [log_msg],
        }


class AnalysisAgent:
    """Analyze with Ollama LLM"""
    
    def __init__(self):
        self.llm = ChatOllama(model="mistral", base_url="http://localhost:11434")
    
    async def __call__(self, state: AlertState) -> dict:
        alert = state["normalized_alert"]
        if not alert:
            return {"root_cause": None, "confidence": 0.0, "recommendations": []}
        
        prompt = f"""Analyze this incident and provide root cause:
        
Alert: {alert.get('message')}
Severity: {alert.get('severity')}
Source: {alert.get('source')}

Respond in JSON: {{"root_cause": "...", "confidence": 0.8, "recommendations": ["..."]}}"""
        
        try:
            response = self.llm.invoke(prompt)
            result = json.loads(response.content)
            log_msg = "✓ Analysis complete"
        except Exception as e:
            result = {"root_cause": "Analysis error", "confidence": 0.0, "recommendations": []}
            log_msg = f"✗ Analysis failed: {str(e)}"
        
        return {
            "root_cause": result.get("root_cause"),
            "confidence": result.get("confidence", 0.0),
            "recommendations": result.get("recommendations", []),
            "execution_log": state.get("execution_log", []) + [log_msg],
        }


class ResponseAgent:
    """Send notifications and publish results"""
    
    async def __call__(self, state: AlertState) -> dict:
        log_msg = f"✓ Response sent: {state.get('incident_id')}"
        
        response_data = {
            "incident_id": state.get("incident_id"),
            "root_cause": state.get("root_cause"),
            "confidence": state.get("confidence"),
            "recommendations": state.get("recommendations"),
        }
        
        logger.info(f"Response: {json.dumps(response_data, indent=2)}")
        
        return {
            "execution_log": state.get("execution_log", []) + [log_msg],
        }


class IncidentManagementWorkflow:
    """LangGraph workflow orchestrator"""
    
    def __init__(self):
        self.ingestion_agent = AlertIngestionAgent()
        self.correlation_agent = CorrelationAgent()
        self.analysis_agent = AnalysisAgent()
        self.response_agent = ResponseAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AlertState)
        
        # Add nodes
        workflow.add_node("ingest", self._ingest_node)
        workflow.add_node("correlate", self._correlate_node)
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("respond", self._respond_node)
        
        # Add edges
        workflow.add_edge("ingest", "correlate")
        workflow.add_edge("correlate", "analyze")
        workflow.add_edge("analyze", "respond")
        workflow.add_edge("respond", END)
        
        # Set entry point
        workflow.set_entry_point("ingest")
        
        # Compile with memory checkpoint
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _ingest_node(self, state: AlertState):
        return await self.ingestion_agent(state)
    
    async def _correlate_node(self, state: AlertState):
        return await self.correlation_agent(state)
    
    async def _analyze_node(self, state: AlertState):
        return await self.analysis_agent(state)
    
    async def _respond_node(self, state: AlertState):
        return await self.response_agent(state)
    
    async def process_alert(self, raw_alert: dict):
        """Execute complete workflow"""
        initial_state = AlertState(
            raw_alert=raw_alert,
            normalized_alert=None,
            alert_id=None,
            similar_alerts=[],
            incident_id=None,
            root_cause=None,
            confidence=0.0,
            recommendations=[],
            execution_log=[],
        )
        
        result = await self.graph.ainvoke(initial_state)
        return result
    
    def visualize_workflow(self):
        """Print ASCII workflow diagram"""
        return """
        ┌─────────────────────────────────────────────────────┐
        │    LangGraph Incident Management Workflow            │
        └─────────────────────────────────────────────────────┘
        
        Alert Input
            │
            ▼
        ┌──────────────────────┐
        │  1. Ingest Agent     │ → Normalize & deduplicate
        └──────────────────────┘
            │
            ▼
        ┌──────────────────────┐
        │  2. Correlate Agent  │ → Find related alerts
        └──────────────────────┘
            │
            ▼
        ┌──────────────────────┐
        │  3. Analysis Agent   │ → Ollama LLM analysis
        └──────────────────────┘
            │
            ▼
        ┌──────────────────────┐
        │  4. Response Agent   │ → Send notifications
        └──────────────────────┘
            │
            ▼
        Response Output
        """


# Usage Example
if __name__ == "__main__":
    import asyncio
    
    async def main():
        workflow = IncidentManagementWorkflow()
        
        # Print workflow
        print(workflow.visualize_workflow())
        
        # Sample alert
        sample_alert = {
            "timestamp": "2024-01-15T10:30:00Z",
            "source": "prometheus",
            "severity": "high",
            "message": "CPU usage exceeded 90% on prod-server-01",
        }
        
        # Execute workflow
        print("Processing alert...")
        result = await workflow.process_alert(sample_alert)
        
        # Display results
        print("\n✓ Workflow Complete!")
        print(f"Incident ID: {result.get('incident_id')}")
        print(f"Root Cause: {result.get('root_cause')}")
        print(f"Confidence: {result.get('confidence'):.0%}")
        print(f"Recommendations: {result.get('recommendations')}")
        print("\nExecution Log:")
        for log in result.get("execution_log", []):
            print(f"  {log}")
    
    asyncio.run(main())
