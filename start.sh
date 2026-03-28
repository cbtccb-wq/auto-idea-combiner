#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
BACKEND_PORT=8765
FRONTEND_PORT=1420
BACKEND_PID=""
FRONTEND_PID=""

# ---- カラー出力 ----
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ---- クリーンアップ ----
cleanup() {
    echo ""
    info "終了しています..."
    [[ -n "$BACKEND_PID" ]]  && kill "$BACKEND_PID"  2>/dev/null || true
    [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
    info "終了しました。"
}
trap cleanup EXIT INT TERM

echo ""
echo " ============================================="
echo "  Auto Idea Combiner - 起動中..."
echo " ============================================="
echo ""

# ---- 前提ツール確認 ----
for tool in uv pnpm; do
    if ! command -v "$tool" &>/dev/null; then
        error "$tool が見つかりません。"
        case $tool in
            uv)   error "  インストール: curl -LsSf https://astral.sh/uv/install.sh | sh" ;;
            pnpm) error "  インストール: npm install -g pnpm" ;;
        esac
        exit 1
    fi
done

# ---- .env 確認 ----
if [[ ! -f "$ROOT/.env" ]]; then
    warn ".env が見つかりません。.env.example からコピーします..."
    cp "$ROOT/.env.example" "$ROOT/.env"
    warn ".env を編集してAPIキーを設定してください: $ROOT/.env"
fi

# ---- バックエンド起動 ----
info "[1/3] Pythonバックエンドを起動中 (port $BACKEND_PORT)..."
cd "$BACKEND"
uv run uvicorn main:app --port "$BACKEND_PORT" >"$ROOT/backend.log" 2>&1 &
BACKEND_PID=$!

# ---- バックエンド起動待ち ----
info "[2/3] バックエンドの起動を待っています..."
for i in $(seq 1 15); do
    sleep 2
    if curl -sf "http://localhost:$BACKEND_PORT/api/health" >/dev/null 2>&1; then
        info "       バックエンド起動完了!"
        break
    fi
    if [[ $i -eq 15 ]]; then
        error "バックエンドの起動がタイムアウトしました。"
        error "backend.log を確認してください: $ROOT/backend.log"
        exit 1
    fi
done

# ---- フロントエンド起動 ----
info "[3/3] フロントエンドを起動中..."
cd "$FRONTEND"

if [[ ! -d "node_modules" ]]; then
    info "       依存関係をインストール中 (初回のみ)..."
    pnpm install
fi

# ビルド済み実行ファイルの確認
BUILT_APP=""
if [[ -f "src-tauri/target/release/auto-idea-combiner" ]]; then
    BUILT_APP="src-tauri/target/release/auto-idea-combiner"
elif [[ -f "src-tauri/target/release/bundle/macos/Auto Idea Combiner.app/Contents/MacOS/auto-idea-combiner" ]]; then
    BUILT_APP="src-tauri/target/release/bundle/macos/Auto Idea Combiner.app/Contents/MacOS/auto-idea-combiner"
fi

if [[ -n "$BUILT_APP" ]]; then
    info "       ビルド済み実行ファイルを起動します。"
    "$BUILT_APP" &
    FRONTEND_PID=$!
else
    info "       開発モードで起動します (pnpm tauri dev)"
    warn "       初回はRustのコンパイルに数分かかります..."
    pnpm tauri dev &
    FRONTEND_PID=$!
fi

echo ""
echo " ============================================="
echo "  起動完了!"
echo "  バックエンド: http://localhost:$BACKEND_PORT"
echo "  フロントエンド: http://localhost:$FRONTEND_PORT"
echo " ============================================="
echo ""
info "終了するには Ctrl+C を押してください。"
echo ""

# バックグラウンドプロセスが終了するまで待機
wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
