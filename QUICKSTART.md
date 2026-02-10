# Quick Reference Guide - Kagent Multi-Agent Setup

## Quick Status Check

```bash
# View all agents
kubectl get agents -n kagent

# View model configs
kubectl get modelconfig -n kagent

# View MCP servers
kubectl get remotemcpserver -n kagent

# View secrets
kubectl get secret kagent-openai -n kagent
```

## Deployed Agents

| Agent | Purpose | Command to Describe |
|-------|---------|---------------------|
| `orchestrator-agent` | Main coordinator | `kubectl describe agent orchestrator-agent -n kagent` |
| `k8s-debug-agent` | K8s debugging | `kubectl describe agent k8s-debug-agent -n kagent` |
| `monitoring-agent` | Monitoring | `kubectl describe agent monitoring-agent -n kagent` |
| `security-agent` | Security | `kubectl describe agent security-agent -n kagent` |
| `cluster-admin-agent` | Cluster Admin | `kubectl describe agent cluster-admin-agent -n kagent` |

## Common Commands

### Create a Chat Session

```bash
# With orchestrator (recommended for general queries)
kubectl create -f - <<EOF
### 1. Using Kagent CLI

Make sure you have port-forwarded the controller:
```bash
# In a separate terminal
kubectl port-forward svc/kagent-controller 8083:8083 -n default
```

Invoke an agent:
```bash
# Ask the orchestrator
kagent invoke --agent orchestrator-agent --task "Perform a cluster health check"

# Ask a specialist directly
kagent invoke --agent k8s-debug-agent --task "List pods in kagent namespace"
```

### 2. Using the Dashboard

Port-forward the UI service:
```bash
# In a separate terminal
kubectl port-forward svc/kagent-ui 8080:8080 -n default
```

1. Open http://localhost:8080 in your browser
2. Select an agent (e.g., `orchestrator-agent`)
3. Type your message and send

### View Chat Sessions

```bash
kubectl get chatsessions -n kagent
kubectl describe chatsession <session-name> -n kagent
```

### Update Model Config

```bash
kubectl edit modelconfig default-model-config -n kagent
```

### Add New Agent

1. Create agent manifest in `manifests/`
2. Apply: `kubectl apply -f manifests/your-agent.yaml`
3. Verify: `kubectl get agent your-agent -n kagent`

## Orchestrator Routing Logic

The orchestrator automatically routes requests:

| Request Type | Routes To |
|--------------|-----------|
| Pod issues, logs, debugging | `k8s-debug-agent` |
| Metrics, performance, health | `monitoring-agent` |
| Security, RBAC, compliance | `security-agent` |
| Complex/multi-domain | Multiple agents |

## Example Queries

### To Orchestrator
- "Perform a comprehensive health check"
- "My app is slow and crashing - investigate"  
- "Full security and performance audit"

### To K8s Debug Agent
- "Why is pod X crashing?"
- "Show me logs for deployment Y"
- "Check events in namespace Z"

### To Monitoring Agent
- "Show cluster resource usage"
- "Are there any performance issues?"
- "Analyze CPU and memory trends"

### To Security Agent
- "Scan for vulnerabilities"
- "Check RBAC permissions for user X"
- "Audit pod security policies"

## Troubleshooting

### Agent Not Ready

```bash
kubectl describe agent <agent-name> -n kagent
# Check Status section for errors
```

### Wrong Model/API Key

```bash
# Update secret
kubectl delete secret kagent-gemini -n kagent
kubectl create secret generic kagent-gemini -n kagent \
  --from-literal=GOOGLE_API_KEY=your-new-key

# Update model config
kubectl edit modelconfig default-model-config -n kagent
```

### MCP Server Issues

```bash
# Check MCP server registration
kubectl get remotemcpserver <server-name> -n kagent -o yaml

# Check if server pods exist (if deployed)
kubectl get pods -n kagent -l app=<mcp-server-name>
```

## Files

- **Main Documentation**: `README.md`
- **Deployment Walkthrough**: `.gemini/antigravity/brain/.../walkthrough.md`
- **A2A Migration Guide**: `docs/A2A-FUTURE.md`
- **Manifests**: `manifests/*.yaml`
- **Examples**: `examples/*.yaml`

## Key Architecture Points

1. **Orchestrator** is the user-facing agent that routes to specialists
2. **Specialist agents** have domain expertise (K8s, monitoring, security)
3. **Agent-to-agent** communication happens via `type: Agent` tools
4. **MCP servers** provide tools that agents can use
5. **Gemini 2.0 Flash** powers all agents via shared model config

## Next Steps After Deployment

1. Create test chat sessions
2. Ask questions to test routing
3. Monitor agent performance
4. Deploy actual MCP servers (optional)
5. Add more specialist agents as needed
6. Explore A2A protocol when available

---

**Cluster**: kind-kagent-demo  
**Namespace**: kagent  
**Model**: Gemini 2.0 Flash (Experimental)  
**Agents**: 4 (1 orchestrator + 3 specialists)
