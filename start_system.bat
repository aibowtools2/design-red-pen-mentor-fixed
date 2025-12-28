@echo off
echo Starting Naruhodo Design AI System...

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && call venv\Scripts\activate && uvicorn main:app --reload"

echo Starting Watcher Service...
start "Watcher Service" cmd /k "cd backend && call venv\Scripts\activate && python watcher.py"

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo Opening Dashboard...
timeout /t 5
start http://localhost:5173

echo System Started! 
echo 1. Ensure 'backend/.env' has your GOOGLE_API_KEY.
echo 2. Drop videos into 'watched_videos' folder.
echo 3. Check the dashboard.
pause
