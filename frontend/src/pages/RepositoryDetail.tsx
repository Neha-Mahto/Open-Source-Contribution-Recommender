import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Star, GitFork, ExternalLink } from "lucide-react";
import { Card } from "../components/Card";
import { HealthRing, HealthRingLegend } from "../components/HealthRing";
import { IssueCard } from "../components/IssueCard";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";
import { api } from "../lib/api";
import type { RepositoryOut, IssueOut } from "../types";
import { Inbox } from "lucide-react";

export function RepositoryDetail() {
  const { id } = useParams<{ id: string }>();

  const repoQuery = useQuery({
    queryKey: ["repository", id],
    queryFn: () => api.get<RepositoryOut>(`/repositories/${id}`),
  });

  const issuesQuery = useQuery({
    queryKey: ["issues", "repository", id],
    queryFn: () => api.get<IssueOut[]>(`/issues?repository_id=${id}&limit=200`),
    enabled: !!id,
  });

  if (repoQuery.isLoading) return <LoadingSkeleton rows={3} />;
  const repo = repoQuery.data;
  if (!repo) return null;

  const repoIssues = issuesQuery.data || [];

  return (
    <div className="flex flex-col gap-6">
      <Link to="/repositories" className="flex items-center gap-1.5 text-sm text-ink-secondary hover:text-ink-primary">
        <ArrowLeft size={14} /> Back to repositories
      </Link>

      <Card>
        <div className="flex items-start justify-between gap-6">
          <div>
            <h1 className="font-display text-2xl font-semibold text-ink-primary">{repo.full_name}</h1>
            {repo.description && <p className="mt-2 max-w-xl text-sm text-ink-secondary">{repo.description}</p>}
            <div className="mt-3 flex items-center gap-4 font-mono text-xs text-ink-faint">
              {repo.primary_language && <span>{repo.primary_language}</span>}
              <span className="flex items-center gap-1"><Star size={12} /> {repo.stars.toLocaleString()}</span>
              <span className="flex items-center gap-1"><GitFork size={12} /> {repo.forks.toLocaleString()}</span>
              <span>{repo.open_issues_count} open issues</span>
            </div>
            <a
              href={repo.url}
              target="_blank"
              rel="noreferrer"
              className="mt-3 inline-flex items-center gap-1.5 text-sm text-blaze hover:text-blaze-bright"
            >
              View on GitHub <ExternalLink size={13} />
            </a>
          </div>
          <div className="flex flex-col items-center gap-3">
            <HealthRing
              activity={repo.activity_score}
              community={repo.community_score}
              friendliness={repo.friendliness_score}
              overall={repo.overall_health_score}
            />
            <HealthRingLegend />
          </div>
        </div>
      </Card>

      <div>
        <h2 className="mb-3 font-display text-sm font-medium text-ink-primary">Open issues in this repo</h2>
        {issuesQuery.isLoading ? (
          <LoadingSkeleton rows={3} />
        ) : repoIssues.length === 0 ? (
          <EmptyState icon={<Inbox size={28} />} title="No issues synced" description="Try re-syncing this repository." />
        ) : (
          <div className="flex flex-col gap-3">
            {repoIssues.map((issue) => (
              <IssueCard key={issue.id} issue={issue} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
