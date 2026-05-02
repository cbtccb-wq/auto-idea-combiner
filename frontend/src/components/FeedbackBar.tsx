import type { FeedbackRating } from "../types";

interface FeedbackBarProps {
  onSelect: (rating: FeedbackRating) => void;
}

const feedbackOptions: Array<{ label: string; value: FeedbackRating }> = [
  { label: "かなり良い", value: "great" },
  { label: "悪くない", value: "ok" },
  { label: "見送り", value: "no" },
  { label: "もう少し近く", value: "closer" },
  { label: "もう少し遠く", value: "further" },
  { label: "もっと実用的", value: "practical" },
  { label: "もっと大胆に", value: "wilder" },
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
