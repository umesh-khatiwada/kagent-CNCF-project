#!/bin/bash

# Kagent Automated Setup Script for Kind Cluster
# This script sets up a kind cluster, installs kagent via Helm, and deploys project manifests.
# Supports both OpenAI and Gemini providers.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Kagent Project Setup...${NC}"

# 1. Prerequisites Check
echo -e "\n${YELLOW}🔍 Checking prerequisites...${NC}"
for cmd in docker kind kubectl helm curl; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}❌ Error: $cmd is not installed. Please install it and try again.${NC}"
        exit 1
    fi
    echo -e "✅ $cmd is installed"
done

# 2. Kind Cluster Setup
CLUSTER_NAME="kind-kagent-demo"
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo -e "\n${GREEN}✅ Kind cluster '${CLUSTER_NAME}' already exists.${NC}"
else
    echo -e "\n${YELLOW}🏗️ Creating Kind cluster '${CLUSTER_NAME}'...${NC}"
    kind create cluster --name ${CLUSTER_NAME}
fi

# Switch context
kubectl config use-context kind-${CLUSTER_NAME}

# 3. Kagent CLI Installation
if ! command -v kagent &> /dev/null; then
    echo -e "\n${YELLOW}📥 Installing Kagent CLI...${NC}"
    curl https://raw.githubusercontent.com/kagent-dev/kagent/main/scripts/get-kagent | bash
    # Add to path for current session
    export PATH=$PATH:/usr/local/bin
else
    echo -e "\n${GREEN}✅ Kagent CLI already installed.${NC}"
fi

# 4. API Key Setup
PROVIDER="openAI" # Default provider (camelCase required for Helm)
API_KEY=""

if [ -n "$OPENAI_API_KEY" ]; then
    API_KEY=$OPENAI_API_KEY
    PROVIDER="openAI"
    echo -e "\n${GREEN}✅ Using OPENAI_API_KEY from environment.${NC}"
elif [ -n "$GOOGLE_API_KEY" ]; then
    API_KEY=$GOOGLE_API_KEY
    PROVIDER="gemini"
    echo -e "\n${GREEN}✅ Using GOOGLE_API_KEY from environment.${NC}"
else
    echo -e "\n${YELLOW}🔑 No API key found in environment.${NC}"
    echo "Which provider would you like to use?"
    echo "1) OpenAI (DeepSeek/Generic)"
    echo "2) Gemini"
    read -p "Select [1-2]: " PROVIDER_CHOICE

    if [ "$PROVIDER_CHOICE" == "2" ]; then
        PROVIDER="gemini"
        read -p "Please enter your GOOGLE_API_KEY: " API_KEY
    else
        PROVIDER="openAI"
        read -p "Please enter your OPENAI_API_KEY: " API_KEY
    fi

    if [ -z "$API_KEY" ]; then
        echo -e "${RED}❌ Error: API Key is required.${NC}"
        exit 1
    fi
fi

# 5. Kagent Controller Installation (via Helm)
echo -e "\n${YELLOW}⚙️ Installing Kagent Controller via Helm...${NC}"

# Create namespace if it doesn't exist
kubectl create namespace kagent --dry-run=client -o yaml | kubectl apply -f -

# Install CRDs
echo -e "📦 Installing Kagent CRDs..."
helm upgrade --install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds -n kagent

# Install/Upgrade Kagent
echo -e "📦 Installing Kagent App (Provider: $PROVIDER)..."

# Delete old secrets and existing ModelConfigs/Agents/MCPServers to avoid conflicts and ownership issues
# We purge these because Helm expects to manage them if they are part of the chart
kubectl delete secret kagent-openai -n kagent --ignore-not-found
kubectl delete secret kagent-gemini -n kagent --ignore-not-found
kubectl delete modelconfig default-model-config -n kagent --ignore-not-found

# Purge any agents or MCP servers that might conflict with Helm's built-in ones
echo -e "🧹 Purging existing kagent resources to avoid Helm ownership conflicts..."
kubectl delete agents.kagent.dev --all -n kagent --ignore-not-found --wait
kubectl delete remotemcpservers.kagent.dev --all -n kagent --ignore-not-found --wait

if [ "$PROVIDER" == "gemini" ]; then
    helm upgrade --install kagent oci://ghcr.io/kagent-dev/kagent/helm/kagent -n kagent \
      --set providers.default=gemini \
      --set providers.gemini.apiKey=$API_KEY
else
    # openAI provider (case-sensitive)
    helm upgrade --install kagent oci://ghcr.io/kagent-dev/kagent/helm/kagent -n kagent \
      -f kagent-values.yaml \
      --set providers.default=openAI \
      --set providers.openAI.apiKey=$API_KEY \
      --set providers.openAI.model=deepseek-chat \
      --set providers.openAI.baseUrl=https://api.deepseek.com/v1
fi

# 6. Apply Project Manifests
echo -e "\n${YELLOW}📄 Applying project manifests...${NC}"
if [ -d "manifests" ]; then
    # Wait a moment for CRDs and Secrets to be fully ready
    sleep 5
    kubectl apply -f manifests/
else
    echo -e "${RED}❌ Error: manifests directory not found!${NC}"
    exit 1
fi

# 7. Verification
echo -e "\n${GREEN}✅ Setup complete! Verifying status...${NC}"

echo -e "\n${YELLOW}🤖 Agents Status:${NC}"
kubectl get agents -n kagent

echo -e "\n${YELLOW}🔧 MCP Servers Status:${NC}"
kubectl get remotemcpserver -n kagent

echo -e "\n${YELLOW}🌐 Dashboard Access:${NC}"
echo -e "To access the dashboard, run:"
echo -e "kubectl port-forward -n kagent svc/kagent-ui 8080:8080"
echo -e "Then open: http://localhost:8080"

echo -e "\n${GREEN}🎉 Kagent project is ready to use!${NC}"
