import { useState } from "react";
import { submitFeedback } from "../api/client";
import { GenerateButton } from "../components/GenerateButton";
import { IdeaList } from "../components/IdeaList";
import type { FeedbackRating, IdeaCard } from "../types";

export function Home() {
  const [ideas, setIdeas] = useState<IdeaCard[]>([]);
  const [error, setError] = useState("");
  const [feedbackState, setFeedbackState] = useState<Record<string, string>>({});

  const handleFeedback = async (ideaId: string, rating: FeedbackRating) => {
    try {
      await submitFeedback({ ideaCardId: ideaId, rating });
      setFeedbackState((current) => ({
        ...current,
        [ideaId]: "フィードバックを保存しました。",
      }));
    } catch (feedbackError) {
      setFeedbackState((current) => ({
        ...current,
        [ideaId]:
          feedbackError instanceof Error
            ? feedbackError.message
            : "フィードバックの送信に失敗しました。",
      }));
    }
  };

  const feedbackMessages = Object.values(feedbackState);
  const latestFeedback = feedbackMessages[feedbackMessages.length - 1];

  return (
    <div className="space-y-6">
      <GenerateButton onGenerated={setIdeas} onError={setError} />

      {error ? (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
          {error}
        </div>
      ) : null}

      <IdeaList ideas={ideas} onFeedback={handleFeedback} />

      {latestFeedback ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-300">
          最新のフィードバック: {latestFeedback}
        </div>
      ) : null}
    </div>
  );
}
