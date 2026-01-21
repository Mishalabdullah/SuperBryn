# Known Limitations

## Tavus Avatar Video

### Free Tier Limitation

**Issue:** Avatar video stops showing after 5 minutes of usage

**Details:**
- Tavus free tier provides only 5 minutes of avatar video generation
- After the 5-minute quota is exhausted, the avatar video will not be displayed
- The voice agent will continue to work normally without visual avatar
- Audio and all other features remain fully functional

**Workaround:**
- Voice conversations work perfectly without the avatar
- Upgrade to Tavus paid tier for unlimited avatar video

**Status:** Known limitation of Tavus free tier

---

## Tool Call Latency

### Deployment Region Differences

**Issue:** Tool calls may take longer on deployed version compared to local development

**Details:**
- Frontend and LiveKit Cloud may be hosted in different geographical regions
- Network latency between regions can add 100-500ms per tool call
- RPC (Remote Procedure Call) communication between frontend and agent is affected by distance
- Multiple tool calls in sequence can compound the delay

**Expected Behavior:**
- **Local Development:** Near-instant tool call responses (<100ms)
- **Deployed (Different Regions):** 200-800ms additional latency per tool call
- **Same Region Deployment:** Minimal additional latency

**Impact:**
- Slight delay when displaying tool call updates in UI
- Appointment booking, slot fetching, and other operations may feel slower
- Overall conversation flow remains natural

**Mitigation:**
- Deploy frontend and LiveKit Cloud agent in the same region when possible
- Use CDN or edge deployment for frontend
- Optimize tool calls to batch operations where possible

**Status:** Expected behavior due to geographical distribution

---

**Last Updated:** January 21, 2026
