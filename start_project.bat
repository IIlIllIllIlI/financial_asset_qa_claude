@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo   Financial Asset QA System - Startup
echo ============================================
echo.

REM --- .env check ---
if not exist ".env" (
    echo [WARN] .env not found at project root
    if exist "docs\.env" (
        echo [INFO] Copying docs\.env to project root...
        copy "docs\.env" ".env" >nul
        echo [OK]  .env copied from docs\.env
    ) else (
        echo [ERROR] No .env found. Create one with MINIMAX_API_KEY and TAVILY_API_KEY.
    )
) else (
    echo [OK]  .env found
)

echo.

REM --- Kill conflicting port processes ---
call :kill_port 8000
call :kill_port 3000
echo.

REM --- [1/5] Backend venv ---
echo [1/5] Backend virtual environment...
if not exist "backend\venv" (
    echo [INFO] Creating venv...
    cd backend
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        cd ..
        goto :error_end
    )
    cd ..
    echo [OK]  venv created
) else (
    echo [OK]  venv exists
)

REM --- [2/5] Backend deps ---
echo.
echo [2/5] Backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] pip install failed
    cd ..
    goto :error_end
)
echo [OK]  Backend dependencies installed
cd ..

REM --- [3/5] Frontend deps ---
echo.
echo [3/5] Frontend dependencies...
cd frontend
call npm install --silent 2>nul
echo [OK]  Frontend dependencies installed
cd ..

REM --- [4/5] Start Backend ---
echo.
echo [4/5] Starting backend on port 8000...
start "Backend - FastAPI" cmd /k "cd /d %cd%\backend && call venv\Scripts\activate.bat && echo Backend starting on http://localhost:8000 ... && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo [OK]  Backend window opened

REM --- [5/5] Start Frontend ---
echo.
echo [5/5] Starting frontend on port 3000...
start "Frontend - Next.js" cmd /k "cd /d %cd%\frontend && echo Frontend starting on http://localhost:3000 ... && npm run dev"
echo [OK]  Frontend window opened

REM --- Done ---
echo.
echo ============================================
echo   Frontend : http://localhost:3000
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo ============================================
echo.
echo Press any key to close this window (services keep running)
pause >nul
exit /b 0

REM ===============================
REM ===  kill_port subroutine  ====
REM ===============================
:kill_port
set "port=%~1"
powershell -Command "$p = Get-NetTCPConnection -LocalPort %port% -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1; if ($p) { Stop-Process -Id $p -Force; Write-Host '[WARN] Port %port% was occupied by PID' $p '- killed' } else { Write-Host '[OK]  Port %port% available' }"
timeout /t 1 /nobreak >nul
exit /b

REM ===============================
REM ===  error fallback  ==========
REM ===============================
:error_end
echo.
echo ============================================
echo   Startup FAILED - see errors above.
echo ============================================
pause >nul
exit /b 1
