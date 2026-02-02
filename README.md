# Kagent Multi-Agent Setup with A2A and MCP

Complete kagent setup for the `kind-kagent-demo` cluster featuring:
- 🤖 Multiple specialized AI agents using Gemini
- 🔄 Agent-to-Agent (A2A) communication
- 🎯 Orchestrator pattern for task delegation
- 🔧 MCP (Model Context Protocol) integration
- 📊 Comprehensive examples and documentation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User / API Client                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Orchestrator Agent   │ ◄─── A2A Service
              │  (Task Routing)      │
              └──────────┬───────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌────────┐    ┌────────────┐   ┌──────────┐
    │  K8s   │    │ Monitoring │   │ Security │
    │ Debug  │    │   Agent    │   │  Agent   │
    │ Agent  │    │            │   │          │
    └───┬────┘    └─────┬──────┘   └────┬─────┘
        │               │               │
        ▼               ▼               ▼
    ┌────────┐    ┌────────────┐   ┌──────────┐
    │  K8s   │    │ Monitoring │   │ Security │
    │  MCP   │    │    MCP     │   │   MCP    │
    │ Server │    │   Server   │   │  Server  │
    └────────┘    └────────────┘   └──────────┘
```

## Components

### 1. Specialized Skill Agents

#### 🔍 K8s Debug Agent (`k8s-debug-agent`)
**Purpose**: Kubernetes troubleshooting specialist
- Diagnose pod failures and crashes
- Analyze container logs
- Inspect resource states
- Check networking and connectivity
- Review cluster events

**Tools**: K8s MCP server (kubectl operations)
**A2A Service**: Configured in Agent spec

#### 📊 Monitoring Agent (`monitoring-agent`)
**Purpose**: Observability and performance specialist
- Analyze resource utilization metrics
- Detect performance anomalies
- Monitor application health
- Recommend optimization strategies
- Trend analysis

**Tools**: Monitoring MCP server + K8s MCP server
**A2A Service**: Configured in Agent spec

#### 🔒 Security Agent (`security-agent`)
**Purpose**: Security and compliance specialist
- Security scanning and vulnerability assessment
- RBAC analysis
- Network policy evaluation
- Pod security standards validation
- Compliance auditing

**Tools**: Security MCP server + K8s MCP server
**A2A Service**: Configured in Agent spec

### 2. Orchestrator Agent

#### 🎯 Orchestrator (`orchestrator-agent`)
**Purpose**: Main coordination and routing agent
- Analyzes incoming requests
- Routes to appropriate specialist agents
- Coordinates multi-agent workflows
- Aggregates and synthesizes responses
- User-facing interface

**Communication**: A2A clients to all specialist agents
**A2A Service**: Configured in Agent spec

### 3. MCP Servers

MCP (Model Context Protocol) servers provide tools that agents can use:
- **kagent-tool-server**: Kubernetes operations (kubectl)
- **monitoring-mcp-server**: Metrics and performance tools
- **security-mcp-server**: Security scanning tools

### 4. A2A Protocol

Agent-to-Agent (A2A) protocol enables:
- Service discovery between agents
- Standardized inter-agent communication
- Skill exposure and invocation
- Multi-agent workflow coordination

## Quick Start

### Prerequisites

1. Kind cluster named `kind-kagent-demo` (already exists)
2. Kagent CRDs and controller installed
3. Gemini API key

### Installation

1. **Create the Gemini API secret**:
```bash
cd /home/umesh-bb/Desktop/kagent
source keys.txt

# The secret is already created, but if needed:
kubectl create secret generic kagent-gemini \
  -n kagent \
  --from-literal=GOOGLE_API_KEY=$GOOGLE_API_KEY
```

2. **Deploy all manifests**:
```bash
# Apply in order
kubectl apply -f manifests/00-namespace.yaml
kubectl apply -f manifests/02-model-config.yaml
kubectl apply -f manifests/03-mcp-servers.yaml
kubectl apply -f manifests/04-skill-agents.yaml
kubectl apply -f manifests/06-orchestrator.yaml

# Or apply all at once
kubectl apply -f manifests/
```

3. **Verify deployment**:
```bash
# Check all agents
kubectl get agents -n kagent

# Check A2A configuration in agents
kubectl get agents -n kagent -o wide

# Check MCP servers
kubectl get remotemcpserver -n kagent

