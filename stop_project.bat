@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo   Stopping Financial Asset QA System
echo ============================================
echo.

call :stop_port 8000
call :stop_port 3000

echo.
echo ============================================
echo   All services stopped.
echo ============================================
pause >nul
exit /b 0

:stop_port
set "port=%~1"

powershell -Command "$p = Get-NetTCPConnection -LocalPort %port% -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1; if ($p) { Stop-Process -Id $p -Force; Write-Host '[OK]  Port %port% freed (PID' $p ')' } else { Write-Host '[OK]  Port %port% already free' }"
exit /b
