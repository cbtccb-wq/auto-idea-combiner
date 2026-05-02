# セットアップガイド

## 前提条件

| ツール | バージョン | 補足 |
|--------|-----------|------|
| Python | 3.11+ | `uv` の利用を推奨 |
| uv | 最新版 | `pip install uv` |
| Node.js | 20+ | |
| pnpm | 8+ | `npm install -g pnpm` |
| Rust / Cargo | 最新安定版 | Tauri 実行用 |

> Windows では [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) も入れておくと安心です。

## 1. リポジトリを取得

```bash
git clone https://github.com/cbtccb-wq/auto-idea-combiner.git
cd auto-idea-combiner
```

## 2. `.env` を作成

```bash
cp .env.example .env
```

最低限、利用する LLM に応じて API キーを設定してください。

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx

# 使う場合だけ設定
# OPENAI_API_KEY=sk-xxxxx
# GEMINI_API_KEY=xxxxx
```

`LLM_PROVIDER` は `anthropic` / `openai` / `gemini` / `local` を選べます。  
`local` を選ぶと外部 LLM を使わず、テンプレートベースで生成します。

## 3. Windows では `start.bat` が最短

リポジトリ直下で次を実行すると、バックエンドとフロントエンドをまとめて起動できます。

```bat
start.bat
```

起動時のログは次に出力されます。

- `backend.log`
- `frontend.log`

ブラウザ版は `http://localhost:1420/` で開きます。

## 4. 手動起動する場合

### バックエンド

```bash
cd backend
uv sync
uv run uvicorn main:app --port 8765 --reload
```

確認:

```bash
curl http://localhost:8765/api/health
```

### フロントエンド

```bash
cd frontend
pnpm install
pnpm dev
```

Tauri で起動する場合:

```bash
pnpm tauri dev
```

## 5. 初回の使い方

1. アプリを開く
2. `設定` タブで `ローカル走査ディレクトリ` を保存する
3. `ホーム` タブで `素材を取り込む` を押す
4. その後に `アイデアを生成` を押す

初回は「素材の取り込み」をしないと、生成に必要な概念が足りずエラーになります。

## 6. 現在の実装で保存される設定

- `LLM プロバイダ`
- `スコア重み`
- `ローカル走査ディレクトリ`

`Embedding` は現在 `Local` 固定です。

## 7. よくある確認ポイント

### 起動はしたが生成できない

`設定` タブでフォルダを保存したあと、`ホーム` で `素材を取り込む` を実行してください。

### API 通信で失敗する

バックエンドの `http://localhost:8765/api/health` が `{"status":"ok"}` を返すか確認してください。

### LLM を切り替えてもエラーになる

対応する API キーが `.env` に入っているか確認してください。  
キーが無い場合は `local` にするとテンプレート生成で動作確認できます。
