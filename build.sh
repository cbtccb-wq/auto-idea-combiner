#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

echo ""
echo " ============================================="
echo "  Auto Idea Combiner - 本番ビルド"
echo " ============================================="
echo ""

for tool in uv pnpm cargo; do
    if ! command -v "$tool" &>/dev/null; then
        error "$tool が見つかりません。"
        exit 1
    fi
done

info "[1/3] Pythonバックエンド依存関係を確認中..."
cd "$ROOT/backend" && uv sync
info "       完了"

info "[2/3] フロントエンド依存関係を確認中..."
cd "$ROOT/frontend"
[[ ! -d "node_modules" ]] && pnpm install
info "       完了"

info "[3/3] Tauriアプリをビルド中 (数分かかります)..."
pnpm tauri build

echo ""
echo " ============================================="
echo "  ビルド完了!"
echo "  実行ファイル: frontend/src-tauri/target/release/"
echo "  インストーラー: frontend/src-tauri/target/release/bundle/"
echo " ============================================="
