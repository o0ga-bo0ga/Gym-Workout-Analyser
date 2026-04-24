# Gym Workout Analysis

> Your personal AI workout analyst that runs while you sleep.

An automated daily pipeline that fetches your workout from Lyfta, stores it in a database, gets it analyzed by Groq Llama, and slides into your Discord with insights. All on autopilot via GitHub Actions.

No apps to open. No notifications to check. Just wake up and there's your analysis.

---

## The Problem

You're hitting the gym consistently but:
- Haven't looked at your progress in weeks
- Not sure if you're actually getting stronger
- Can't remember what you did last Monday
- Want someone (or something) to tell you what's up

## The Solution

This pipeline does the boring stuff so you don't have to:

1. **Grabs your workout** from Lyfta automatically
2. **Saves it** to your database with all the juicy details
3. **Asks Llama** "what do think?" about your training
4. **Drops the intel** in your Discord

All while you're sleeping. You wake up, check your phone, and boom - here's what went down and what to do next.

---

## How It Works

```
You crush a workout → Lyfta logs it → Pipeline runs at 10PM → 
Llama analyzes it → Discord notifies you → You get better
```

### What It Tracks
- Every workout (chest, back, legs, shoulders, arms)
- Volume, sets, reps going up or down
- Rest days (yes, they're tracked too)
- 28 days of history for context

### What Llama Tells You
- Are you actually following your split?
- Is your volume trending up?
- What's good / what's not
- One actionable tip for next session

---

## Features

| Feature | What's It Do |
|--------|--------------|
| **Auto-fetch** | Grabs today's workout from Lyfta |
| **Database** | PostgreSQL with connection pooling - fast & reliable |
| **LLM Analysis** | Groq Llama 3.1 8B - fast, free, no rate limits |
| **LangSmith** | See your LLM costs & traces at langsmith.app |
| **Discord** | Daily report delivered to your channel |
| **Auto-cleanup** | Deletes data older than 12 months |
| **Retry Logic** | Exponential backoff for flaky APIs |

---

## The Tech Stack

```
Lyfta API → Python → PostgreSQL → Groq Llama → Discord
                ↑
            LangSmith (tracing)
```

* **Python 3.10+**
* **PostgreSQL** (Supabase)
* **Groq** (Llama 3.1 8B - free tier is generous)
* **LangSmith** (free tier)
* **Discord Webhooks** (free)
* **GitHub Actions** (free)

Zero dollars spent. All free tiers.

---

## Setup (5 Minutes)

```bash
# 1. Get these free API keys:
- Lyfta API key (from my.lyfta.app)
- Supabase URL (from supabase.com)
- Groq API key (from console.groq.com)
- Discord webhook (create in Discord server settings)
- LangSmith API key (optional, from langsmith.app)

# 2. Add to GitHub Secrets:
LYFTA_API_KEY
SUPABASE_DATABASE_URL
DISCORD_WEBHOOK_URL
GROQ_API_KEY
LANGSMITH_API_KEY  # optional

# 3. Go to Actions → Daily Workout Pipeline → Run workflow
```

That's it. It runs automatically every night at 10PM IST.

---

## Running Locally

```bash
# Full run with real APIs
GROQ_API_KEY=sk_xxx python src/main.py

# Test run (no external APIs)
LLM_MOCK=true python src/main.py
```

---

## Sample Output

When you crush a workout, Discord shows:

```
🏋️ Workout Report
**Chest + Triceps** — 2026-04-24

1. Relevance: Follows your Monday split perfectly ✓
2. Progression: Volume up 12% vs last chest day
3. Good: Going to failure on bench press
4. Bad: Only 1 tricep exercise - could add pushdowns
5. Next: Add incline fly for better chest activation
```

On rest days:
```
Rest day taken. Recovery is important!
```

---

## Why This Exists

I got tired of:
- Opening apps to check workouts
- Wondering if I'm actually progressing
- Not knowing what to do next
- Paying for coaching when I just wanted simple feedback

So I built a pipeline that does it for free.

---

## What's Next

- [ ] Add my personal tips/tricks as RAG knowledge base
- [ ] Try different models (Llama 4, Qwen)
- [ ] Add weekly/monthly summaries
- [ ] Trend graphs in Discord

Pull requests welcome.

---

## TL;DR

| What | Value |
|------|-------|
| Cost | $0 |
| Daily effort | 0 |
| Setup time | 5 min |
| Coffee needed | 0 |

[Get started →](#setup-5-minutes)