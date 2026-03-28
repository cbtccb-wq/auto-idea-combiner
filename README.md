# Auto Idea Combiner 🔀

**偶然発想エンジン** — ユーザーの日常デジタル行動から概念を抽出・組み合わせて新しいアイデアの種を生成するデスクトップアプリ

> 「一見無関係な概念が衝突する瞬間」を意図的に作り出す

## 概要

ユーザーが普段見ている情報・作業内容・メモ・閲覧履歴・過去の発想ログなどを自動的に収集・解析し、
**一見すると無関係な複数の概念を自動で組み合わせ**、新しいアイデアの種を生成するソフトウェアです。

毎回ユーザーがテーマや条件を細かく入力しなくても動作し、
日常のデジタル行動の中から素材を拾って、自動的に「発想の衝突」を起こすことを目指します。

## 技術スタック

| 領域 | 採用技術 |
|------|----------|
| フロントエンド | Tauri 2.x + React 18 + TypeScript |
| バックエンド | Python 3.11+ + FastAPI |
| DB | SQLite + ChromaDB |
| NLP | spaCy / janome + KeyBERT |
| Embedding | sentence-transformers (ローカル) |
| LLM | Claude / GPT / Gemini（設定で切替） |

## セットアップ

```bash
# 1. リポジトリのクローン
git clone https://github.com/cbtccb-wq/auto-idea-combiner.git
cd auto-idea-combiner

# 2. 環境変数設定
cp .env.example .env
# .env を編集してAPIキーを設定

# 3. バックエンド起動
cd backend
uv sync
uvicorn main:app --port 8765 --reload

# 4. フロントエンド起動（別ターミナル）
cd frontend
pnpm install
pnpm tauri dev
```

## アーキテクチャ

```
情報収集 → 概念抽出 → Embedding → 組み合わせ選定 → LLM生成 → スコアリング → UI表示
```

## ライセンス

MIT
