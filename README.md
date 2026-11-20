# Kagent Multi-Agent Setup with A2A and MCP

A [kagent](https://kagent.dev) setup of specialised Kubernetes AI agents with an orchestrator, Agent-to-Agent (A2A) delegation and MCP tool servers, deployable on a k3s or Kind cluster. Features:
- 🤖 Multiple specialized AI agents using **DeepSeek** (via OpenAI)
- 🔄 Agent-to-Agent (A2A) communication
- 🎯 Orchestrator pattern with prioritized delegation
- 🔧 MCP (Model Context Protocol) integration
- 📂 Advanced **Cluster Admin Agent** for full CRUD operations

## Table of Contents

- [Architecture](#architecture)
- [Components](#components)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Testing A2A Communication](#testing-a2a-communication)
- [Repository Structure](#directory-structure)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)
- [Security Notes](#security-notes)
- [Resources](#resources)
- [License](#license)
- [Author](#author)

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
         └───────────────┼───────────────┘
                         ▼
          ┌──────────────────────────────┐
          │ MCP servers: kagent-tool-    │
          │ server and k8s-mcp           │
          └──────────────────────────────┘
```

The orchestrator also delegates to `cluster-admin-agent` (see `manifests/06-orchestrator.yaml`). All agents use the `kagent-tool-server` and `k8s-mcp` RemoteMCPServers (`manifests/03-mcp-servers.yaml`).

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

**Tools**: `kagent-tool-server` and `k8s-mcp`
**A2A Service**: Configured in Agent spec

#### 🔒 Security Agent (`security-agent`)
**Purpose**: Security and compliance specialist
- Security scanning and vulnerability assessment
- RBAC analysis
- Network policy evaluation
- Pod security standards validation
- Compliance auditing

**Tools**: k8s-mcp (`pods_list`, `pods_log`, `resources_list`, etc.)
**A2A Service**: Configured in Agent spec

#### ⚒️ Cluster Admin Agent (`cluster-admin-agent`)
**Purpose**: Advanced Kubernetes administrator
- Full CRUD operations (Create, Update, Get, Delete)
- Scaling and lifecycle management
- Helm release management
- System-wide resource operations

**Tools**: Full administrative toolset from `k8s-mcp` and `kagent-tool-server`
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
- **kagent-tool-server**: kagent tool server (`http://kagent-tools.kagent.svc.cluster.local:8084`)
- **k8s-mcp**: Kubernetes MCP server, deployed from `manifests/05-k8s-mcp-deployment.yaml`

(No separate monitoring or security MCP servers are defined in the manifests.)

### 4. A2A Protocol

Agent-to-Agent (A2A) protocol enables:
- Service discovery between agents
- Standardized inter-agent communication
- Skill exposure and invocation
- Multi-agent workflow coordination

## Quick Start

### Prerequisites

- A Kubernetes cluster (k3s, or a local Kind cluster created by `setup.sh`), `kubectl`, `helm`
- For `setup.sh`: `docker`, `kind`, `curl`
- An OpenAI-compatible API key (the manifests use DeepSeek via `https://api.deepseek.com/v1`, model `deepseek-chat`), or a Google API key for Gemini (supported by `setup.sh`)

### Option A: Automated (Kind) with `setup.sh`

```bash
chmod +x setup.sh
export OPENAI_API_KEY=<your-api-key>   # or GOOGLE_API_KEY; otherwise you are prompted
./setup.sh
```

The script creates a Kind cluster `kind-kagent-demo`, installs the kagent CLI, the `kagent-crds` and `kagent` Helm charts (using `kagent-values.yaml`, which disables the built-in agents) and applies `manifests/`. Then:

```bash
kubectl port-forward -n kagent svc/kagent-ui 8080:8080   # open http://localhost:8080
```

### Option B: Existing cluster with `deploy-kagent.sh`

1. Install kagent via Helm first (with the API key; see the `helm upgrade --install kagent oci://ghcr.io/kagent-dev/kagent/helm/kagent ...` command in `setup.sh`) so the `kagent-openai` secret exists.
2. Point `KUBECONFIG` at your cluster. `deploy-kagent.sh` and `export-kubeconfig.sh` hard-code a local kubeconfig path; edit it for your machine.
3. Run:

```bash
chmod +x deploy-kagent.sh
./deploy-kagent.sh
```

It creates the `kagent` namespace, a `host-kubeconfig` secret from your kubeconfig, and applies the manifests in `manifests/`.

Or apply the manifests manually (the API key secret must already exist):

```bash
kubectl apply -f manifests/
```

### Verify deployment:
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
- Model (currently `deepseek-chat`, provider `OpenAI`, base URL `https://api.deepseek.com/v1`)
- The ModelConfig is named `llama3-model-config` and reads the key from secret `kagent-openai` (`OPENAI_API_KEY`)

### Agent System Messages

Each agent has a detailed system message defining its:
- Role and expertise
- Available tools
- Decision-making process
- Communication style

Edit the agent manifests in `manifests/04-skill-agents.yaml` and `manifests/06-orchestrator.yaml`.

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
# Get the orchestrator session and send queries
kagent invoke --agent orchestrator-agent --task "Hello"
```

## Directory Structure

```
.
├── README.md
├── QUICKSTART.md                     # Command cheat sheet
├── docs/A2A-IMPLEMENTATION.md        # How A2A is configured via a2aConfig
├── setup.sh                          # Kind + Helm + manifests automation
├── deploy-kagent.sh                  # Apply manifests to an existing cluster
├── export-kubeconfig.sh              # Sets KUBECONFIG (edit the path)
├── kagent-values.yaml                # Helm values (disables built-in agents)
├── manifests/
│   ├── 00-namespace.yaml             # kagent namespace
│   ├── 02-model-config.yaml          # ModelConfig (deepseek-chat via OpenAI provider)
│   ├── 03-mcp-servers.yaml           # RemoteMCPServers: kagent-tool-server, k8s-mcp
│   ├── 04-skill-agents.yaml          # k8s-debug, monitoring, security agents
│   ├── 05-k8s-mcp-deployment.yaml    # k8s-mcp Deployment, Service, RBAC
│   ├── 06-orchestrator.yaml          # orchestrator-agent
│   ├── 08-cluster-admin-agent.yaml   # cluster-admin-agent
│   └── kagent-openai.yaml            # Secret manifest (see Security Notes)
├── debug-agents/                     # Extra debug agent / orchestrator variants
└── examples/                         # A2A client and custom MCP server examples
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

## Security Notes

- Never commit API keys. `manifests/kagent-openai.yaml` is a Secret manifest exported from a Helm release; do not store a real key in it. Create the secret from an environment variable instead (for example via the Helm `--set providers.openAI.apiKey` flag used in `setup.sh`).
- `deploy-kagent.sh` stores your kubeconfig in the cluster as the `host-kubeconfig` secret and `cluster-admin-agent` has broad write access; use only on clusters you can afford to experiment on.
- Rotate any key that has ever been committed.

## Resources

- [Kagent Documentation](https://kagent.dev)
- [A2A Protocol Specification](https://a2a.dev)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [DeepSeek API](https://api-docs.deepseek.com/)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)

## License

Released under the [MIT License](LICENSE).

## Author

[Umesh Khatiwada](https://github.com/umesh-khatiwada)
