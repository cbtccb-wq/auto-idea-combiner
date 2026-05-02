import { useEffect, useState } from "react";
import { getIdeas, submitFeedback } from "../api/client";
import { IdeaList } from "../components/IdeaList";
import type { FeedbackRating, IdeaCard } from "../types";

export function History() {
  const [ideas, setIdeas] = useState<IdeaCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    void loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setIsLoading(true);
      setError("");
      const history = await getIdeas();
      setIdeas(
        [...history].sort(
          (left, right) => Date.parse(right.created_at) - Date.parse(left.created_at),
        ),
      );
    } catch (historyError) {
      setError(historyError instanceof Error ? historyError.message : "履歴の読み込みに失敗しました。");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (ideaId: string, rating: FeedbackRating) => {
    try {
      await submitFeedback({ ideaCardId: ideaId, rating });
    } catch (feedbackError) {
      setError(
        feedbackError instanceof Error
          ? feedbackError.message
          : "フィードバックの送信に失敗しました。",
      );
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-white">履歴</h2>
          <p className="mt-1 text-sm text-slate-400">
            これまでに生成したアイデアを一覧で確認できます。
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadHistory()}
          className="rounded-full border border-slate-700 bg-slate-900/80 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-cyan-400/40 hover:text-white"
        >
          読み直す
        </button>
      </div>

      {error ? (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
          {error}
        </div>
      ) : null}

      {isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/60 px-6 py-5 text-sm text-slate-300">
          履歴を読み込んでいます...
        </div>
      ) : (
        <IdeaList ideas={ideas} onFeedback={handleFeedback} />
      )}
    </div>
  );
}
