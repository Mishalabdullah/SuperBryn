# Setup Instructions for AI Voice Agent

This guide will walk you through setting up the complete AI Voice Agent with Tavus Avatar.

## Prerequisites

- Node.js 18+ and pnpm (for frontend)
- Python 3.10-3.13 and uv (for backend)
- Supabase account (free tier)
- LiveKit Cloud account (free tier)
- API keys for: OpenAI, Deepgram, Cartesia, Tavus

---

## Part 1: Supabase Database Setup

### Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in project details:
   - Name: `appointment-agent` (or your choice)
   - Database Password: Choose a strong password
   - Region: Select closest to you
5. Click "Create new project" and wait for provisioning

### Step 2: Run SQL Setup Script

1. In your Supabase dashboard, go to **SQL Editor** (left sidebar)
2. Click **New Query**
3. Copy the entire contents of `agent-starter-python/supabase_setup.sql`
4. Paste into the SQL editor
5. Click **Run** (or press Cmd/Ctrl + Enter)
6. You should see "Success. No rows returned" message

### Step 3: Verify Tables Created

1. Go to **Table Editor** (left sidebar)
2. You should see 3 tables:
   - `user_profiles`
   - `appointments`
   - `conversation_summaries`

### Step 4: Get Supabase Credentials

1. Go to **Project Settings** > **API** (gear icon in sidebar)
2. Copy these values (they're already in your `.env.local`):
   - `URL` → SUPABASE_URL
   - `anon public` key → SUPABASE_KEY

---

## Part 2: Tavus Avatar Setup

### Step 1: Create Tavus Account

1. Go to [https://tavus.io](https://tavus.io)
2. Sign up for an account
3. Get your API key from the dashboard

### Step 2: Create a Replica

1. In Tavus dashboard, go to **Replicas**
2. Click **Create Replica**
3. Upload a short video of yourself (or use a stock video)
4. Wait for replica processing (can take a few minutes)
5. Copy the **Replica ID**

### Step 3: Create a Persona (LiveKit Compatible)

You need to create a persona via the Tavus API with specific settings for LiveKit:

```bash
curl --request POST \
  --url https://tavusapi.com/v2/personas \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_TAVUS_API_KEY" \
  -d '{
    "layers": {
        "transport": {
            "transport_type": "livekit"
        }
    },
    "persona_name": "Appointment Assistant",
    "pipeline_mode": "echo"
}'
```

**Replace `YOUR_TAVUS_API_KEY` with your actual Tavus API key.**

The response will include a `persona_id` - copy this value!

### Step 4: Update Environment Variables

Edit `agent-starter-python/.env.local` and add:

```env
TAVUS_REPLICA_ID=your_replica_id_here
TAVUS_PERSONA_ID=your_persona_id_here
```

---

## Part 3: Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd agent-starter-python
```

### Step 2: Install Dependencies

```bash
uv sync
```

This will install all required Python packages including:
- livekit-agents with tavus plugin
- supabase client
- python-dateutil

### Step 3: Verify Environment Variables

Check that your `.env.local` file has all these variables:

```env
# LiveKit
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
LIVEKIT_URL=...

# Supabase
SUPABASE_URL=...
SUPABASE_KEY=...

# AI Services
OPENAI_API_KEY=...
DEEPGRAM_API_KEY=...
CARTESIA_API_KEY=...

# Tavus
TAVUS_API_KEY=...
TAVUS_REPLICA_ID=...
TAVUS_PERSONA_ID=...
```

### Step 4: Download Required Models

```bash
uv run python src/agent.py download-files
```

This downloads:
- Silero VAD model
- LiveKit turn detector model

### Step 5: Test Locally (Optional)

Test the agent in console mode:

```bash
uv run python src/agent.py console
```

You should be able to have a voice conversation with the agent!

---

## Part 4: Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd ../agent-starter-react
```

### Step 2: Install Dependencies

```bash
pnpm install
```

### Step 3: Verify Environment Variables

Check `agent-starter-react/.env.local`:

```env
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
LIVEKIT_URL=...
```

### Step 4: Run Development Server

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Part 5: Local Testing

### Testing the Full Stack

1. **Start the backend agent:**
   ```bash
   cd agent-starter-python
   uv run python src/agent.py dev
   ```

2. **In a new terminal, start the frontend:**
   ```bash
   cd agent-starter-react
   pnpm dev
   ```

3. **Open browser to http://localhost:3000**

4. **Click "Start call"** and test the agent:
   - Give your phone number
   - Ask to book an appointment
   - Try "What appointments do I have?"
   - Try to modify or cancel an appointment
   - Say "goodbye" or "end call" to see the summary

---

## Part 6: Deployment

### Deploy Backend to LiveKit Cloud

1. **Install LiveKit CLI** (if not already installed):
   ```bash
   curl -sSL https://get.livekit.io/cli | bash
   ```

2. **Authenticate with LiveKit Cloud:**
   ```bash
   lk cloud auth
   ```

3. **Configure the agent:**
   ```bash
   cd agent-starter-python
   lk agent config
   ```
   - Select your LiveKit Cloud project
   - Agent ID: `appointment-agent` (or your choice)

4. **Deploy the agent:**
   ```bash
   lk agent deploy
   ```

   This will:
   - Build a Docker container
   - Upload to LiveKit Cloud
   - Deploy with autoscaling
   - Takes 1-2 minutes

5. **View deployment status:**
   ```bash
   lk agent list
   ```

6. **View logs:**
   ```bash
   lk agent logs
   ```

### Deploy Frontend to Vercel

1. **Push code to GitHub:**
   ```bash
   cd agent-starter-react
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create appointment-agent-frontend --public --source=. --remote=origin
   git push -u origin main
   ```

2. **Deploy to Vercel:**
   - Go to [https://vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Configure environment variables:
     - `LIVEKIT_API_KEY`
     - `LIVEKIT_API_SECRET`
     - `LIVEKIT_URL`
   - Click "Deploy"

3. **Access your deployed app:**
   - Vercel will provide a URL (e.g., `https://your-app.vercel.app`)
   - Test the full flow!

---

## Part 7: Verification Checklist

Use this checklist to verify everything is working:

### Database
- [ ] Supabase tables created successfully
- [ ] Can insert test data manually
- [ ] Row Level Security enabled

### Backend
- [ ] All environment variables configured
- [ ] Dependencies installed (`uv sync`)
- [ ] Models downloaded (`download-files`)
- [ ] Agent runs locally (`dev` command)
- [ ] Tavus avatar loads (check logs)

### Frontend
- [ ] Dependencies installed (`pnpm install`)
- [ ] Runs locally (`pnpm dev`)
- [ ] Can connect to LiveKit room
- [ ] Can hear agent speaking

### Integration
- [ ] Can identify user (phone number)
- [ ] Can book appointment
- [ ] Appointment appears in Supabase
- [ ] Can retrieve appointments
- [ ] Can modify appointment
- [ ] Can cancel appointment
- [ ] Summary generated at end
- [ ] Avatar video syncs with speech

### Deployment
- [ ] Backend deployed to LiveKit Cloud
- [ ] Frontend deployed to Vercel
- [ ] Production app works end-to-end

---

## Troubleshooting

### "SUPABASE_URL not found"
- Make sure `.env.local` exists in `agent-starter-python/`
- Check that the file has all required variables
- Restart the agent after updating `.env.local`

### "Tavus avatar failed to load"
- Verify TAVUS_REPLICA_ID and TAVUS_PERSONA_ID are set
- Check that persona was created with `pipeline_mode: echo` and `transport_type: livekit`
- The agent will continue without avatar if it fails (audio-only)

### "Cannot connect to Supabase"
- Verify SUPABASE_KEY is the `anon public` key, not the service role key
- Check your Supabase project is active
- Test connection in Supabase dashboard

### "No audio in frontend"
- Check browser permissions for microphone
- Try a different browser (Chrome/Edge recommended)
- Check that agent is running (`lk agent list`)

### "Import errors in Python"
- Run `uv sync` to install all dependencies
- Make sure you're using Python 3.10-3.13
- Check that you're in the virtual environment

---

## Next Steps

Once everything is working:

1. **Customize the agent:**
   - Edit instructions in `src/agent.py`
   - Modify available time slots in `src/slots_config.json`
   - Add custom tools for your use case

2. **Improve the UI:**
   - Customize colors in `app-config.ts`
   - Add your logo
   - Modify component styles

3. **Add features:**
   - Email confirmations
   - SMS reminders
   - Calendar integration
   - Payment processing

4. **Monitor and iterate:**
   - Check LiveKit Cloud dashboard for metrics
   - Review conversation summaries in Supabase
   - Gather user feedback

---

## Support

- **LiveKit Docs:** https://docs.livekit.io
- **LiveKit Discord:** https://livekit.io/join-slack
- **Supabase Docs:** https://supabase.com/docs
- **Tavus Docs:** https://docs.tavus.io

Good luck with your AI Voice Agent! 🚀
