# Quick Start Guide - Resume Data Collection

**Last Update:** December 4, 2025, 3:50 AM

---

## Instant Status Check
```bash
cd "/path/to/repo"
python3 src/collection/check_status.py
```

---

## Resume Collection (Choose One)

### Gemini Already Running?
Check with: `ps aux | grep python | grep gemini`

If running: **Do nothing**, let it continue.
If not running: Run option below.

### Start/Resume Gemini
```bash
cd "/path/to/repo"
python3 src/collection/resume_gemini.py YOUR_GEMINI_API_KEY
```

### Start/Resume Llama (Need API Key First)
Get free key: https://console.groq.com (no credit card)

```bash
cd "/path/to/repo"
python3 src/collection/resume_llama.py YOUR_GROQ_API_KEY_HERE
```

---

## Current Status (as of 3:50 AM Dec 4)

**Gemini:** 69.4% complete, ~26 min remaining, RUNNING NOW
**Llama:** 17.9% complete, NEEDS API KEY to start

---

## Files You Need

- `src/collection/check_status.py` - Check progress
- `src/collection/resume_gemini.py` - Resume Gemini
- `src/collection/resume_llama.py` - Resume Llama
- `docs/internal/RESUME_INSTRUCTIONS.md` - Full details
- `docs/internal/SESSION_SUMMARY.md` - What was done today

---

## That's It!

Everything is automated. Scripts skip existing files. Safe to restart anytime.
