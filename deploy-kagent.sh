#!/bin/bash
set -e

# Set KUBECONFIG
export KUBECONFIG=/home/umesh-bb/Desktop/kubeconfig/k3s.yaml

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "kubectl not found. Please install kubectl."
    exit 1
fi

# Ensure namespace exists
kubectl create namespace kagent --dry-run=client -o yaml | kubectl apply -f -

# Check for API key secret
if ! kubectl get secret kagent-openai -n kagent &> /dev/null; then
    echo "Error: API key secret 'kagent-openai' not found in namespace 'kagent'."
    echo "Please create it manually or provide the key via notify_user."
    exit 1
else
    echo "API key secret 'kagent-openai' exists."
fi

# Create host-kubeconfig secret from local k3s.yaml
echo "Creating host-kubeconfig secret from local k3s.yaml..."
kubectl create secret generic host-kubeconfig \
    -n kagent \
    --from-file=config=$KUBECONFIG \
    --dry-run=client -o yaml | kubectl apply -f -

# Apply manifests
echo "Applying manifests..."
kubectl apply -f manifests/00-namespace.yaml
kubectl apply -f manifests/02-model-config.yaml
kubectl apply -f manifests/03-mcp-servers.yaml
kubectl apply -f manifests/04-skill-agents.yaml
kubectl apply -f manifests/05-k8s-mcp-deployment.yaml
kubectl apply -f manifests/06-orchestrator.yaml

echo "Deployment complete!"
kubectl get agents -n kagent
