import type { FeedbackRating, IdeaCard as IdeaCardType } from "../types";
import { IdeaCard } from "./IdeaCard";

interface IdeaListProps {
  ideas: IdeaCardType[];
  onFeedback: (id: string, rating: FeedbackRating) => void;
}

export function IdeaList({ ideas, onFeedback }: IdeaListProps) {
  if (ideas.length === 0) {
    return (
      <div className="rounded-3xl border border-dashed border-slate-700 bg-slate-900/40 p-10 text-center text-slate-400">
        まだアイデアがありません。生成ボタンから 3 件の案を作成できます。
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
      {ideas.map((idea) => (
        <IdeaCard key={idea.id} card={idea} onFeedback={onFeedback} />
      ))}
    </div>
  );
}
