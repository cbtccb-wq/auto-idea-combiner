import { useEffect, useState, type FormEvent } from "react";
import { getSettings, updateSettings } from "../api/client";
import type { ScoreWeights, Settings } from "../types";

const defaultSettings: Settings = {
  llm_provider: "anthropic",
  embedding_provider: "local",
  score_weights: {
    novelty: 0.22,
    relevance: 0.18,
    distance: 0.18,
    feasibility: 0.16,
    fun: 0.16,
    api_fit: 0.1,
  },
  external_api_enabled: true,
  local_scan_dirs: [],
};

const weightLabels: Array<{ key: keyof ScoreWeights; label: string }> = [
  { key: "novelty", label: "新規性" },
  { key: "relevance", label: "関連性" },
  { key: "distance", label: "距離感" },
  { key: "feasibility", label: "実現性" },
  { key: "fun", label: "楽しさ" },
  { key: "api_fit", label: "API適合" },
];

export function SettingsPage() {
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    void (async () => {
      try {
        const current = await getSettings();
        setSettings(current);
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "設定の取得に失敗しました。");
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  const handleWeightChange = (key: keyof ScoreWeights, rawValue: string) => {
    const nextValue = Number.parseFloat(rawValue);

    setSettings((current) => ({
      ...current,
      score_weights: {
        ...current.score_weights,
        [key]: Number.isFinite(nextValue) ? nextValue : 0,
      },
    }));
  };

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    try {
      setIsSaving(true);
      setMessage("");
      const updated = await updateSettings(settings);
      setSettings(updated);
      setMessage("設定を更新しました。");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "設定の更新に失敗しました。");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-2xl font-semibold text-white">設定</h2>
        <p className="mt-1 text-sm text-slate-400">
          LLM プロバイダとスコア重みを調整して、生成の傾向を細かく制御します。
        </p>
      </div>

      {message ? (
        <div className="rounded-2xl border border-slate-700 bg-slate-900/80 px-4 py-3 text-sm text-slate-200">
          {message}
        </div>
      ) : null}

      {isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/60 px-6 py-5 text-sm text-slate-300">
          設定を読み込んでいます...
        </div>
      ) : (
        <form
          onSubmit={handleSave}
          className="space-y-6 rounded-[2rem] border border-white/10 bg-slate-900/70 p-6 shadow-glow"
        >
          <div className="grid gap-5 lg:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm font-medium text-slate-200">LLM プロバイダ</span>
              <select
                value={settings.llm_provider}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    llm_provider: event.target.value,
                  }))
                }
                className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400/60"
              >
                <option value="anthropic">Anthropic</option>
                <option value="openai">OpenAI</option>
                <option value="gemini">Gemini</option>
                <option value="local">Local</option>
              </select>
            </label>

            <label className="space-y-2">
              <span className="text-sm font-medium text-slate-200">Embedding プロバイダ</span>
              <select
                value={settings.embedding_provider}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    embedding_provider: event.target.value,
                  }))
                }
                className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400/60"
              >
                <option value="local">Local</option>
                <option value="openai">OpenAI</option>
                <option value="voyage">Voyage</option>
              </select>
            </label>
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-white">スコア重み</h3>
              <p className="mt-1 text-sm text-slate-400">0.00 から 1.00 の範囲で設定します。</p>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              {weightLabels.map((weight) => (
                <label
                  key={weight.key}
                  className="space-y-2 rounded-2xl border border-slate-800 bg-slate-950/70 p-4"
                >
                  <span className="text-sm font-medium text-slate-200">{weight.label}</span>
                  <input
                    type="number"
                    min={0}
                    max={1}
                    step={0.01}
                    value={settings.score_weights[weight.key]}
                    onChange={(event) => handleWeightChange(weight.key, event.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none transition focus:border-cyan-400/60"
                  />
                </label>
              ))}
            </div>
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm font-medium text-slate-200">ローカル走査ディレクトリ</span>
              <textarea
                rows={4}
                value={settings.local_scan_dirs.join("\n")}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    local_scan_dirs: event.target.value
                      .split("\n")
                      .map((entry) => entry.trim())
                      .filter(Boolean),
                  }))
                }
                className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400/60"
                placeholder="C:\\Users\\...\\notes"
              />
            </label>

            <label className="flex items-start gap-3 rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
              <input
                type="checkbox"
                checked={settings.external_api_enabled}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    external_api_enabled: event.target.checked,
                  }))
                }
                className="mt-1 h-4 w-4 rounded border-slate-600 bg-slate-900 text-cyan-400 focus:ring-cyan-400"
              />
              <div>
                <p className="text-sm font-medium text-slate-100">外部 API を有効化</p>
                <p className="mt-1 text-sm text-slate-400">
                  ニュースや外部データを取り込む補助ソースを使用します。
                </p>
              </div>
            </label>
          </div>

          <button
            type="submit"
            disabled={isSaving}
            className="inline-flex items-center justify-center rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-cyan-900 disabled:text-slate-300"
          >
            {isSaving ? "保存中..." : "設定を保存"}
          </button>
        </form>
      )}
    </div>
  );
}
