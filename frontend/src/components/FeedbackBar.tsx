import type { FeedbackRating } from "../types";

interface FeedbackBarProps {
  onSelect: (rating: FeedbackRating) => void;
}

const feedbackOptions: Array<{ label: string; value: FeedbackRating }> = [
  { label: "面白い", value: "interesting" },
  { label: "まあまあ", value: "okay" },
  { label: "うーん", value: "not_sure" },
  { label: "もっと遠く", value: "more_distant" },
  { label: "もっと実用的", value: "more_practical" },
];

export function FeedbackBar({ onSelect }: FeedbackBarProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {feedbackOptions.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onSelect(option.value)}
          className="rounded-full border border-slate-700 bg-slate-900/80 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:border-cyan-400/40 hover:bg-cyan-400/10 hover:text-white"
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
