import { useState } from "react";
import { generateIdeas } from "../api/client";
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
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerate = async () => {
    try {
      setIsLoading(true);
      onError("");
      const ideas = await generateIdeas({ detailLevel, count: 3 });
      onGenerated(ideas);
    } catch (error) {
      onError(error instanceof Error ? error.message : "アイデア生成に失敗しました。");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="rounded-[2rem] border border-cyan-400/20 bg-gradient-to-br from-slate-900/90 via-slate-900/80 to-cyan-950/50 p-6 shadow-glow">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <p className="mb-2 text-xs uppercase tracking-[0.32em] text-cyan-300/80">
            Generate Today&apos;s Set
          </p>
          <h2 className="text-2xl font-semibold text-white">今日の組み合わせを 3 件生成</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
            発想の距離感を調整しながら、新規性と実用性のバランスを見比べます。
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

          <button
            type="button"
            onClick={handleGenerate}
            disabled={isLoading}
            className="inline-flex min-w-[15rem] items-center justify-center rounded-2xl bg-cyan-400 px-6 py-4 text-base font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-cyan-900 disabled:text-slate-300"
          >
            {isLoading ? "生成中..." : "アイデアを生成"}
          </button>
        </div>
      </div>
    </section>
  );
}
