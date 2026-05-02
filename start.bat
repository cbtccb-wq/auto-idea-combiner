@echo off
setlocal EnableExtensions
title Auto Idea Combiner

set "ROOT=%~dp0"
set "BACK=%ROOT%backend"
set "FRONT=%ROOT%frontend"
set "BACKEND_PORT=8765"
set "FRONTEND_PORT=1420"
set "BACKEND_URL=http://127.0.0.1:%BACKEND_PORT%/api/health"
set "FRONTEND_URL=http://127.0.0.1:%FRONTEND_PORT%/"
set "FRONTEND_BROWSER_URL=http://localhost:%FRONTEND_PORT%/"
set "BACKEND_LOG=%ROOT%backend.log"
set "FRONTEND_LOG=%ROOT%frontend.log"

echo.
echo  =============================================
echo   Auto Idea Combiner - Starting...
echo  =============================================
echo.

where uv >nul 2>&1
if errorlevel 1 (
    echo [ERROR] uv not found. Install: https://docs.astral.sh/uv/
    pause
    exit /b 1
)

where pnpm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pnpm not found. Install: npm install -g pnpm
    pause
    exit /b 1
)

if not exist "%ROOT%.env" (
    copy "%ROOT%.env.example" "%ROOT%.env" >nul
    echo [WARN] .env created. Set your API key.
    notepad "%ROOT%.env"
)

if exist "%BACKEND_LOG%" del /q "%BACKEND_LOG%" >nul 2>&1
if exist "%FRONTEND_LOG%" del /q "%FRONTEND_LOG%" >nul 2>&1

echo [0/3] Cleaning up stale processes...
call :kill_port %BACKEND_PORT%
call :kill_port %FRONTEND_PORT%

echo [1/3] Starting backend on port %BACKEND_PORT%...
start "AIC-Backend" cmd /k "cd /d ""%BACK%"" && uv run uvicorn main:app --port %BACKEND_PORT%"

echo [2/3] Waiting for backend (first run may take several minutes)...
call :wait_for_url "%BACKEND_URL%" 120 3 "backend" "%BACKEND_LOG%"
if errorlevel 1 exit /b 1

echo [3/3] Starting frontend on port %FRONTEND_PORT%...
cd /d "%FRONT%"
if not exist "node_modules" (
    echo        Installing node_modules...
    call pnpm install
    if errorlevel 1 (
        echo [ERROR] pnpm install failed.
        pause
        exit /b 1
    )
)

start "AIC-Frontend" cmd /k "cd /d ""%FRONT%"" && pnpm dev"

echo        Waiting for frontend...
call :wait_for_url "%FRONTEND_URL%" 45 2 "frontend" "%FRONTEND_LOG%"
if errorlevel 1 exit /b 1

echo        Opening browser...
start "" "%FRONTEND_BROWSER_URL%"

echo.
echo  =============================================
echo   Started!
echo   Backend:  http://127.0.0.1:%BACKEND_PORT%
echo   Frontend: %FRONTEND_BROWSER_URL%
echo  Logs:
echo     %BACKEND_LOG%
echo     %FRONTEND_LOG%
echo  =============================================
echo.
echo  Close AIC-Backend and AIC-Frontend windows to stop.
echo.
pause
exit /b 0

:kill_port
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":%~1 "') do (
    if "%%a" NEQ "0" taskkill /F /PID %%a >nul 2>&1
)
exit /b 0

:wait_for_url
setlocal
set "URL=%~1"
set /a MAX_RETRIES=%~2
set /a SLEEP_SEC=%~3
set "LABEL=%~4"
set "LOG=%~5"
set /a RETRY=0

:wait_loop
powershell -NoLogo -NoProfile -Command ^
    "try { $response = Invoke-WebRequest -UseBasicParsing -Uri '%URL%' -TimeoutSec 2; if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) { exit 0 } exit 1 } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 (
    echo        %LABEL% ready!
    endlocal & exit /b 0
)

set /a RETRY+=1
if %RETRY% geq %MAX_RETRIES% (
    echo [ERROR] %LABEL% did not become ready in time.
    call :show_log_tail "%LOG%"
    pause
    endlocal & exit /b 1
)

echo        Waiting for %LABEL%... (%RETRY%/%MAX_RETRIES%)
%SystemRoot%\System32\timeout.exe /t %SLEEP_SEC% /nobreak >nul
goto wait_loop

:show_log_tail
if exist "%~1" (
    echo         Last log lines from %~1
    powershell -NoLogo -NoProfile -Command "Get-Content -Path '%~1' -Tail 30"
) else (
    echo         Log file not found yet: %~1
)
exit /b 0
