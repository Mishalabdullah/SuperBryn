# Quick Test Guide

## Option 1: Test WITHOUT Avatar (Fastest - Audio Only)

The agent will work perfectly in audio-only mode while you set up Tavus. The code gracefully handles missing Tavus credentials.

### Step 1: Verify Environment Variables

```bash
cd agent-starter-python
cat .env.local
```

Make sure you have:
- ✅ OPENAI_API_KEY
- ✅ DEEPGRAM_API_KEY
- ✅ CARTESIA_API_KEY
- ✅ LIVEKIT credentials
- ✅ SUPABASE credentials

### Step 2: Download Required Models

```bash
uv run python src/agent.py download-files
```

This downloads:
- Silero VAD model
- LiveKit turn detector

### Step 3: Test in Console Mode (Voice Test)

```bash
uv run python src/agent.py console
```

This lets you talk to the agent directly in your terminal!

**Try these commands:**
1. "My phone number is 5551234567"
2. "I'd like to book an appointment for tomorrow at 2pm"
3. "My name is John Doe"
4. "What appointments do I have?"
5. "Cancel my appointment"
6. "Goodbye"

### Step 4: Run Backend for Web Testing

```bash
uv run python src/agent.py dev
```

Leave this running in one terminal.

### Step 5: Run Frontend (New Terminal)

```bash
cd agent-starter-react
pnpm install
pnpm dev
```

### Step 6: Test in Browser

1. Open http://localhost:3000
2. Click "Start call"
3. Allow microphone access
4. Talk to the agent!

**Test Flow:**
1. Say your phone number
2. Say your name
3. Ask "What times are available tomorrow?"
4. Book an appointment
5. Ask "What appointments do I have?"
6. Say "Goodbye" to see the summary

---

## Option 2: Test WITH Tavus Avatar

### Step 1: Create Tavus Persona

You need to create a Tavus replica and persona first. Here's how:

#### A. Get Tavus API Key
- Already in .env.local: `TAVUS_API_KEY=35f2755cf4c943c099e43dcc6e13f50f`

#### B. Create Replica
1. Go to https://tavus.io/dashboard
2. Navigate to "Replicas"
3. Click "Create Replica"
4. Upload a short video (or use stock)
5. Copy the Replica ID

#### C. Create Persona (via API)

Run this command (replace YOUR_REPLICA_ID with the ID from step B):

```bash
curl --request POST \
  --url https://tavusapi.com/v2/personas \
  -H "Content-Type: application/json" \
  -H "x-api-key: 35f2755cf4c943c099e43dcc6e13f50f" \
  -d '{
    "layers": {
        "transport": {
            "transport_type": "livekit"
        }
    },
    "persona_name": "Appointment Assistant",
    "pipeline_mode": "echo",
    "replica_id": "YOUR_REPLICA_ID"
}'
```

This will return a JSON with `persona_id`. Copy it!

#### D. Update .env.local

```bash
# Edit agent-starter-python/.env.local
TAVUS_REPLICA_ID=your_replica_id_here
TAVUS_PERSONA_ID=your_persona_id_here
```

#### E. Restart Agent

```bash
# Stop the dev server (Ctrl+C)
uv run python src/agent.py dev
```

Now the avatar will appear!

---

## Option 3: Quick Database Test

Before running the full agent, test the database connection:

```python
# Run this in Python console
import os
from dotenv import load_dotenv
load_dotenv('.env.local')

from src.database import DatabaseManager

db = DatabaseManager()

# Test creating a user
import asyncio
async def test():
    user = await db.create_user_profile("1234567890", "Test User")
    print("User created:", user)
    
    # Get user
    found = await db.get_user_profile("1234567890")
    print("User found:", found)

asyncio.run(test())
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'supabase'"
- Run: `uv sync` in agent-starter-python folder

### "OPENAI_API_KEY not found"
- Make sure .env.local exists in agent-starter-python/
- Check that all API keys are set

### "Cannot connect to Supabase"
- Verify your Supabase project is active
- Check SUPABASE_URL and SUPABASE_KEY in .env.local

### "No audio in browser"
- Check microphone permissions
- Try Chrome/Edge (best WebRTC support)
- Make sure backend agent is running

### Agent says "Tavus avatar failed to load"
- This is OK! Agent continues in audio-only mode
- To enable avatar, follow Option 2 above

---

## What to Expect

### With Audio Only (No Avatar)
- ✅ Voice conversation works perfectly
- ✅ All 7 tools function correctly
- ✅ Database integration works
- ✅ UI shows tool calls and appointments
- ✅ Summary generated at end
- ❌ No visual avatar (blank or placeholder)

### With Avatar (Tavus Configured)
- ✅ Everything above PLUS
- ✅ Realistic avatar video
- ✅ Lip-sync with speech
- ✅ Natural facial expressions

---

## Performance Testing

Once it's working, test these scenarios:

### Happy Path
1. ✅ Identify user
2. ✅ Check availability
3. ✅ Book appointment
4. ✅ Confirm booking
5. ✅ End call with summary

### Edge Cases
1. ✅ Try to book same slot twice (should prevent)
2. ✅ Try to book past date (should reject)
3. ✅ Book without giving phone number (should ask for it)
4. ✅ Say "I don't know" when asked for date (should clarify)
5. ✅ Interrupt agent mid-sentence (should handle gracefully)

### Database Verification
After booking an appointment, check Supabase:
1. Go to your Supabase dashboard
2. Table Editor → appointments
3. You should see your appointment listed!

---

## Next Steps After Testing

Once everything works locally:

1. **Deploy Backend**
   ```bash
   lk agent deploy
   ```

2. **Deploy Frontend**
   ```bash
   # Push to GitHub first
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create --public
   
   # Then deploy on Vercel
   # Go to vercel.com and import your repo
   ```

3. **Test Production**
   - Use the Vercel URL
   - Test full flow end-to-end
   - Verify database updates

---

## Quick Checklist

Before testing:
- [ ] Supabase tables created (run supabase_setup.sql)
- [ ] Backend dependencies installed (`uv sync`)
- [ ] Frontend dependencies installed (`pnpm install`)
- [ ] Models downloaded (`download-files`)
- [ ] Environment variables set
- [ ] Microphone working

During testing:
- [ ] Backend agent running (`dev` mode)
- [ ] Frontend running (http://localhost:3000)
- [ ] Can connect and hear agent
- [ ] Can give phone number
- [ ] Can book appointment
- [ ] Appointment shows in UI
- [ ] Summary displays at end

After testing:
- [ ] Verify data in Supabase
- [ ] Check conversation_summaries table
- [ ] Test from different browser
- [ ] Ready to deploy!

---

Good luck! 🚀

If you get stuck, check the console logs - they're very detailed and will help debug issues.
