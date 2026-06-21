import type { IssueDifficulty } from "../types";

const CONFIG: Record<IssueDifficulty, { label: string; color: string; bg: string }> = {
  beginner: { label: "Beginner", color: "#7FA66B", bg: "rgba(127, 166, 107, 0.12)" },
  intermediate: { label: "Intermediate", color: "#D4A017", bg: "rgba(212, 160, 23, 0.12)" },
  advanced: { label: "Advanced", color: "#B5533C", bg: "rgba(181, 83, 60, 0.12)" },
};

export function DifficultyBadge({ difficulty }: { difficulty: IssueDifficulty }) {
  const cfg = CONFIG[difficulty];
  return (
    <span
      className="inline-flex items-center rounded-full px-2.5 py-0.5 font-mono text-[11px] uppercase tracking-wide"
      style={{ color: cfg.color, backgroundColor: cfg.bg }}
    >
      {cfg.label}
    </span>
  );
}
