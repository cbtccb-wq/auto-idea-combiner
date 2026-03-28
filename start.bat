@echo off
setlocal EnableDelayedExpansion
title Auto Idea Combiner

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "BACKEND_PORT=8765"

echo.
echo  =============================================
echo   Auto Idea Combiner - Starting...
echo  =============================================
echo.

:: Check uv
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] uv not found.
    echo         Install: https://docs.astral.sh/uv/
    pause
    exit /b 1
)

:: Check pnpm
where pnpm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pnpm not found.
    echo         Install: npm install -g pnpm
    pause
    exit /b 1
)

:: Copy .env if missing
if not exist "%ROOT%.env" (
    echo [INFO] .env not found. Copying from .env.example...
    copy "%ROOT%.env.example" "%ROOT%.env" >nul
    echo [WARN] Please set your API key in .env
    notepad "%ROOT%.env"
)

:: Start backend
echo [1/3] Starting Python backend (port %BACKEND_PORT%)...
cd /d "%BACKEND%"
start "AIC-Backend" /min cmd /c "uv run uvicorn main:app --port %BACKEND_PORT%"

:: Wait for backend
echo [2/3] Waiting for backend...
set /a RETRY=0
:WAIT_LOOP
timeout /t 2 /nobreak >nul
curl -s "http://localhost:%BACKEND_PORT%/api/health" >nul 2>&1
if %errorlevel% equ 0 goto BACKEND_READY
set /a RETRY+=1
if %RETRY% geq 15 (
    echo [ERROR] Backend startup timed out. Check backend.log
    pause
    exit /b 1
)
goto WAIT_LOOP

:BACKEND_READY
echo        Backend ready!

:: Start frontend
echo [3/3] Starting frontend...
cd /d "%FRONTEND%"

if not exist "node_modules" (
    echo        Installing dependencies (first time only)...
    pnpm install
)

if exist "src-tauri\target\release\auto-idea-combiner.exe" (
    start "" "src-tauri\target\release\auto-idea-combiner.exe"
) else (
    echo        Running in dev mode (first run compiles Rust, takes a few minutes)...
    start "AIC-Frontend" cmd /c "pnpm tauri dev"
)

echo.
echo  =============================================
echo   Started!
echo   Backend:  http://localhost:%BACKEND_PORT%
echo   Frontend: http://localhost:1420
echo  =============================================
echo.
echo  Close this window to stop the backend.
echo.
pause
