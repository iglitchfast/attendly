# Attendly

Answers one question: **"Can I skip today's class(es) without dropping
below my required attendance %?"**

Calendar-driven — you enter a one-time baseline (from whatever attendance
app you already use) plus your weekly timetable and semester dates. The
app calculates conducted/remaining classes per subject going forward, so
you're not manually updating counts all semester.

## Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, JWT auth (pbkdf2_sha256
  hashing — not bcrypt, see gotchas below)
- **Frontend**: Plain HTML/CSS/JS. No framework, no build step, no npm.

## Running it

```bash
# Backend
cd attendly/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# http://localhost:8000

# Frontend (separate terminal)
cd attendly/frontend
python3 -m http.server 3000
# open http://localhost:3000/login.html
```

## Flow

1. `login.html` — register or log in, JWT stored in `localStorage`
2. `setup.html` — semester start/end dates, working-day flags, baseline
   attendance per subject
3. `timetable.html` — assign a subject to each day × period slot
4. `dashboard.html` — subject cards with live %, safe-skip counts
5. `today.html` — today's specific classes, Can Skip: YES / NO / RISKY

## Known gotchas (don't re-debug these)

- Password hashing **must** use `pbkdf2_sha256`, not `bcrypt` — bcrypt has
  a passlib version-compatibility bug on this setup.
- SQLite file (`attendly.db`) auto-creates in `backend/` on first run.
  Safe to delete and restart fresh during development.
- Frontend deliberately has no npm/build step/framework. Don't reintroduce
  Next.js/React/Tailwind.
- `python-multipart` is required in `requirements.txt` even though login
  uses JSON bodies — FastAPI's OAuth2 scheme needs it under the hood.

## Not yet wired up

- `PATCH /me/settings` route for saving semester_start/semester_end/
  saturday_working/sunday_working from `setup.html` — schema
  (`UserSettingsUpdate`) exists in `schemas.py` but no route uses it yet.
  `setup.js` currently only saves subjects, not these fields.
- Holiday/working-day-override management UI (backend routes exist in
  `routers/holidays.py`, no frontend page yet).
- "Mark a specific class as missed" — the calendar engine currently
  assumes full attendance since the baseline date; there's no way yet
  to record a skip after the fact and have it count against `attended`.