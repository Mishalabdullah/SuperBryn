#!/bin/bash

# LiveKit Agent Deployment Script
# This script deploys the appointment booking agent to LiveKit Cloud

set -e  # Exit on error

echo "🚀 Deploying LiveKit Agent to Cloud..."
echo ""

# Check if lk CLI is installed
if ! command -v lk &> /dev/null; then
    echo "❌ LiveKit CLI not found. Please install it first:"
    echo "   brew install livekit-cli"
    echo "   Or download from: https://github.com/livekit/livekit-cli/releases"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "livekit.toml" ]; then
    echo "❌ livekit.toml not found. Please run this from the agent-starter-python directory."
    exit 1
fi

# Deploy the agent
echo "📦 Building and deploying agent..."
lk agent deploy

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "📊 Checking agent status..."
    lk agent status
    echo ""
    echo "💡 To view logs, run: lk agent logs"
    echo "💡 To check status, run: lk agent status"
else
    echo "❌ Deployment failed. Check the error messages above."
    exit 1
fi
