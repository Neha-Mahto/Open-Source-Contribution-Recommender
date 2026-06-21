import { Link } from "react-router-dom";
import { Star, GitFork } from "lucide-react";
import { HealthRing } from "./HealthRing";
import type { RepositoryOut } from "../types";

export function RepoCard({ repo }: { repo: RepositoryOut }) {
  return (
    <Link
      to={`/repositories/${repo.id}`}
      className="flex items-center gap-5 rounded-xl border border-base-border bg-base-surface p-5 transition-colors hover:border-blaze/40"
    >
      <HealthRing
        activity={repo.activity_score}
        community={repo.community_score}
        friendliness={repo.friendliness_score}
        overall={repo.overall_health_score}
        size={84}
      />
      <div className="min-w-0 flex-1">
        <h3 className="font-display text-base font-medium text-ink-primary">{repo.full_name}</h3>
        {repo.description && (
          <p className="mt-1 line-clamp-2 text-sm text-ink-secondary">{repo.description}</p>
        )}
        <div className="mt-2 flex items-center gap-4 font-mono text-xs text-ink-faint">
          {repo.primary_language && <span>{repo.primary_language}</span>}
          <span className="flex items-center gap-1">
            <Star size={12} /> {repo.stars.toLocaleString()}
          </span>
          <span className="flex items-center gap-1">
            <GitFork size={12} /> {repo.forks.toLocaleString()}
          </span>
          <span>{repo.open_issues_count} open issues</span>
        </div>
      </div>
    </Link>
  );
}
