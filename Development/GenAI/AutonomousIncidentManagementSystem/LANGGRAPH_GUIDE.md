# LangGraph-Based Multi-Agent Orchestration

## What is LangGraph?

LangGraph is a graph-based framework for orchestrating multi-agent workflows as state machines. Instead of chaining agents with imperative code, you define agents as nodes and connections as edges.

## Architecture: 4-Agent Pipeline

```
Alert → Ingest → Correlate → Analyze → Respond
        ↓         ↓           ↓        ↓
    Normalize  Group Alerts   LLM    Notify
```

## State Schema

```python
class AlertState(TypedDict):
    raw_alert: dict
    normalized_alert: Optional[dict]
    alert_id: Optional[str]
    incident_id: Optional[str]
    root_cause: Optional[str]
    confidence: float
    recommendations: List[str]
    execution_log: List[str]
```

## Agent Implementation

### Alert Ingestion Agent

```python
class AlertIngestionAgent:
    async def __call__(self, state: AlertState) -> dict:
        alert = state["raw_alert"]
        normalized = {
            "id": f"alert_{hash(str(alert))}",
            "source": alert.get("source"),
            "severity": alert.get("severity", "medium"),
            "message": alert.get("message", ""),
        }
        return {
            "normalized_alert": normalized,
            "alert_id": normalized["id"],
            "execution_log": state.get("execution_log", []) + ["✓ Ingested"],
        }
```

### Correlation Agent

```python
class CorrelationAgent:
    async def __call__(self, state: AlertState) -> dict:
        alert = state["normalized_alert"]
        incident_id = f"incident_{hash(alert.get('message', ''))}" if alert else None
        return {
            "incident_id": incident_id,
            "execution_log": state.get("execution_log", []) + ["✓ Correlated"],
        }
```

### Analysis Agent (Ollama)

```python
class AnalysisAgent:
    def __init__(self):
        self.llm = ChatOllama(model="mistral", base_url="http://localhost:11434")
    
    async def __call__(self, state: AlertState) -> dict:
        alert = state["normalized_alert"]
        prompt = f"Analyze: {alert.get('message')}\nRespond in JSON"
        
        try:
            response = self.llm.invoke(prompt)
            result = json.loads(response.content)
        except:
            result = {"root_cause": "Error", "confidence": 0, "recommendations": []}
        
        return {
            "root_cause": result.get("root_cause"),
            "confidence": result.get("confidence", 0),
            "recommendations": result.get("recommendations", []),
        }
```

### Response Agent

```python
class ResponseAgent:
    async def __call__(self, state: AlertState) -> dict:
        logger.info(f"Incident: {state.get('incident_id')}")
        return {
            "execution_log": state.get("execution_log", []) + ["✓ Sent"],
        }
```

## Building the Graph

```python
class IncidentManagementWorkflow:
    def __init__(self):
        self.ingestion_agent = AlertIngestionAgent()
        self.correlation_agent = CorrelationAgent()
        self.analysis_agent = AnalysisAgent()
        self.response_agent = ResponseAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AlertState)
        
        workflow.add_node("ingest", self._ingest_node)
        workflow.add_node("correlate", self._correlate_node)
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("respond", self._respond_node)
        
        workflow.add_edge("ingest", "correlate")
        workflow.add_edge("correlate", "analyze")
        workflow.add_edge("analyze", "respond")
        workflow.add_edge("respond", END)
        workflow.set_entry_point("ingest")
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _ingest_node(self, state): return await self.ingestion_agent(state)
    async def _correlate_node(self, state): return await self.correlation_agent(state)
    async def _analyze_node(self, state): return await self.analysis_agent(state)
    async def _respond_node(self, state): return await self.response_agent(state)
    
    async def process_alert(self, raw_alert: dict):
        initial_state = AlertState(
            raw_alert=raw_alert,
            normalized_alert=None,
            alert_id=None,
            incident_id=None,
            root_cause=None,
            confidence=0.0,
            recommendations=[],
            execution_log=[],
        )
        return await self.graph.ainvoke(initial_state)
```

## Usage Example

```python
async def main():
    workflow = IncidentManagementWorkflow()
    
    alert = {
        "source": "prometheus",
        "severity": "high",
        "message": "CPU > 90% on prod-server",
    }
    
    result = await workflow.process_alert(alert)
    print(f"Root Cause: {result['root_cause']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Recommendations: {result['recommendations']}")

asyncio.run(main())
```

## Execution Timeline

```
T+0ms    → Alert arrives
T+50ms   → Normalized by Ingestion Agent  
T+100ms  → Correlated with existing alerts
T+300ms  → Analysis Agent triggered
T+500ms  → Ollama LLM called
T+1200ms → LLM response received
T+1300ms → Result formatted and sent
T+1400ms → Complete
```

## Comparison: LangGraph vs Raw Async

| Feature | Raw Async | LangGraph |
|---------|-----------|-----------|
| State Passing | Manual | Automatic |
| Fault Tolerance | None | Built-in |
| Adding Agents | Rewrite functions | Add 2 lines |
| Debugging | Complex | Visual graph |
| Extensibility | Hard | Easy |

## Installation

```bash
pip install -r requirements-langgraph.txt
```

## Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements-langgraph.txt .
RUN pip install -r requirements-langgraph.txt
COPY backend/ .
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

## Running Locally

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run workflow
pip install -r requirements-langgraph.txt
python backend/src/agents/langgraph_orchestrator.py
```

## Key Takeaways

1. LangGraph provides declarative agent orchestration
2. StateGraph automatically manages state passing
3. Built-in checkpointing enables fault tolerance
4. Linear pipeline solves most incident scenarios
5. Highly extensible - add conditional edges for complex routing
6. Production-ready with monitoring and logging

For full code: `backend/src/agents/langgraph_orchestrator.py`
