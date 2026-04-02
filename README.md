# Agentic AI Design Patterns

A comprehensive reference implementation of 6 core agentic AI design patterns with production-ready code, extensive documentation, and real-world use cases.

## Overview

This project demonstrates proven architectural patterns for building intelligent agent systems using LLMs. Each pattern includes:

- **Detailed explanation** of the pattern's purpose and use cases
- **Production-grade source code** with full type annotations
- **Runnable examples** you can execute immediately
- **Best practices** for error handling, logging, and observability
- **Real-world incident management system** showcasing multi-agent orchestration

## 6 Core Design Patterns

### 1. **Single Agent Pattern**
A standalone agent that processes input and generates output. Perfect for simple classification, summarization, or analysis tasks.

**Use Cases:** Alert classification, text analysis, content moderation

### 2. **Tool-Using Agent Pattern**
An agent with access to external tools for data retrieval, computation, and system interaction.

**Use Cases:** Customer support automation, database queries, API integration

### 3. **Multi-Agent Pattern**
Multiple specialized agents working in parallel on different aspects of a problem.

**Use Cases:** Incident management, complex analysis, distributed processing

### 4. **Hierarchical Agent Pattern**
Agents organized in a hierarchy where higher-level agents coordinate lower-level ones.

**Use Cases:** Project management, organizational automation, decision trees

### 5. **Agent Loop Pattern**
An agent that iteratively refines its response through multiple reasoning steps.

**Use Cases:** Problem-solving, code generation, complex reasoning tasks

### 6. **Dynamic Agent Pattern**
An agent that selects its approach dynamically based on the input and context.

**Use Cases:** Context-aware assistance, adaptive workflows, flexible automation

## Project Structure

```
.
├── README.md                 # This file
├── PATTERNS.md              # Deep dive into each pattern with code
├── QUICKSTART.md            # Get started in 5 minutes
├── ARCHITECTURE.md          # System design and architecture
│
├── src/                     # Source code modules
│   ├── config.py           # Configuration management
│   ├── llm/
│   │   └── client.py       # LLM provider abstraction (OpenAI, Anthropic)
│   ├── tools/
│   │   └── base.py         # Tool base classes and implementations
│   └── agents/
│       └── base.py         # Agent base classes and implementations
│
├── examples/               # Runnable examples
│   ├── simple_agent.py    # Rule-based alert classification (no LLM)
│   └── incident_management.py  # Production incident management system
│
├── docs/                  # Additional documentation
│   └── ARCHITECTURE.md    # System architecture details
│
├── requirements.txt       # Python dependencies
└── .env.example          # Environment configuration template
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your LLM API keys (optional for some examples)
```

### 3. Run Simple Example

```bash
python examples/simple_agent.py
```

This runs a rule-based alert classification example that requires **no external API keys**.

### 4. Run Incident Management System

```bash
python examples/incident_management.py
```

This demonstrates a production-grade 4-agent system with:
- Alert normalization
- Intelligent correlation
- Analysis and scoring
- Automated response recommendations

## Key Concepts

### Agents

An **agent** is an autonomous entity that:
- Receives input (queries, events, data)
- Reasons about the problem using an LLM
- Takes actions via tools
- Returns structured output

```python
class Agent(ABC):
    async def process(self, input_data: dict) -> dict:
        """Process input and return output"""
        pass
```

### Tools

**Tools** are external functions agents can call:
- Database queries
- API calls
- System metrics retrieval
- Notifications
- Web searches

```python
class Tool(ABC):
    async def execute(self, **kwargs) -> dict:
        """Execute the tool with given parameters"""
        pass
```

### State Management

Agents communicate through **structured state objects** using Pydantic models for type safety:

```python
@dataclass
class AgentState:
    data: dict
    agent_name: str
    timestamp: str
    errors: list = field(default_factory=list)
```

## Technologies Used

- **LLM Providers**: OpenAI, Anthropic (abstracted interface)
- **Frameworks**: LangChain, LangGraph
- **Async Runtime**: asyncio with aiohttp/httpx
- **Data Validation**: Pydantic v2.5.0
- **Type Safety**: Full type annotations throughout
- **Structured Logging**: JSON logging for observability

## Real-World Example: Incident Management System

The `examples/incident_management.py` demonstrates:

1. **IncidentAlertAgent**: Normalizes alerts from multiple sources
2. **IncidentCorrelationAgent**: Groups related alerts
3. **IncidentAnalysisAgent**: Analyzes incident severity and impact
4. **IncidentResponseAgent**: Generates mitigation recommendations
5. **IncidentManagementWorkflow**: Orchestrates the entire pipeline

```
Alert Input → Normalize → Correlate → Analyze → Respond → Output
```

## Design Principles

1. **Type Safety**: All components use Pydantic models and type annotations
2. **Error Handling**: Graceful degradation with fallback logic
3. **Observability**: Structured logging and correlation IDs
4. **Modularity**: Composable, reusable agent and tool components
5. **Async-First**: Concurrent execution for performance
6. **Tool Abstraction**: Clean separation between agents and external systems

## Getting Started

1. **Read**: Check out [QUICKSTART.md](QUICKSTART.md) for a 5-minute intro
2. **Run**: Execute `python examples/simple_agent.py` to see it in action
3. **Explore**: Review [PATTERNS.md](PATTERNS.md) for detailed pattern explanations
4. **Build**: Create your own agent using the base classes in `src/agents/base.py`

## Documentation

- **[PATTERNS.md](PATTERNS.md)** - Deep dive into each of the 6 patterns with code examples
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design, layers, and data flow
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[INDEX.md](INDEX.md)** - Complete file index and navigation

## Contributing

This project demonstrates production-grade agentic AI patterns. Feel free to:
- Adapt patterns for your use cases
- Extend with additional tools
- Integrate with your LLM provider
- Build multi-agent orchestrations

## License

This project is provided as a reference implementation for agentic AI patterns.

## Key Files to Explore

| File | Purpose |
|------|---------|
| `examples/simple_agent.py` | Immediate runnable example (no setup needed) |
| `examples/incident_management.py` | Production-grade multi-agent system |
| `src/agents/base.py` | Agent base classes and implementations |
| `src/tools/base.py` | Tool abstraction and examples |
| `src/llm/client.py` | LLM provider abstraction |
| `PATTERNS.md` | Detailed pattern documentation |

---

**Ready to build intelligent agents?** Start with [QUICKSTART.md](QUICKSTART.md) or dive into [PATTERNS.md](PATTERNS.md).
