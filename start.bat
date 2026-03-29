@echo off
setlocal EnableDelayedExpansion
title Auto Idea Combiner

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "BACKEND_PORT=8765"
set "FRONTEND_PORT=1420"

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

:: [1/3] Start backend
echo [1/3] Starting Python backend (port %BACKEND_PORT%)...
cd /d "%BACKEND%"
start "AIC-Backend" cmd /c "uv run uvicorn main:app --port %BACKEND_PORT%"

:: Wait for backend health check
echo [2/3] Waiting for backend (max 3 min, loading AI model on first run)...
set /a RETRY=0
:WAIT_LOOP
timeout /t 3 /nobreak >nul
curl -s "http://localhost:%BACKEND_PORT%/api/health" 2>nul | findstr "ok" >nul
if %errorlevel% equ 0 goto BACKEND_READY
set /a RETRY+=1
if %RETRY% geq 60 (
    echo [ERROR] Backend startup timed out.
    echo         Check the AIC-Backend window for errors.
    pause
    exit /b 1
)
echo        Still loading... (%RETRY%/60)
goto WAIT_LOOP

:BACKEND_READY
echo        Backend ready!

:: [3/3] Start frontend
echo [3/3] Starting frontend...
cd /d "%FRONTEND%"

if not exist "node_modules" (
    echo        Installing node_modules (first time, takes 1-2 min)...
    call pnpm install
    if %errorlevel% neq 0 (
        echo [ERROR] pnpm install failed.
        pause
        exit /b 1
    )
)

start "AIC-Frontend" cmd /c "pnpm dev"

:: Wait for frontend to be ready (up to 60 seconds)
echo        Waiting for frontend to start...
set /a FRETRY=0
:FRONT_WAIT
timeout /t 2 /nobreak >nul
curl -s "http://localhost:%FRONTEND_PORT%" >nul 2>&1
if %errorlevel% equ 0 goto FRONT_READY
set /a FRETRY+=1
if %FRETRY% geq 30 (
    echo        Frontend check timed out, opening anyway...
    goto FRONT_READY
)
goto FRONT_WAIT

:FRONT_READY
echo        Opening browser...
start "" "http://localhost:%FRONTEND_PORT%"

echo.
echo  =============================================
echo   Started!
echo   Backend:  http://localhost:%BACKEND_PORT%
echo   Frontend: http://localhost:%FRONTEND_PORT%
echo  =============================================
echo.
echo  Keep this window open (or close it - processes run independently).
echo.
pause
