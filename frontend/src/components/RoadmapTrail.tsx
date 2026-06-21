// The contribution roadmap, drawn as a literal trail with 4 waypoints --
// the most direct expression of the "open source as terrain to hike"
// metaphor. Completed waypoints are blazed (filled + colored); the current
// one pulses faintly; future ones are outlines.

interface RoadmapTrailProps {
  currentStage: number; // 1-4
  label: string;
}

const STAGES = [
  { stage: 1, name: "Explore" },
  { stage: 2, name: "First issue" },
  { stage: 3, name: "Submit PR" },
  { stage: 4, name: "Contributor" },
];

export function RoadmapTrail({ currentStage, label }: RoadmapTrailProps) {
  return (
    <div>
      <div className="flex items-center">
        {STAGES.map((s, i) => {
          const completed = s.stage < currentStage;
          const isCurrent = s.stage === currentStage;
          const isLast = i === STAGES.length - 1;

          return (
            <div key={s.stage} className="flex flex-1 items-center last:flex-none">
              <div className="flex flex-col items-center gap-2">
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full border-2 font-mono text-xs ${
                    completed || isCurrent
                      ? "border-blaze bg-blaze text-base-bg"
                      : "border-base-border bg-base-surface text-ink-faint"
                  } ${isCurrent ? "ring-4 ring-blaze/20" : ""}`}
                >
                  {s.stage}
                </div>
                <span
                  className={`whitespace-nowrap text-xs ${
                    completed || isCurrent ? "text-ink-primary" : "text-ink-faint"
                  }`}
                >
                  {s.name}
                </span>
              </div>
              {!isLast && (
                <div
                  className={`mx-2 h-0.5 flex-1 rounded ${
                    s.stage < currentStage ? "bg-blaze" : "bg-base-border"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
      <p className="mt-4 font-display text-sm text-ink-secondary">
        Current waypoint: <span className="text-blaze">{label}</span>
      </p>
    </div>
  );
}
