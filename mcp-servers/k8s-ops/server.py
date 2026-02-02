#!/usr/bin/env python3
"""K8s Operations MCP Server"""
from mcp.server.fastmcp import FastMCP
from kubernetes import client, config

# Initialize K8s client
try:
    config.load_incluster_config()
except:
    try:
        config.load_kube_config()
    except:
        print("Warning: Could not load k8s config")

v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

# Create MCP server
mcp = FastMCP("k8s-ops")

@mcp.tool()
def list_pods(namespace: str = "default") -> list[str]:
    """List pods in a specific namespace"""
    pods = v1.list_namespaced_pod(namespace)
    return [p.metadata.name for p in pods.items]

@mcp.tool()
def get_pod_logs(name: str, namespace: str = "default") -> str:
    """Get logs from a specific pod"""
    return v1.read_namespaced_pod_log(name, namespace, tail_lines=50)

@mcp.tool()
def list_namespaces() -> list[str]:
    """List all namespaces in the cluster"""
    ns_list = v1.list_namespace()
    return [n.metadata.name for n in ns_list.items]

@mcp.tool()
def list_services(namespace: str = "default") -> list[str]:
    """List services in a namespace"""
    svcs = v1.list_namespaced_service(namespace)
    return [s.metadata.name for s in svcs.items]

@mcp.tool()
def list_deployments(namespace: str = "default") -> list[str]:
    """List deployments in a namespace"""
    deps = apps_v1.list_namespaced_deployment(namespace)
    return [d.metadata.name for d in deps.items]

@mcp.tool()
def list_nodes() -> list[str]:
    """List all nodes in the cluster"""
    nodes = v1.list_node()
    return [n.metadata.name for n in nodes.items]

@mcp.tool()
def list_events(namespace: str = "default") -> list[str]:
    """List events in a namespace"""
    events = v1.list_namespaced_event(namespace)
    return [f"{e.last_timestamp} - {e.type} - {e.reason} - {e.message}" for e in events.items]

if __name__ == "__main__":
    # Use default transport - FastMCP will handle it
    mcp.run()
