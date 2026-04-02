# Architecture Guide

## System Overview

The Agentic AI Design Patterns system is built on a 5-layer architecture:

```
┌─────────────────────────────────────────────────────────┐
│  Application Layer                                      │
│  (User interfaces, APIs, workflows)                     │
├─────────────────────────────────────────────────────────┤
│  Orchestration Layer                                    │
│  (Multi-agent pipelines, state management)              │
├─────────────────────────────────────────────────────────┤
│  Agent Layer                                            │
│  (Individual agents, reasoning, decision-making)        │
├─────────────────────────────────────────────────────────┤
│  Tool Layer                                             │
│  (External functions, integrations, services)           │
├─────────────────────────────────────────────────────────┤
│  LLM Service Layer                                      │
│  (OpenAI, Anthropic, or other LLM providers)            │
└─────────────────────────────────────────────────────────┘
```

## Layer Details

### Application Layer
- Entry points for user interactions
- API endpoints, CLIs, web interfaces
- Request/response handling
- Example: FastAPI server running incident management

### Orchestration Layer
- Coordinates multiple agents
- Manages state flow between agents
- Handles error conditions and retries
- Example: IncidentManagementWorkflow

### Agent Layer
- Individual reasoning units
- Processes input state to output state
- Can use tools or call LLMs
- Example: IncidentAnalysisAgent

### Tool Layer
- Stateless, single-purpose functions
- Database queries, API calls, notifications
- Consistent error handling
- Example: QueryDatabaseTool, SendNotificationTool

### LLM Service Layer
- Abstract interface to LLM providers
- Handles authentication, rate limiting
- Supports tool calling/function definitions
- Example: OpenAIClient, AnthropicClient

## Data Flow

### Single Agent Processing

```
Input State
    ↓
[Agent]
  ├─ Receives state
  ├─ Optionally calls tools
  ├─ Optionally queries LLM
  └─ Updates state with results
    ↓
Output State
```

### Multi-Agent Pipeline

```
Input
  ↓
[Agent 1: Normalize]
  ├─ Data validation
  └─ Schema conversion
    ↓
[Agent 2: Correlate]
  ├─ Pattern matching
  └─ Grouping
    ↓
[Agent 3: Analyze]
  ├─ Tool calls
  └─ Enrichment
    ↓
[Agent 4: Respond]
  ├─ Decision making
  └─ Action planning
    ↓
Output
```

## State Management

### AgentState Structure

```python
@dataclass
class AgentState:
    data: dict[str, Any]           # Actual payload
    agent_name: str                # Who processed this
    timestamp: str                 # When
    errors: list[str]              # Error tracking
```

### State Mutations

Each agent should:
1. Read data from input state
2. Process and enrich
3. Add results to output state
4. Preserve previous data
5. Append any errors

```python
state.data["classification"] = "high_priority"
state.data["processed_at"] = datetime.now()
state.errors.append("Optional warning")
```

## Error Handling Strategy

### Graceful Degradation

```
Try: Use LLM for analysis
  ↓
Catch: Fallback to rule-based
  ↓
Catch: Use defaults
  ↓
Always: Return valid output
```

### Error Types

- **Validation Errors**: Bad input format
- **Tool Errors**: External service unavailable
- **LLM Errors**: API rate limit, authentication
- **Logic Errors**: Unexpected data state

### Recovery

```python
try:
    result = await agent.process(state)
except ToolError as e:
    state.errors.append(f"Tool failed: {e}")
    # Use fallback
    result = await fallback_logic(state)
```

## Concurrency Model

### Async/Await

All agent and tool methods are async:

```python
async def process(self, state: AgentState) -> AgentState:
    """Process state asynchronously."""
    pass
```

### Parallel Execution

Multiple agents can run in parallel:

```python
# Run agents concurrently
results = await asyncio.gather(
    agent1.process(state),
    agent2.process(state),
    agent3.process(state),
)
```

## Extensibility Points

### Adding New Agents

Extend `Agent` base class:

```python
class CustomAgent(Agent):
    name = "custom"
    
    async def process(self, state: AgentState) -> AgentState:
        # Your logic
        return state
```

### Adding New Tools

Extend `Tool` base class:

```python
class CustomTool(Tool):
    name = "custom_tool"
    description = "Does something"
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, data={})
```

### Adding New LLM Providers

Extend `LLMClient` base class:

```python
class CustomLLMClient(LLMClient):
    async def complete(self, prompt: str, **kwargs) -> str:
        # Your provider integration
        pass
    
    async def chat_with_tools(self, messages, tools, **kwargs) -> dict:
        # Your provider integration
        pass
```

## Performance Considerations

### Optimization Strategies

1. **Async Everywhere**: Use async/await for I/O operations
2. **Connection Pooling**: Reuse HTTP connections
3. **Caching**: Cache LLM responses when possible
4. **Batching**: Process multiple items together
5. **Timeouts**: Set timeouts on tool calls

### Scalability

- Agents are stateless (except input/output)
- Can run distributed across machines
- State can be stored in databases
- Tools can be microservices

## Monitoring & Observability

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Agent {self.name} processed state")
```

### Metrics to Track

- Agent execution time
- Tool call count and latency
- Error rates by agent/tool
- Throughput (states/second)

### Correlation IDs

Track a state through the pipeline:

```python
state.correlation_id = str(uuid.uuid4())
# Use in logs for tracing
```

---

For pattern implementations, see [PATTERNS.md](PATTERNS.md).
