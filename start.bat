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
echo   Auto Idea Combiner - 起動中...
echo  =============================================
echo.

:: ---- 前提ツール確認 ----
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] uv が見つかりません。
    echo         https://docs.astral.sh/uv/ からインストールしてください。
    pause
    exit /b 1
)

where pnpm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pnpm が見つかりません。
    echo         npm install -g pnpm を実行してください。
    pause
    exit /b 1
)

:: ---- .env 確認 ----
if not exist "%ROOT%.env" (
    echo [INFO] .env が見つかりません。.env.example からコピーします...
    copy "%ROOT%.env.example" "%ROOT%.env" >nul
    echo [WARN] .env を開いてAPIキーを設定してください。
    notepad "%ROOT%.env"
)

:: ---- バックエンド起動 ----
echo [1/3] Pythonバックエンドを起動中 (port %BACKEND_PORT%)...
cd /d "%BACKEND%"
start "AIC-Backend" /min cmd /c "uv run uvicorn main:app --port %BACKEND_PORT% 2>&1 | tee ..\backend.log"

:: ---- バックエンド起動待ち ----
echo [2/3] バックエンドの起動を待っています...
set /a RETRY=0
:WAIT_LOOP
timeout /t 2 /nobreak >nul
curl -s "http://localhost:%BACKEND_PORT%/api/health" >nul 2>&1
if %errorlevel% equ 0 goto BACKEND_READY
set /a RETRY+=1
if %RETRY% geq 15 (
    echo [ERROR] バックエンドの起動がタイムアウトしました。
    echo         backend.log を確認してください。
    pause
    exit /b 1
)
goto WAIT_LOOP

:BACKEND_READY
echo        バックエンド起動完了!

:: ---- フロントエンド起動 ----
echo [3/3] フロントエンドを起動中...
cd /d "%FRONTEND%"

:: node_modules がなければインストール
if not exist "node_modules" (
    echo        依存関係をインストール中 (初回のみ)...
    pnpm install
)

:: Tauri ビルド済みか確認 → あれば実行ファイル起動、なければ dev モード
if exist "src-tauri\target\release\auto-idea-combiner.exe" (
    echo        ビルド済み実行ファイルを起動します。
    start "" "src-tauri\target\release\auto-idea-combiner.exe"
) else (
    echo        開発モードで起動します (pnpm tauri dev)
    echo        初回はRustのコンパイルに数分かかります...
    start "AIC-Frontend" cmd /c "pnpm tauri dev"
)

echo.
echo  =============================================
echo   起動完了!
echo   バックエンド: http://localhost:%BACKEND_PORT%
echo   フロントエンド: http://localhost:%FRONTEND_PORT%
echo  =============================================
echo.
echo  終了するには、このウィンドウを閉じてください。
echo  (バックエンドとフロントエンドのウィンドウも閉じてください)
echo.
pause
