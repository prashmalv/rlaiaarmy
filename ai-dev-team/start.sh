#!/bin/bash
set -e

echo "🤖 AI Dev Team — Starting..."

# ── Backend ────────────────────────────────────────────────────────────────
if [ ! -f "backend/.env" ]; then
  echo "⚠️  backend/.env not found. Copying from .env.example..."
  cp backend/.env.example backend/.env
  echo "❗ Please set your ANTHROPIC_API_KEY in backend/.env before continuing."
  exit 1
fi

echo "📦 Installing backend dependencies..."
cd backend
/opt/homebrew/bin/python3.13 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q pydantic-settings -r requirements.txt

echo "🚀 Starting FastAPI backend on http://localhost:8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# ── Frontend ───────────────────────────────────────────────────────────────
echo "📦 Installing frontend dependencies..."
cd frontend
npm install --silent

echo "🚀 Starting React frontend on http://localhost:3000..."
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ AI Dev Team is running!"
echo "   Frontend → http://localhost:3000"
echo "   Backend  → http://localhost:8000"
echo "   API Docs → http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services."

wait $BACKEND_PID $FRONTEND_PID
