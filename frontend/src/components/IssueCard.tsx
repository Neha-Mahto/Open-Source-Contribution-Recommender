import { Bookmark as BookmarkIcon, ExternalLink } from "lucide-react";
import { DifficultyBadge } from "./DifficultyBadge";
import { LabelChip } from "./LabelChip";
import type { RecommendedIssue, IssueOut } from "../types";

interface IssueCardProps {
  issue: RecommendedIssue | IssueOut;
  matchScore?: number;
  repositoryFullName?: string | null;
  onBookmark?: () => void;
  isBookmarked?: boolean;
  bookmarkPending?: boolean;
}

export function IssueCard({
  issue,
  matchScore,
  repositoryFullName,
  onBookmark,
  isBookmarked,
  bookmarkPending,
}: IssueCardProps) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-xl border border-base-border bg-base-surface p-4 transition-colors hover:border-blaze/40">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          {repositoryFullName && (
            <span className="font-mono text-xs text-ink-faint">{repositoryFullName}</span>
          )}
          {matchScore !== undefined && (
            <span className="font-mono text-xs text-blaze">match {matchScore.toFixed(0)}</span>
          )}
        </div>
        <a
          href={issue.url}
          target="_blank"
          rel="noreferrer"
          className="mt-1 inline-flex items-center gap-1.5 font-display text-sm font-medium text-ink-primary hover:text-blaze"
        >
          {issue.title}
          <ExternalLink size={13} className="text-ink-faint" />
        </a>
        <div className="mt-2 flex flex-wrap items-center gap-1.5">
          <DifficultyBadge difficulty={issue.difficulty} />
          {issue.labels?.slice(0, 3).map((label) => <LabelChip key={label} label={label} />)}
        </div>
      </div>
      {onBookmark && (
        <button
          onClick={onBookmark}
          disabled={bookmarkPending}
          aria-label={isBookmarked ? "Remove bookmark" : "Save issue"}
          className={`shrink-0 rounded-lg border p-2 transition-colors ${
            isBookmarked
              ? "border-blaze/40 bg-blaze/10 text-blaze"
              : "border-base-border text-ink-faint hover:border-blaze/40 hover:text-blaze"
          }`}
        >
          <BookmarkIcon size={16} fill={isBookmarked ? "currentColor" : "none"} />
        </button>
      )}
    </div>
  );
}
