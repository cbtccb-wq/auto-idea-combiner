interface ScoreBadgeProps {
  label: string;
  value: number;
}

function badgeTone(value: number): string {
  if (value > 0.7) {
    return "border-emerald-400/30 bg-emerald-500/15 text-emerald-200";
  }
  if (value > 0.4) {
    return "border-amber-400/30 bg-amber-500/15 text-amber-200";
  }
  return "border-rose-400/30 bg-rose-500/15 text-rose-200";
}

export function ScoreBadge({ label, value }: ScoreBadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-medium ${badgeTone(
        value,
      )}`}
    >
      <span className="text-slate-200/80">{label}</span>
      <span className="font-semibold text-white">{value.toFixed(2)}</span>
    </span>
  );
}
