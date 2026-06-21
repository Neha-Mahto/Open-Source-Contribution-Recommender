import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
import { Card } from "../components/Card";
import { RoadmapTrail } from "../components/RoadmapTrail";
import { ActivityHeatmap } from "../components/ActivityHeatmap";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import type { DashboardOut } from "../types";
import { Map } from "lucide-react";

const STAT_LABELS: { key: keyof DashboardOut["contribution_stats"]; label: string }[] = [
  { key: "issues_opened", label: "Issues opened" },
  { key: "pr_submitted", label: "PRs submitted" },
  { key: "pr_merged", label: "PRs merged" },
  { key: "pr_closed", label: "PRs closed" },
];

export function Dashboard() {
  const { user } = useAuth();
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api.get<DashboardOut>("/dashboard"),
  });

  if (isLoading) return <LoadingSkeleton rows={4} />;
  if (!data) return null;

  const chartData = data.language_breakdown.map((l) => ({ name: l.language, count: l.count }));

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-primary">
          Welcome back, {user?.name?.split(" ")[0] || user?.github_username}
        </h1>
        <p className="mt-1 text-sm text-ink-secondary">Here's where you stand on the trail.</p>
      </div>

      <Card>
        <RoadmapTrail
          currentStage={data.contribution_stats.roadmap_stage}
          label={data.contribution_stats.roadmap_label}
        />
      </Card>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {STAT_LABELS.map(({ key, label }) => (
          <Card key={key} className="text-center">
            <p className="font-mono text-3xl font-medium text-ink-primary">
              {data.contribution_stats[key] as number}
            </p>
            <p className="mt-1 text-xs text-ink-secondary">{label}</p>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="mb-4 font-display text-sm font-medium text-ink-primary">Activity, last 90 days</h2>
          {data.activity_timeline.length === 0 ? (
            <EmptyState
              icon={<Map size={28} />}
              title="No tracked activity yet"
              description="Log a contribution from an issue you've opened or a PR you've submitted to start filling in the trail."
            />
          ) : (
            <ActivityHeatmap days={data.activity_timeline} />
          )}
        </Card>

        <Card>
          <h2 className="mb-4 font-display text-sm font-medium text-ink-primary">
            Language breakdown (from saved issues)
          </h2>
          {chartData.length === 0 ? (
            <EmptyState
              icon={<Map size={28} />}
              title="Nothing saved yet"
              description="Bookmark a few issues from the Explore page and this chart fills in automatically."
            />
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={chartData} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={90}
                  tick={{ fill: "#9CA39B", fontSize: 12, fontFamily: "IBM Plex Mono" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{ background: "#1C2220", border: "1px solid #2C3431", borderRadius: 8 }}
                  labelStyle={{ color: "#ECE8DE" }}
                />
                <Bar dataKey="count" fill="#D97742" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>
      </div>

      {data.bookmarked_collections.length > 0 && (
        <Card>
          <h2 className="mb-3 font-display text-sm font-medium text-ink-primary">Your collections</h2>
          <div className="flex flex-wrap gap-2">
            {data.bookmarked_collections.map((c) => (
              <span
                key={c.collection_name}
                className="rounded-full border border-base-border bg-base-surface2 px-3 py-1 text-xs text-ink-secondary"
              >
                {c.collection_name} · {c.count}
              </span>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
