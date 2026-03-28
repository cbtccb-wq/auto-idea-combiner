# セットアップガイド

## 前提条件

| ツール | バージョン | 備考 |
|--------|-----------|------|
| Python | 3.11+ | `uv` 経由を推奨 |
| uv | 最新版 | `pip install uv` |
| Node.js | 20+ | |
| pnpm | 8+ | `npm install -g pnpm` |
| Rust / Cargo | 最新安定版 | Tauri必須: [rustup.rs](https://rustup.rs) |

> **Windows の場合**: [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) も必要です（Tauri用）

---

## 1. リポジトリのクローン

```bash
git clone https://github.com/cbtccb-wq/auto-idea-combiner.git
cd auto-idea-combiner
```

---

## 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を開き、使用するLLMのAPIキーを**最低1つ**設定してください:

```env
# 使用するLLMを選択（anthropic / openai / gemini）
LLM_PROVIDER=anthropic

# 対応するAPIキーを設定
ANTHROPIC_API_KEY=sk-ant-xxxxx
# OPENAI_API_KEY=sk-xxxxx
# GEMINI_API_KEY=xxxxx
```

---

## 3. バックエンドのセットアップ

```bash
cd backend

# 依存関係インストール（初回のみ）
uv sync

# サーバー起動
uv run uvicorn main:app --port 8765 --reload
```

起動確認:
```
http://localhost:8765/api/health
# → {"status": "ok"}
```

---

## 4. フロントエンドのセットアップ

別ターミナルで:

```bash
cd frontend

# 依存関係インストール（初回のみ）
pnpm install

# デスクトップアプリとして起動
pnpm tauri dev

# ブラウザで確認する場合（バックエンド別途起動が必要）
pnpm dev
# → http://localhost:1420
```

---

## 5. 初回データ投入

1. アプリを起動する
2. **設定タブ** → ローカルスキャンディレクトリを指定（例: `~/Documents`）
3. **ホームタブ** → 「アイデアを生成」ボタンをクリック

---

## 6. LLMプロバイダーの切り替え

`.env` の `LLM_PROVIDER` を変更して再起動するだけです:

```env
LLM_PROVIDER=openai   # GPT-4o-mini を使用
LLM_PROVIDER=gemini   # Gemini 1.5 Flash を使用
LLM_PROVIDER=anthropic  # Claude Haiku を使用（デフォルト）
```

---

## 7. Embeddingをローカルで使う（APIキー不要）

デフォルト設定ではローカルの`sentence-transformers`モデルを使用します（初回ダウンロードあり）:

```env
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

OpenAI Embeddingを使う場合:
```env
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
```

---

## よくある問題

**`uv sync` でエラーが出る**
→ Python 3.11+ がインストールされているか確認: `python --version`

**Tauri ビルドでエラーが出る**
→ Rust と C++ Build Tools が入っているか確認: `cargo --version`

**アイデアが生成されない（空のリストが返る）**
→ `.env` のAPIキーが正しく設定されているか確認。バックエンドログを確認: `uvicorn` のターミナル出力を見てください。
