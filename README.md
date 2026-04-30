# 💪 Gym Workout Analysis

[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)

> *Your personal AI workout analyst that runs while you sleep.*

---

An automated daily pipeline that fetches your workout from Lyfta 📱, stores it in a database 💾, gets it analyzed by Groq Llama 🧠, and slides into your Discord 💬 with insights.

**Zero apps to open. Zero notifications to check. Wake up and boom 💥 - here's your analysis.**

---

## 😤 The Problem

You're hitting the gym hard but:

- Haven't looked at your progress in weeks 📉
- Not sure if you're actually getting stronger 💪
- Can't remember what you did last Monday 🤔
- Want someone to tell you what's up 👀

## 🎯 The Solution

This pipeline does the boring stuff so you don't have to:

```
📱 Lyfta      💾 Database      🧠 Groq Llama      💬 Discord
   │              │              │               │
   ▼              ▼              ▼               ▼
You crush  →  Pipeline runs  →  Analyzes it   →  Intel in
a workout     at 10PM          overnight       Discord
```

**What you get:**
- ✅ Every workout logged automatically
- ✅ Volume tracking (up/down/flat)
- ✅ Rest days tracked too 😴
- ✅ 28 days of history for context
- ✅ Actionable tips for next session

---

## 🚀 Features

| Feature | What It Does |
|:-------:|:-----------|
| 📥 **Auto-fetch** | Grabs today's workout from Lyfta |
| 💾 **Database** | PostgreSQL with pooling - ⚡ fast |
| 🧠 **LLM** | Groq Llama 3.1 8B - free & blazing fast |
| 📊 **LangSmith** | See costs & traces at langsmith.app |
| 💬 **Discord** | Daily report in your channel |
| 🧹 **Auto-cleanup** | Nukes data older than 12 months |
| 🔄 **Retry** | Exponential backoff - no panic |

---

## 🛠️ The Tech Stack

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Lyfta     │ ──▶ │   Python    │ ──▶ │   Groq      │ ──▶ │  Discord    │
│    API     │     │     3.10+   │     │   Llama 3.1 │     │  Webhook    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                            │                   │
                            ▼                   ▼
                     ┌─────────────┐     ┌─────────────┐
                     │ PostgreSQL  │     │ LangSmith   │ (optional)
                     │  Supabase   │     │   Tracing   │
                     └─────────────┘     └─────────────┘
```

- **$0** - All free tiers. No credit card needed.
- **5 min** - Setup time
- **0 daily effort** - It just runs 🚀

---

## ⚡ Quick Setup

```bash
# Get these free keys:
📱 Lyfta        → my.lyfta.app
💾 Supabase    → supabase.com
🧠 Groq        → console.groq.com  
💬 Discord     → Server Settings → Integrations → Webhooks
📊 LangSmith   → langsmith.app (optional)
```

```bash
# Add to GitHub Secrets:
LYFTA_API_KEY
SUPABASE_DATABASE_URL
DISCORD_WEBHOOK_URL
GROQ_API_KEY
LANGSMITH_API_KEY     # optional
```

**Done.** Pipeline runs automatically at **10PM IST** every night.

---

## 🏃‍♂️ Run Locally

```bash
# Full run - real APIs
GROQ_API_KEY=sk_xxx python src/main.py

# Test run - no external calls
LLM_MOCK=true python src/main.py
```

---

## 📱 Sample Output

### After a Chest Day 💪:
```
����️ Workout Report
━━━━━━━━━━━━━━━━━━━━━━
📅 Chest + Triceps • 2026-04-24
━━━━━━━━━━━━━━━━━━━━━━

✅ 1. Relevance: Follows your Monday split 
✅ 2. Progression: +12% volume vs last chest day
✅ 3. Good: Going to failure on bench 
⚠️ 4. Bad: Only 1 tricep exercise

💡 Next: Incline fly for better chest activation
```

### Rest Day 😴:
```
😴 Rest day taken. Recovery is important!
```

---

## 📊 LangSmith Dashboard

When you enable LangSmith, you get:

- 💵 **Cost tracking** - Pennies per month
- ⏱️ **Latency** - Always < 1 second with Groq
- 📝 **Traces** - Every prompt/response logged

🔗 [View at langsmith.app](https://langsmith.app)

---

## 🤔 Why This Exists

| Before | After |
|:-------|:------|
| Open apps to check workouts | Wakes up to Discord notification |
| Wondering "am I progressing?" | Volume trends tracked |
| No idea what to do next | One actionable tip delivered |
| Paying for coaching | Free forever |

---

## 🔮 What's Next

- [ ] RAG knowledge base with your tips/tricks
- [ ] Try Llama 4 or Qwen models
- [ ] Weekly summary generation
- [ ] Trend charts in Discord

⭐ Star it if it helps. PRs welcome.

---

## 📋 TL;DR

| Metric | Value |
|:-------|:------|
| 💰 Cost | Free |
| ⏰ Daily effort | 0 min |
| ⏱️ Setup time | 5 min |
| ☕ Coffee needed | 0 |

**Ready?** → [Jump to ⚡ Quick Setup](#⚡-quick-setup)