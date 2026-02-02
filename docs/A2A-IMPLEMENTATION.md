# A2A Protocol Integration - UPDATED

## ✅ A2A Now Configured!

The agents have been updated with `a2aConfig` sections to expose their skills via the A2A protocol.

## What Changed

Instead of using separate `A2AService` resources (which don't exist as CRDs), kagent uses an `a2aConfig` section directly in each Agent definition.

## Agent Configuration

Each agent now has an `a2aConfig` section that defines its skills:

### K8s Debug Agent Skills

```yaml
a2aConfig:
  skills:
    - id: diagnose-pod-issues
      name: Diagnose Pod Issues
      description: Diagnose pod startup failures, crashes, or restart loops
      examples:
        - "Why is my pod crashing?"
        - "Diagnose pod failures in namespace X"
    
    - id: analyze-logs
      name: Analyze Logs  
      description: Analyze container logs to identify errors
      examples:
        - "Show logs for pod X"
        
    - id: inspect-resources
      name: Inspect Resources
      description: Inspect Kubernetes resource states
      examples:
        - "Check deployment status"
```

### Monitoring Agent Skills

```yaml
a2aConfig:
  skills:
    - id: analyze-metrics
      name: Analyze Metrics
      description: Analyze resource utilization metrics
      examples:
        - "Show CPU usage"
        
    - id: health-check
      name: Health Check
      description: Perform comprehensive health checks
      examples:
        - "Check cluster health"
```

### Security Agent Skills

```yaml
a2aConfig:
  skills:
    - id: security-scan
      name: Security Scan
      description: Perform security scans for vulnerabilities
      examples:
        - "Scan for vulnerabilities"
        
    - id: rbac-analysis
      name: RBAC Analysis
      description: Analyze RBAC permissions
      examples:
        - "Analyze RBAC permissions"
```

### Orchestrator Skills

```yaml
a2aConfig:
  skills:
    - id: comprehensive-analysis
      name: Comprehensive Analysis
      description: Multi-agent comprehensive analysis
      examples:
        - "Perform a full cluster analysis"
        
    - id: troubleshoot
      name: Troubleshoot
      description: Multi-agent troubleshooting
      examples:
        - "My application is slow - investigate"
```

## Accessing A2A Endpoints

The A2A endpoints are exposed via the kagent-controller service on port 8083.

### 1. Port Forward

```bash
kubectl port-forward svc/kagent-controller 8083:8083 -n kagent
```

### 2. Access Agent Card

Each agent exposes its capabilities at `.well-known/agent.json`:

```bash
# Orchestrator agent card
curl localhost:8083/api/a2a/kagent/orchestrator-agent/.well-known/agent.json

# K8s debug agent card
curl localhost:8083/api/a2a/kagent/k8s-debug-agent/.well-known/agent.json

# Monitoring agent card  
curl localhost:8083/api/a2a/kagent/monitoring-agent/.well-known/agent.json

# Security agent card
curl localhost:8083/api/a2a/kagent/security-agent/.well-known/agent.json
```

### 3. Agent Card Structure

The agent card follows the [A2A protocol specification](https://a2a.guide/protocol/agent-card.html) and includes:

- Agent name and description
- URL endpoint
- Capabilities (streaming, notifications, etc.)
- Skills with examples
- Input/output modes
- Tags for categorization

## Calling Agents via A2A

### From Another Agent

Agents can call each other using the `type: Agent` tool configuration:

```yaml
tools:
  - type: Agent
    agent:
      name: k8s-debug-agent
      kind: Agent
      apiGroup: kagent.dev
```

The orchestrator agent uses this to coordinate the specialist agents.

### From External A2A Client

You can use an A2A-compatible client to invoke agents:

```bash
# Using A2A host CLI (if installed)
a2a invoke http://localhost:8083/api/a2a/kagent/orchestrator-agent \
  "Perform a cluster health check"
```

### Via Kagent Dashboard/CLI

Use the kagent dashboard or CLI to interact with agents (see kagent documentation).

## Files Updated

- ✅ `manifests/04-skill-agents.yaml` - Added a2aConfig to all skill agents
- ✅ `manifests/06-orchestrator.yaml` - Added a2aConfig to orchestrator
- ✅ `manifests/05-a2a-services.yaml` - Backed up (not needed)

## Benefits of A2A Configuration

1. **Skill Discovery**: Other agents/systems can discover what each agent can do
2. **Standardized Interface**: Follows A2A protocol for interoperability  
3. **Clear Examples**: Each skill has example queries
4. **Tag-based Organization**: Skills are categorized with tags
5. **Multi-modal Support**: Specify input/output modes (text, audio, etc.)

## Comparison: Before vs After

### Before (Our Initial Approach)
- Used separate `A2AService` CRD (doesn't exist)
- Required additional manifests
- Not compatible with kagent's implementation

### After (Correct Approach)
- Uses `a2aConfig` in Agent spec
- Native kagent A2A support
- Automatic endpoint exposure via kagent-controller
- Follows kagent documentation patterns

## Testing A2A

### 1. Verify Agent Cards

```bash
# Port forward kagent-controller (in default namespace)
kubectl port-forward svc/kagent-controller 8083:8083 -n default

# In another terminal, check agent cards
for agent in orchestrator-agent k8s-debug-agent monitoring-agent security-agent; do
  echo "=== $agent ==="
  curl -s localhost:8083/api/a2a/kagent/$agent/.well-known/agent.json | \
    python3 -m json.tool | head -30
  echo
done
```

### 2. Check Skills

The agent card JSON will show all configured skills with their descriptions and examples.

### 3. Invoke via A2A

Follow the kagent documentation for invoking agents via A2A protocol.

## Next Steps

1. ✅ A2A configuration added to all agents
2. ✅ Skills defined with examples
3. ✅ Agent endpoints accessible via kagent-controller
4. 📝 Test A2A invocation via kagent dashboard/CLI
5. 📝 Integrate with external A2A clients if needed

## Resources

- [Kagent A2A Documentation](https://kagent.dev/docs/kagent/examples/a2a-agents)
- [A2A Protocol Specification](https://a2a.guide)
- [Agent Card Format](https://a2a.guide/protocol/agent-card.html)
