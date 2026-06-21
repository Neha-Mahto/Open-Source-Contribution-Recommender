import type { ActivityDay } from "../types";

// GitHub-style calendar heatmap, but using the palette's ochre/blaze ramp
// instead of GitHub's own green -- same information, distinct identity.

function intensityColor(count: number, max: number): string {
  if (count === 0) return "#1C2220";
  const ratio = max > 0 ? count / max : 0;
  if (ratio > 0.75) return "#D97742";
  if (ratio > 0.5) return "#D4A017";
  if (ratio > 0.25) return "#7FA66B";
  return "#3A4440";
}

export function ActivityHeatmap({ days }: { days: ActivityDay[] }) {
  const byDate = new Map(days.map((d) => [d.date, d.count]));
  const max = days.reduce((m, d) => Math.max(m, d.count), 0);

  const today = new Date();
  const cells: { date: string; count: number }[] = [];
  for (let i = 89; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const key = d.toISOString().slice(0, 10);
    cells.push({ date: key, count: byDate.get(key) ?? 0 });
  }

  // Group into weeks (columns of 7) for a calendar-grid layout
  const weeks: { date: string; count: number }[][] = [];
  for (let i = 0; i < cells.length; i += 7) {
    weeks.push(cells.slice(i, i + 7));
  }

  return (
    <div>
      <div className="flex gap-1">
        {weeks.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-1">
            {week.map((cell) => (
              <div
                key={cell.date}
                title={`${cell.date}: ${cell.count} contribution${cell.count === 1 ? "" : "s"}`}
                className="h-3 w-3 rounded-sm"
                style={{ backgroundColor: intensityColor(cell.count, max) }}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center gap-2 text-xs text-ink-faint">
        <span>Less</span>
        {[0, 0.2, 0.5, 0.8, 1].map((r) => (
          <span
            key={r}
            className="h-3 w-3 rounded-sm"
            style={{ backgroundColor: intensityColor(r === 0 ? 0 : Math.ceil(r * max), max) }}
          />
        ))}
        <span>More</span>
      </div>
    </div>
  );
}