# Check model config
kubectl get modelconfig -n kagent
```

## Usage Examples

### Example 1: Simple Kubernetes Troubleshooting

Talk directly to the K8s Debug agent:
```bash
kagent invoke --agent k8s-debug-agent --task "Why is the pod xyz in namespace abc crashing?"
```

### Example 2: Comprehensive Health Check via Orchestrator

The orchestrator coordinates multiple agents:
```bash
# Ask: "Perform a comprehensive health check of my cluster"
kagent invoke --agent orchestrator-agent --task "Perform a comprehensive health check of my cluster"

# The orchestrator will:
# 1. Call k8s-debug-service to check resources
# 2. Call monitoring-service to check metrics
# 3. Call security-service to check security posture
# 4. Aggregate results
```

### Example 3: A2A Client Usage

See `examples/a2a-client-example.yaml` for a full example of creating a client that calls other agents via A2A.

### Example 4: Custom MCP Server

See `examples/custom-mcp-server.yaml` for:
- How to implement a custom MCP server
- How to deploy it in Kubernetes
- How to register it with kagent
- How to use it in an agent

## Configuration

### Model Configuration

Edit `manifests/02-model-config.yaml` to change:
- Model version (currently `gemini-2.0-flash-exp`)
- Temperature
- Max output tokens
- Other Gemini-specific settings

### Agent System Messages

Each agent has a detailed system message defining its:
- Role and expertise
- Available tools
- Decision-making process
- Communication style

Edit the agent manifests in `manifests/04-skill-agents.yaml` and `manifests/06-orchestrator.yaml`.

### A2A Skills

### A2A Skills

A2A skills are now configured directly in the Agent resource under `a2aConfig`. Edit `manifests/04-skill-agents.yaml` or `manifests/06-orchestrator.yaml` to:
- Add new skills
- Modify skill descriptions
- Change skill names

## Testing A2A Communication

1. **Deploy the example A2A client**:
```bash
kubectl apply -f examples/a2a-client-example.yaml
```

2. **Check A2A service status**:
```bash
kubectl get agents -n kagent -o jsonpath='{range .items[*]}{.metadata.name}{"\n   "}{.spec.declarative.a2aConfig.skills[*].id}{"\n"}{end}'
```

3. **Test inter-agent communication**:
```bash
```bash
# Get the orchestrator session and send queries
kagent invoke --agent orchestrator-agent --task "Hello"
```

## Directory Structure

```
/home/umesh-bb/Desktop/kagent/
├── manifests/
│   ├── 00-namespace.yaml          # Namespace definition
│   ├── 02-model-config.yaml       # Gemini model configuration
│   ├── 03-mcp-servers.yaml        # MCP server registrations
│   ├── 04-skill-agents.yaml       # Specialized skill agents
│   └── 06-orchestrator.yaml       # Orchestrator agent
├── examples/
│   ├── a2a-client-example.yaml    # A2A client example
│   └── custom-mcp-server.yaml     # Custom MCP server example
├── keys.txt                        # API keys (gitignored)
└── README.md                       # This file
```

## Troubleshooting

### Agents not ready

Check agent status:
```bash
kubectl get agents -n kagent
kubectl describe agent <agent-name> -n kagent
```

Common issues:
- Missing API key secret
- Invalid model configuration
- MCP server not available

### A2A communication failing

# Check agent A2A configuration
kubectl get agent <agent-name> -n kagent -o yaml | grep a2aConfig
```

Check agent logs:
```bash
kubectl logs -n kagent <agent-pod-name>
```

### MCP server connection issues

Verify MCP server registration:
```bash
kubectl get remotemcpserver -n kagent
kubectl describe remotemcpserver <server-name> -n kagent
```

Check if MCP server pods are running:
```bash
kubectl get pods -n kagent -l app=<mcp-server-name>
```

## Advanced Usage

### Creating Custom Agents

1. Create agent manifest with appropriate system message
2. Configure tools (MCP servers or A2A clients)
3. Optional: Create A2A service to expose the agent
4. Apply and test

### Multi-Agent Workflows

The orchestrator demonstrates multi-agent patterns:
- **Sequential**: One agent's output feeds the next
- **Parallel**: Multiple agents work independently
- **Conditional**: Route based on request type
- **Aggregation**: Combine multiple agent responses

### Extending MCP Servers

Add more capabilities:
1. Implement MCP server following the protocol
2. Deploy as Kubernetes service
3. Register with RemoteMCPServer CRD
4. Add to agent tool configurations

## Resources

- [Kagent Documentation](https://kagent.dev)
- [A2A Protocol Specification](https://a2a.dev)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)

## License

This setup is provided as-is for demonstration purposes.
