@echo off
setlocal EnableDelayedExpansion
title Auto Idea Combiner - Build

set "ROOT=%~dp0"
set "FRONTEND=%ROOT%frontend"

echo.
echo  =============================================
echo   Auto Idea Combiner - 本番ビルド
echo  =============================================
echo.

:: ---- 前提ツール確認 ----
for %%t in (uv pnpm cargo) do (
    where %%t >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] %%t が見つかりません。
        pause
        exit /b 1
    )
)

:: ---- バックエンド依存インストール ----
echo [1/3] Pythonバックエンド依存関係を確認中...
cd /d "%ROOT%backend"
uv sync
echo        完了

:: ---- フロントエンド依存インストール ----
echo [2/3] フロントエンド依存関係を確認中...
cd /d "%FRONTEND%"
if not exist "node_modules" pnpm install
echo        完了

:: ---- Tauri本番ビルド ----
echo [3/3] Tauriアプリをビルド中 (数分かかります)...
pnpm tauri build

echo.
echo  =============================================
echo   ビルド完了!
echo   実行ファイル: frontend\src-tauri\target\release\
echo   インストーラー: frontend\src-tauri\target\release\bundle\
echo  =============================================
echo.
pause
