#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  🎙️  Starting AI Voice Agent Backend"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Status:"
echo "  ✅ Models downloaded"
echo "  ✅ Dependencies installed"
echo "  🚀 Starting agent server..."
echo ""
echo "The agent will be ready when you see: 'Agent connected and ready'"
echo ""
echo "Press Ctrl+C to stop the agent"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

uv run python src/agent.py dev
