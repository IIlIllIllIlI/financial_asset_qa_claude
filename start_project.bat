@echo off
echo ============================================
echo  Financial Asset QA System - Startup Script
echo ============================================
echo.

REM Check .env file
if not exist ".env" (
    echo [WARN] .env file not found at project root
    echo Please copy .env.example to .env and fill in your API keys
    echo Or copy from docs/.env if it exists
    if exist "docs\.env" (
        echo [INFO] Copying docs/.env to project root...
        copy "docs\.env" ".env" >nul
        echo [OK] .env copied
    )
)

echo [1/5] Setting up backend virtual environment...
if not exist "backend\venv" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    echo [OK] Virtual environment created
    cd ..
) else (
    echo [OK] Virtual environment already exists
)

echo.
echo [2/5] Installing backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
echo [OK] Backend dependencies installed
cd ..

echo.
echo [3/5] Installing frontend dependencies...
cd frontend
call npm install --silent 2>nul
echo [OK] Frontend dependencies installed
cd ..

echo.
echo [4/5] Starting FastAPI backend on port 8000...
start "Backend - FastAPI" cmd /c "cd backend && venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo [5/5] Starting Next.js frontend on port 3000...
start "Frontend - Next.js" cmd /c "cd frontend && npm run dev"

echo.
echo ============================================
echo  System is starting up...
echo  Frontend: http://localhost:3000
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo ============================================
echo.
echo Open http://localhost:3000 in your browser.
pause
