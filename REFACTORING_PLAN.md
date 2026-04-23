# Refactoring Plan: Gym Workout Analyzer

## Goal
Refactor with solid principles + automated tests, without changing core purpose.

---

## 1. File Renaming (Descriptive Functionality)

| Current | New |
|---------|-----|
| `phase1.py` | `data_fetch.py` |
| `phase2.py` | `persistence.py` |
| `phase3.py` | `analysis_prep.py` |
| `db.py` | `database.py` |
| `lyfta.py` | `lyfta_client.py` |
| `transform.py` | `workout_transformer.py` |
| `discord.py` | `discord_client.py` |
| `gemini.py` | `gemini_client.py` |

---

## 2. Function Naming (verb_object pattern)

| Current | New |
|---------|-----|
| `log_rest_day()` | `save_rest_day()` |
| `log_workout()` | `save_workout()` |
| `init_db()` | `initialize_database()` |
| `fetch_today()` | `fetch_today_workout()` |
| `get_todays_workout()` | `fetch_todays_workout()` |
| `enforce_retention()` | `enforce_data_retention()` |

---

## 3. Fix Unused Functionality

**Connect `analysis_prep.py` to LLM:**
```python
# In main.py - when analysis enabled on workout day:
history_21_days = summarize_last_21_days()  # from phase3
analysis = analyze_workout(workout, history_21_days)
```

**Fix `GEMINI_MODE` config** - remove misleading comment about "real"/"mock"

---

## 4. Resilience Patterns

Add retry with exponential backoff to all external clients:
- Lyfta: 3 retries (2s, 4s, 8s)
- Gemini: 3 retries + handle 429
- Discord: 3 retries + handle 5xx

New files: `src/utils/retry.py`

---

## 5. Code Quality Fixes

- Remove hardcoded insult at `main.py:42`
- Fix SQL injection in `database.py` (retention query)
- Remove empty `src/agents/` directory
- Remove unused `json` import in `db.py`

---

## 6. Testing Strategy

Create:
```
tests/
├── conftest.py          # fixtures
├── unit/
│   ├── test_workout_transformer.py
│   ├── test_database.py
│   └── test_config.py
└── integration/
    ├── test_pipeline.py
```

**Coverage goals:**
- `workout_transformer.py`: 100%
- `config.py`: 100%
- Core pipeline: 80%

---

## 7. Implementation Order

| Phase | Tasks |
|-------|-------|
| 1 | Rename files + refactor function names |
| 2 | Connect `summarize_last_21_days()` to LLM flow |
| 3 | Add retry decorator |
| 4 | Write tests (~35 tests) |
| 5 | Cleanup + final review |

---

## 8. Decisions Needed

1. **Empty `src/agents/`** - remove it?
2. **Hardcoded insult** (`main.py:42`) - replace with config or remove?