#!/bin/bash

# Deployment Verification Script for LiveKit Agent
# This script helps verify that your agent is properly deployed and updated

set -e

echo "🔍 LiveKit Agent Deployment Verification"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "livekit.toml" ]; then
    echo "❌ Error: livekit.toml not found. Please run this from the agent-starter-python directory."
    exit 1
fi

# Check if lk CLI is installed
if ! command -v lk &> /dev/null; then
    echo "❌ LiveKit CLI not found. Please install it first:"
    echo "   brew install livekit-cli"
    exit 1
fi

echo "📊 Step 1: Checking Agent Status"
echo "--------------------------------"
lk agent status
echo ""

echo "📝 Step 2: Recent Deployment Logs (last 20 lines)"
echo "------------------------------------------------"
lk agent logs --tail 20
echo ""

echo "🏗️  Step 3: Recent Builds"
echo "------------------------"
lk agent builds --limit 3
echo ""

echo "✅ Verification Complete!"
echo ""
echo "💡 Next Steps:"
echo "   1. Check the 'Deployed At' timestamp above - should be recent"
echo "   2. Look for 'v1.1.0-slots-fix' in the logs above"
echo "   3. Verify Status shows 'Running'"
echo "   4. Test the agent by asking: 'What appointment slots are available?'"
echo ""
echo "📍 Dashboard: https://cloud.livekit.io/projects/p_/agents"
echo ""
