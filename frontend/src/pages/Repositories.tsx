import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MapPin, Plus, Loader2 } from "lucide-react";
import { Card } from "../components/Card";
import { RepoCard } from "../components/RepoCard";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";
import { api, ApiError } from "../lib/api";
import type { RepositoryOut, RepositorySyncResult } from "../types";

export function Repositories() {
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => api.get<RepositoryOut[]>("/repositories?limit=50"),
  });

  const syncMutation = useMutation({
    mutationFn: (name: string) => api.post<RepositorySyncResult>(`/repositories/sync?full_name=${encodeURIComponent(name)}`),
    onSuccess: () => {
      setFullName("");
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["repositories"] });
      queryClient.invalidateQueries({ queryKey: ["issues"] });
    },
    onError: (err) => {
      if (err instanceof ApiError) {
        setError(err.status === 429 ? "GitHub rate limit hit — try again in a bit." : err.message);
      }
    },
  });

  function handleSync(e: React.FormEvent) {
    e.preventDefault();
    if (!fullName.trim()) return;
    syncMutation.mutate(fullName.trim());
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-primary">Repositories</h1>
        <p className="mt-1 text-sm text-ink-secondary">
          Synced repos, ranked by health score. Add one to start surfacing its issues.
        </p>
      </div>

      <Card>
        <form onSubmit={handleSync} className="flex gap-2">
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="owner/repo — e.g. facebook/react"
            className="flex-1 rounded-lg border border-base-border bg-base-surface2 px-3 py-2 font-mono text-sm text-ink-primary placeholder:text-ink-faint focus:border-blaze focus:outline-none"
          />
          <button
            type="submit"
            disabled={syncMutation.isPending}
            className="flex items-center gap-2 rounded-lg bg-blaze px-4 py-2 text-sm font-medium text-base-bg transition-colors hover:bg-blaze-bright disabled:opacity-60"
          >
            {syncMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
            Sync
          </button>
        </form>
        {error && <p className="mt-2 text-sm text-rust">{error}</p>}
        {syncMutation.data && (
          <p className="mt-2 text-sm text-moss">
            Synced {syncMutation.data.issues_synced} issues ({syncMutation.data.good_first_issues} good first
            issues).
          </p>
        )}
      </Card>

      {reposQuery.isLoading ? (
        <LoadingSkeleton rows={3} />
      ) : !reposQuery.data || reposQuery.data.length === 0 ? (
        <EmptyState
          icon={<MapPin size={28} />}
          title="No repositories synced yet"
          description="Type an owner/repo above to pull its open issues and compute a health score."
        />
      ) : (
        <div className="flex flex-col gap-3">
          {reposQuery.data.map((repo) => (
            <RepoCard key={repo.id} repo={repo} />
          ))}
        </div>
      )}
    </div>
  );
}
