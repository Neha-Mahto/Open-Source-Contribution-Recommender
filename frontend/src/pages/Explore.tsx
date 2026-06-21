import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Compass } from "lucide-react";
import { IssueCard } from "../components/IssueCard";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";
import { api, ApiError } from "../lib/api";
import type { RecommendedIssue, IssueOut, Bookmark } from "../types";

type Tab = "recommended" | "all";

export function Explore() {
  const [tab, setTab] = useState<Tab>("recommended");
  const queryClient = useQueryClient();

  const recommendedQuery = useQuery({
    queryKey: ["issues", "recommended"],
    queryFn: () => api.get<RecommendedIssue[]>("/issues/recommended?limit=30"),
    enabled: tab === "recommended",
  });

  const allQuery = useQuery({
    queryKey: ["issues", "all"],
    queryFn: () => api.get<IssueOut[]>("/issues?limit=50"),
    enabled: tab === "all",
  });

  const bookmarksQuery = useQuery({
    queryKey: ["bookmarks"],
    queryFn: () => api.get<Bookmark[]>("/bookmarks"),
  });
  const bookmarkedIssueIds = new Set((bookmarksQuery.data || []).map((b) => b.issue_id));

  const bookmarkMutation = useMutation({
    mutationFn: (issueId: number) => api.post<Bookmark>("/bookmarks", { issue_id: issueId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bookmarks"] }),
    onError: (err) => {
      // 409 just means it's already saved -- not worth surfacing as an error
      if (!(err instanceof ApiError && err.status === 409)) {
        console.error(err);
      }
    },
  });

  const isLoading = tab === "recommended" ? recommendedQuery.isLoading : allQuery.isLoading;
  const issues: (RecommendedIssue | IssueOut)[] =
    tab === "recommended" ? recommendedQuery.data || [] : allQuery.data || [];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-primary">Explore Issues</h1>
        <p className="mt-1 text-sm text-ink-secondary">
          Ranked by language match, label friendliness, repo health, and freshness.
        </p>
      </div>

      <div className="flex gap-1 rounded-lg border border-base-border bg-base-surface p-1 w-fit">
        {(["recommended", "all"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-md px-4 py-1.5 text-sm transition-colors ${
              tab === t ? "bg-blaze text-base-bg" : "text-ink-secondary hover:text-ink-primary"
            }`}
          >
            {t === "recommended" ? "Recommended for you" : "All synced issues"}
          </button>
        ))}
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={5} />
      ) : issues.length === 0 ? (
        <EmptyState
          icon={<Compass size={28} />}
          title="No issues yet"
          description="Sync a repository from the Repositories page to start populating recommendations."
        />
      ) : (
        <div className="flex flex-col gap-3">
          {issues.map((issue) => (
            <IssueCard
              key={issue.id}
              issue={issue}
              matchScore={"match_score" in issue ? issue.match_score : undefined}
              repositoryFullName={"repository_full_name" in issue ? issue.repository_full_name : undefined}
              isBookmarked={bookmarkedIssueIds.has(issue.id)}
              bookmarkPending={bookmarkMutation.isPending}
              onBookmark={() => bookmarkMutation.mutate(issue.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
