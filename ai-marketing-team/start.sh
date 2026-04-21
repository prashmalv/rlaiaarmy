#!/bin/bash
set -e

echo "🚀 RightLeftAI Marketing Team — Starting..."

if [ ! -f "backend/.env" ]; then
  cp backend/.env.example backend/.env
  echo "⚠️  Set your ANTHROPIC_API_KEY in backend/.env then re-run."
  exit 1
fi

cd backend
source .venv/bin/activate
echo "▶  Backend starting on http://localhost:8001"
uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
cd ..

cd frontend
echo "▶  Frontend starting on http://localhost:3001"
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ RightLeftAI Marketing Team is live!"
echo "   Dashboard  → http://localhost:3001"
echo "   API Docs   → http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop."
wait $BACKEND_PID $FRONTEND_PID
