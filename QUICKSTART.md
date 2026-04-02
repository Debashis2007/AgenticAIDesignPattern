# Quick Start Guide - 5 Minutes

Get up and running with Agentic AI Design Patterns in 5 minutes.

## 1. Prerequisites

- Python 3.8+
- pip (Python package manager)

## 2. Install Dependencies (1 min)

```bash
cd /path/to/AgenticAIDesignPatterns
pip install -r requirements.txt
```

## 3. Run Simple Example (2 min)

No API keys required!

```bash
python examples/simple_agent.py
```

Expected output:
```
============================================================
SIMPLE AGENT EXAMPLE: Alert Classification
============================================================

Alert ID: alert_001
  Original Severity: critical
  Classification: critical_incident
  Recommended Action: escalate_immediately
  Reasoning: Critical severity triggers immediate escalation
...
```

This demonstrates a **rule-based agent** that classifies alerts without needing an LLM.

## 4. Run Production Example (2 min)

```bash
python examples/incident_management.py
```

This showcases a **multi-agent system** with 4 agents:
1. Alert Normalization
2. Correlation
3. Analysis
4. Response Generation

Expected output:
```
======================================================================
INCIDENT MANAGEMENT WORKFLOW
======================================================================

STAGE 1: Normalizing Alerts
----------------------------------------------------------------------
  ✓ Normalized: alert_001 -> database
...
```

## 5. Next Steps

- **Read PATTERNS.md** - Deep dive into all 6 patterns
- **Explore src/agents/base.py** - Build your own agents
- **Add LLM Keys** - Copy .env.example to .env and add API keys
- **Integrate Tools** - Extend src/tools/base.py with your tools

## Useful Commands

```bash
# List all agents
grep "class.*Agent" src/agents/base.py

# View tool schema
python -c "from src.tools.base import ToolExecutor; print(ToolExecutor([]).get_tools_schema())"

# Check configuration
python -c "from src.config import settings; print(settings.dict())"
```

## Architecture Overview

```
User Input
    ↓
[Agent 1] → Process
    ↓
[Agent 2] → Enrich
    ↓
[Agent 3] → Analyze
    ↓
Output
```

## Common Customizations

### Add a New Tool

```python
from src.tools.base import Tool, ToolResult

class MyTool(Tool):
    name = "my_tool"
    description = "Does something useful"
    
    async def execute(self, **kwargs) -> ToolResult:
        # Your implementation
        return ToolResult(success=True, data={})
```

### Add a New Agent

```python
from src.agents.base import Agent, AgentState

class MyAgent(Agent):
    name = "my_agent"
    
    async def process(self, state: AgentState) -> AgentState:
        # Your logic
        return state
```

## Troubleshooting

**ImportError for openai/anthropic?**
- These are optional. Only needed if you use LLM clients
- Simple examples work without them

**Connection errors?**
- Check .env file for API keys
- Or use examples that don't require LLMs

**Python version issues?**
- Ensure Python 3.8+ with `python --version`

---

**Done!** You now understand the basics. Check out [PATTERNS.md](PATTERNS.md) for deep dives into each pattern.
