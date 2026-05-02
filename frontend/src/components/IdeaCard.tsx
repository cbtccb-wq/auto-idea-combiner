import { useState } from "react";
import type { FeedbackRating, IdeaCard as IdeaCardType } from "../types";
import { FeedbackBar } from "./FeedbackBar";
import { ScoreBadge } from "./ScoreBadge";

interface IdeaCardProps {
  card: IdeaCardType;
  onFeedback: (id: string, rating: FeedbackRating) => void;
}

const scoreLabels = {
  novelty: "新規性",
  relevance: "関連性",
  distance: "距離感",
  feasibility: "実現性",
  fun: "楽しさ",
  apiFit: "API適合",
  total: "総合",
};

export function IdeaCard({ card, onFeedback }: IdeaCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <article className="group flex h-full flex-col rounded-3xl border border-white/10 bg-slate-900/75 p-5 shadow-glow backdrop-blur">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <p className="mb-2 text-xs uppercase tracking-[0.28em] text-cyan-300/80">
            {card.concept_a} × {card.concept_b}
          </p>
          <h3 className="text-xl font-semibold text-white">{card.title}</h3>
        </div>
        <div className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-100">
          {card.detail_level}
        </div>
      </div>

      <p className="mb-5 text-sm leading-6 text-slate-300">{card.summary}</p>

      <div className="mb-5 flex flex-wrap gap-2">
        <ScoreBadge label={scoreLabels.novelty} value={card.novelty_score} />
        <ScoreBadge label={scoreLabels.relevance} value={card.relevance_score} />
        <ScoreBadge label={scoreLabels.distance} value={card.distance_score} />
        <ScoreBadge label={scoreLabels.feasibility} value={card.feasibility_score} />
        <ScoreBadge label={scoreLabels.fun} value={card.fun_score} />
        <ScoreBadge label={scoreLabels.apiFit} value={card.api_fit_score} />
        <ScoreBadge label={scoreLabels.total} value={card.total_score} />
      </div>

      <div className="mt-auto space-y-4">
        <FeedbackBar onSelect={(rating) => onFeedback(card.id, rating)} />

        <button
          type="button"
          onClick={() => setExpanded((current) => !current)}
          className="w-full rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-left text-sm text-slate-200 transition hover:border-cyan-400/30 hover:bg-slate-950"
        >
          <div className="flex items-center justify-between gap-4">
            <span className="font-medium">{expanded ? "詳細を閉じる" : "詳細を見る"}</span>
            <span className="text-xs uppercase tracking-[0.24em] text-slate-400">
              {expanded ? "Close" : "Open"}
            </span>
          </div>
        </button>

        {expanded ? (
          <div className="space-y-3 rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm leading-6 text-slate-300">
            <DetailItem label="なぜ面白いか" value={card.why_interesting} />
            <DetailItem label="対象ユーザー" value={card.target_user} />
            <DetailItem label="主な技術" value={card.main_tech} />
            <DetailItem label="MVP" value={card.mvp_outline} />
            <DetailItem label="差別化" value={card.differentiator} />
            <DetailItem label="楽しいポイント" value={card.fun_point} />
            <DetailItem label="リスク" value={card.risks} />
          </div>
        ) : null}
      </div>
    </article>
  );
}

interface DetailItemProps {
  label: string;
  value: string;
}

function DetailItem({ label, value }: DetailItemProps) {
  return (
    <div>
      <p className="mb-1 text-xs uppercase tracking-[0.22em] text-slate-500">{label}</p>
      <p>{value}</p>
    </div>
  );
}
