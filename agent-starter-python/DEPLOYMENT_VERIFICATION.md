# Agent Deployment Verification Guide

This guide shows you how to verify that your LiveKit agent has been successfully updated and deployed.

## Quick Verification Methods

### Method 1: Check Agent Status (Fastest)

```bash
cd /home/mishal/Documents/code/suprbryn/agent-starter-python
lk agent status
```

**What to verify:**
- ✅ **Version** should show a recent timestamp (format: vYYYYMMDDHHMMSS)
- ✅ **Status** should be "Running"
- ✅ **Deployed At** should match your deployment time
- ✅ **Replicas** should show active instances (e.g., "1 / 1 / 1")

**Example output:**
```
┌─────────────────┬─────────────────┬────────────┬─────────┬───────────┬──────────────────────┐
│ ID              │ Version         │ Region     │ Status  │ Replicas  │ Deployed At          │
├─────────────────┼─────────────────┼────────────┼─────────┼───────────┼──────────────────────┤
│ CA_TJct85qxX5YE │ v20260121090000 │ eu-central │ Running │ 1 / 1 / 1 │ 2026-01-21T09:00:00Z │
└─────────────────┴─────────────────┴────────────┴─────────┴───────────┴──────────────────────┘
```

---

### Method 2: Run Automated Verification Script

```bash
cd /home/mishal/Documents/code/suprbryn/agent-starter-python
./verify-deployment.sh
```

This script checks:
- Agent status
- Recent deployment logs
- Build history

---

### Method 3: Check Deployment Logs

```bash
# View live logs
lk agent logs

# View last 50 lines
lk agent logs --tail 50
```

**What to look for in logs:**
- ✅ `🚀 Starting appointment assistant agent v1.1.0-slots-fix` (shows version)
- ✅ `Generated {number} available slots` (shows slot generation is working)
- ✅ Recent timestamps (shows agent is running fresh code)
- ❌ No error messages about missing config or files

---

### Method 4: Test Locally Before Deploying

```bash
cd /home/mishal/Documents/code/suprbryn/agent-starter-python
./test-slots-locally.sh
```

This verifies:
- Slots configuration is correct
- Lunch break is excluded (no 12:00, 12:30 slots)
- Weekends are excluded
- 20 slots are being generated

---

### Method 5: LiveKit Cloud Dashboard

1. Open: https://cloud.livekit.io/projects/p_/agents
2. Navigate to: **Agents** tab
3. Find your agent: **CA_TJct85qxX5YE**
4. Verify:
   - ✅ Status: "Running"
   - ✅ Recent deployment timestamp
   - ✅ Active instances

---

### Method 6: End-to-End Test (Most Reliable)

**Connect to your agent and test:**

1. Open your agent frontend or playground
2. Say: **"What appointment slots are available?"**
3. Verify the response includes:
   - ✅ **~20 slots** (not just 10)
   - ✅ **Multiple days** (today + tomorrow)
   - ✅ **No lunch slots** (no 12:00 PM or 12:30 PM mentioned)
   - ✅ **Slots jump from 11:30 AM to 2:00 PM** (lunch break)
   - ✅ **Only weekdays** (no Saturday/Sunday)

**Example expected output:**
```
"I have 20 available slots to show you. Here are the options:
- Wednesday, January 21 at 10:30 AM
- Wednesday, January 21 at 11:00 AM
- Wednesday, January 21 at 11:30 AM
- Wednesday, January 21 at 2:00 PM    ← Note: jumps from 11:30 AM
- Wednesday, January 21 at 2:30 PM
...
- Thursday, January 22 at 9:00 AM     ← Next day included
- Thursday, January 22 at 9:30 AM
..."
```

---

## Troubleshooting

### Issue: Old version showing in logs

**Solution:**
```bash
# Redeploy
lk agent deploy

# Wait 1-2 minutes for rolling deployment
# Then check status again
lk agent status
```

### Issue: No slots showing or error in logs

**Check:**
1. Verify `slots_config.json` is correct (no 12:00, 12:30)
2. Check database connectivity (Supabase secrets set correctly)
3. Verify environment variables are set in LiveKit Cloud:
   ```bash
   lk agent secret list
   ```

### Issue: Still seeing lunch break slots

**Verify locally first:**
```bash
./test-slots-locally.sh
```

If local test passes but deployed agent still shows lunch slots:
- Old code is deployed → redeploy with `lk agent deploy`
- Cache issue → wait 2-3 minutes for rolling deployment to complete

---

## Deployment Checklist

Before marking deployment as successful, verify:

- [ ] `lk agent status` shows recent deployment timestamp
- [ ] `lk agent status` shows "Running" status
- [ ] `lk agent logs` shows version `v1.1.0-slots-fix`
- [ ] `lk agent logs` shows no errors
- [ ] Test conversation shows 20 slots (not 10)
- [ ] Test conversation shows multiple days
- [ ] Test conversation excludes lunch (11:30 AM → 2:00 PM)
- [ ] Test conversation excludes weekends

---

## Quick Reference Commands

```bash
# Deploy new version
lk agent deploy

# Check status
lk agent status

# View logs
lk agent logs

# List recent builds
lk agent builds

# Rollback if needed
lk agent rollback

# Test locally
./test-slots-locally.sh

# Full verification
./verify-deployment.sh
```

---

## Current Configuration

**Agent ID:** CA_TJct85qxX5YE  
**Project:** test-zflb2pcs  
**Region:** eu-central  
**Version:** v1.1.0-slots-fix  

**Changes in this version:**
- ✅ Increased slots from 10 to 20
- ✅ Excluded lunch break (12:00, 12:30)
- ✅ Fixed slot availability across multiple days
- ✅ Removed duplicate code in fetch_slots

---

## Support

If issues persist:
1. Check LiveKit Cloud dashboard for errors
2. Review full logs: `lk agent logs --tail 200`
3. Verify all secrets are set: `lk agent secret list`
4. Check build logs: `lk agent builds`
