#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  🎭 Tavus Avatar Setup for LiveKit Agent"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This script will help you create a Tavus persona for your agent."
echo ""
echo "IMPORTANT: You need to create a REPLICA first in the Tavus dashboard!"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

TAVUS_API_KEY="35f2755cf4c943c099e43dcc6e13f50f"

echo "Step 1: Create a Replica"
echo "------------------------"
echo ""
echo "1. Go to: https://tavus.io/dashboard/replicas"
echo "2. Click 'Create Replica'"
echo "3. Upload a video (or use a stock/demo video)"
echo "4. Wait for processing (takes a few minutes)"
echo "5. Copy the Replica ID when ready"
echo ""
read -p "Enter your Tavus Replica ID: " REPLICA_ID
echo ""

if [ -z "$REPLICA_ID" ]; then
    echo "❌ Error: Replica ID cannot be empty"
    exit 1
fi

echo "✅ Replica ID: $REPLICA_ID"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Step 2: Creating Persona with LiveKit Configuration..."
echo ""

# Create persona via Tavus API
RESPONSE=$(curl -s --request POST \
  --url https://tavusapi.com/v2/personas \
  -H "Content-Type: application/json" \
  -H "x-api-key: $TAVUS_API_KEY" \
  -d "{
    \"replica_id\": \"$REPLICA_ID\",
    \"layers\": {
        \"transport\": {
            \"transport_type\": \"livekit\"
        }
    },
    \"persona_name\": \"Appointment Assistant\",
    \"pipeline_mode\": \"echo\"
}")

echo "API Response:"
echo "$RESPONSE"
echo ""

# Extract persona_id from response (simple grep/sed approach)
PERSONA_ID=$(echo "$RESPONSE" | grep -o '"persona_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$PERSONA_ID" ]; then
    echo "❌ Failed to create persona. Check the response above for errors."
    echo ""
    echo "Common issues:"
    echo "  - Invalid Replica ID"
    echo "  - API key incorrect"
    echo "  - Replica not yet processed"
    echo ""
    exit 1
fi

echo "✅ Persona created successfully!"
echo "   Persona ID: $PERSONA_ID"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Step 3: Updating .env.local..."
echo ""

# Backup original .env.local
cp .env.local .env.local.backup

# Update the .env.local file
sed -i "s/^TAVUS_REPLICA_ID=.*/TAVUS_REPLICA_ID=$REPLICA_ID/" .env.local
sed -i "s/^TAVUS_PERSONA_ID=.*/TAVUS_PERSONA_ID=$PERSONA_ID/" .env.local

echo "✅ .env.local updated!"
echo ""
echo "Updated values:"
grep "TAVUS_REPLICA_ID\|TAVUS_PERSONA_ID" .env.local
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🎉 Tavus Avatar Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Restart your agent: ./start_agent.sh"
echo "2. Refresh your frontend"
echo "3. Start a call - you should now see your avatar!"
echo ""
echo "════════════════════════════════════════════════════════════════"
