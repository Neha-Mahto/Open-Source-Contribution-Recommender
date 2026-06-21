// The signature visual element of the app: a repo's health score rendered
// as three concentric contour rings (activity / community / friendliness),
// echoing a topographic map -- fitting, since the rest of the product
// treats difficulty and discovery as terrain to navigate.

interface HealthRingProps {
  activity: number;
  community: number;
  friendliness: number;
  overall: number;
  size?: number;
}

const RING_CONFIG = [
  { key: "activity", color: "#7FA66B", label: "Activity" },
  { key: "community", color: "#D4A017", label: "Community" },
  { key: "friendliness", color: "#D97742", label: "Friendliness" },
] as const;

export function HealthRing({ activity, community, friendliness, overall, size = 140 }: HealthRingProps) {
  const values = { activity, community, friendliness };
  const center = size / 2;
  const strokeWidth = size * 0.07;
  const gap = strokeWidth * 0.45;

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="rotate-[-90deg]">
        {RING_CONFIG.map((ring, i) => {
          const radius = center - strokeWidth / 2 - i * (strokeWidth + gap);
          const circumference = 2 * Math.PI * radius;
          const value = values[ring.key as keyof typeof values];
          const dash = (value / 100) * circumference;

          return (
            <g key={ring.key}>
              <circle
                cx={center}
                cy={center}
                r={radius}
                fill="none"
                stroke="#2C3431"
                strokeWidth={strokeWidth}
              />
              <circle
                cx={center}
                cy={center}
                r={radius}
                fill="none"
                stroke={ring.color}
                strokeWidth={strokeWidth}
                strokeDasharray={`${dash} ${circumference}`}
                strokeLinecap="round"
                style={{ transition: "stroke-dasharray 0.6s ease-out" }}
              />
            </g>
          );
        })}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-2xl font-medium text-ink-primary">{Math.round(overall)}</span>
        <span className="font-mono text-[10px] uppercase tracking-wider text-ink-faint">health</span>
      </div>
    </div>
  );
}

export function HealthRingLegend() {
  return (
    <div className="flex flex-col gap-1.5">
      {RING_CONFIG.map((ring) => (
        <div key={ring.key} className="flex items-center gap-2 text-xs text-ink-secondary">
          <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: ring.color }} />
          {ring.label}
        </div>
      ))}
    </div>
  );
}
