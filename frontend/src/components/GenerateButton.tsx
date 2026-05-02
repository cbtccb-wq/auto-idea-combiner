import { useState } from "react";
import { generateIdeas, ingest } from "../api/client";
import type { DetailLevel, IdeaCard } from "../types";

interface GenerateButtonProps {
  onGenerated: (ideas: IdeaCard[]) => void;
  onError: (message: string) => void;
}

const detailLevels: Array<{ label: string; value: DetailLevel }> = [
  { label: "ライト", value: "light" },
  { label: "スタンダード", value: "standard" },
  { label: "ディープ", value: "deep" },
];

export function GenerateButton({ onGenerated, onError }: GenerateButtonProps) {
  const [detailLevel, setDetailLevel] = useState<DetailLevel>("standard");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [statusMessage, setStatusMessage] = useState(
    "設定したフォルダから素材を取り込み、その後にアイデアを生成できます。",
  );

  const handleIngest = async () => {
    try {
      setIsIngesting(true);
      onError("");
      const result = await ingest();

      if (result.sources_scanned === 0) {
        setStatusMessage(
          "取り込める素材が見つかりませんでした。設定タブでローカル走査ディレクトリを保存してください。",
        );
        return;
      }

      if (result.concepts_added === 0) {
        setStatusMessage(
          `${result.sources_scanned} 件の素材を確認しましたが、新しい概念は追加されませんでした。`,
        );
        return;
      }

      setStatusMessage(
        `${result.sources_scanned} 件の素材から ${result.concepts_added} 個の概念を取り込みました。`,
      );
    } catch (error) {
      onError(error instanceof Error ? error.message : "素材の取り込みに失敗しました。");
    } finally {
      setIsIngesting(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      onError("");
      const ideas = await generateIdeas({ detailLevel, count: 3 });
      onGenerated(ideas);
      setStatusMessage(`${ideas.length} 件のアイデアを生成しました。`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "アイデア生成に失敗しました。";
      onError(message);

      if (message.includes("発想の材料")) {
        setStatusMessage("先に「素材を取り込む」を実行して、概念を集めてください。");
      }
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <section className="rounded-[2rem] border border-cyan-400/20 bg-gradient-to-br from-slate-900/90 via-slate-900/80 to-cyan-950/50 p-6 shadow-glow">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <p className="mb-2 text-xs uppercase tracking-[0.32em] text-cyan-300/80">
            Materials And Generation
          </p>
          <h2 className="text-2xl font-semibold text-white">素材を取り込んでから 3 件生成</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
            設定タブで指定したフォルダからテキストを読み込み、概念を更新してからアイデアを作成します。
          </p>
        </div>

        <div className="flex flex-col gap-4 xl:items-end">
          <div className="flex flex-wrap gap-2">
            {detailLevels.map((option) => {
              const isActive = detailLevel === option.value;

              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setDetailLevel(option.value)}
                  className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
                    isActive
                      ? "border-cyan-300/40 bg-cyan-400/15 text-cyan-100"
                      : "border-slate-700 bg-slate-900/80 text-slate-300 hover:border-slate-500 hover:text-white"
                  }`}
                >
                  {option.label}
                </button>
              );
            })}
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={handleIngest}
              disabled={isIngesting || isGenerating}
              className="inline-flex min-w-[11rem] items-center justify-center rounded-2xl border border-cyan-300/30 bg-slate-950/70 px-5 py-4 text-base font-semibold text-cyan-100 transition hover:border-cyan-200/50 hover:bg-cyan-400/10 disabled:cursor-not-allowed disabled:border-slate-800 disabled:text-slate-500"
            >
              {isIngesting ? "取り込み中..." : "素材を取り込む"}
            </button>

            <button
              type="button"
              onClick={handleGenerate}
              disabled={isGenerating || isIngesting}
              className="inline-flex min-w-[15rem] items-center justify-center rounded-2xl bg-cyan-400 px-6 py-4 text-base font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-cyan-900 disabled:text-slate-300"
            >
              {isGenerating ? "生成中..." : "アイデアを生成"}
            </button>
          </div>
        </div>
      </div>

      <div className="mt-5 rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-300">
        {statusMessage}
      </div>
    </section>
  );
}
