#!/bin/bash
# setup_attendly.sh
# Wipes any existing attendly/ folder and scaffolds the fresh project structure.
# Run this from wherever you want the attendly/ folder to live.

set -e

PROJECT_DIR="attendly"

echo "Removing existing $PROJECT_DIR (if present)..."
rm -rf "$PROJECT_DIR"

echo "Creating fresh structure..."

# --- Backend ---
mkdir -p "$PROJECT_DIR/backend/routers"

touch "$PROJECT_DIR/backend/main.py"
touch "$PROJECT_DIR/backend/database.py"
touch "$PROJECT_DIR/backend/models.py"
touch "$PROJECT_DIR/backend/schemas.py"
touch "$PROJECT_DIR/backend/auth.py"
touch "$PROJECT_DIR/backend/attendance_engine.py"
touch "$PROJECT_DIR/backend/calendar_engine.py"
touch "$PROJECT_DIR/backend/requirements.txt"
touch "$PROJECT_DIR/backend/.env"

touch "$PROJECT_DIR/backend/routers/__init__.py"
touch "$PROJECT_DIR/backend/routers/auth_routes.py"
touch "$PROJECT_DIR/backend/routers/subjects.py"
touch "$PROJECT_DIR/backend/routers/timetable.py"
touch "$PROJECT_DIR/backend/routers/holidays.py"
touch "$PROJECT_DIR/backend/routers/predictions.py"

# --- Frontend ---
mkdir -p "$PROJECT_DIR/frontend/css"
mkdir -p "$PROJECT_DIR/frontend/js"

touch "$PROJECT_DIR/frontend/login.html"
touch "$PROJECT_DIR/frontend/setup.html"
touch "$PROJECT_DIR/frontend/timetable.html"
touch "$PROJECT_DIR/frontend/dashboard.html"
touch "$PROJECT_DIR/frontend/today.html"

touch "$PROJECT_DIR/frontend/css/style.css"

touch "$PROJECT_DIR/frontend/js/api.js"
touch "$PROJECT_DIR/frontend/js/attendance-math.js"
touch "$PROJECT_DIR/frontend/js/login.js"
touch "$PROJECT_DIR/frontend/js/setup.js"
touch "$PROJECT_DIR/frontend/js/timetable.js"
touch "$PROJECT_DIR/frontend/js/dashboard.js"
touch "$PROJECT_DIR/frontend/js/today.js"

# --- Root ---
touch "$PROJECT_DIR/README.md"

echo "Done. Structure created:"
find "$PROJECT_DIR" -not -path '*/venv/*' | sort
