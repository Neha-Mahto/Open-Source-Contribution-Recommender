import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Bookmark as BookmarkIcon, ExternalLink, Trash2 } from "lucide-react";
import { Card } from "../components/Card";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";
import { api } from "../lib/api";
import type { Bookmark } from "../types";

export function Saved() {
  const [activeCollection, setActiveCollection] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const bookmarksQuery = useQuery({
    queryKey: ["bookmarks"],
    queryFn: () => api.get<Bookmark[]>("/bookmarks"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/bookmarks/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarks"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const collections = useMemo(() => {
    const names = new Set((bookmarksQuery.data || []).map((b) => b.collection_name));
    return Array.from(names);
  }, [bookmarksQuery.data]);

  const filtered = (bookmarksQuery.data || []).filter(
    (b) => !activeCollection || b.collection_name === activeCollection
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-primary">Saved Issues</h1>
        <p className="mt-1 text-sm text-ink-secondary">Everything you've bookmarked, by collection.</p>
      </div>

      {collections.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setActiveCollection(null)}
            className={`rounded-full border px-3 py-1 text-xs transition-colors ${
              activeCollection === null
                ? "border-blaze bg-blaze/10 text-blaze"
                : "border-base-border text-ink-secondary hover:text-ink-primary"
            }`}
          >
            All
          </button>
          {collections.map((c) => (
            <button
              key={c}
              onClick={() => setActiveCollection(c)}
              className={`rounded-full border px-3 py-1 text-xs transition-colors ${
                activeCollection === c
                  ? "border-blaze bg-blaze/10 text-blaze"
                  : "border-base-border text-ink-secondary hover:text-ink-primary"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      )}

      {bookmarksQuery.isLoading ? (
        <LoadingSkeleton rows={3} />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<BookmarkIcon size={28} />}
          title="Nothing saved here yet"
          description="Save issues from the Explore page to build out collections like 'Hacktoberfest Targets' or 'Backend Projects'."
        />
      ) : (
        <div className="flex flex-col gap-3">
          {filtered.map((bookmark) => (
            <Card key={bookmark.id} className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <span className="font-mono text-xs text-ink-faint">{bookmark.repository_full_name}</span>
                <a
                  href={bookmark.issue_url || "#"}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-1 flex items-center gap-1.5 font-display text-sm font-medium text-ink-primary hover:text-blaze"
                >
                  {bookmark.issue_title}
                  <ExternalLink size={13} className="text-ink-faint" />
                </a>
                {bookmark.note && <p className="mt-1.5 text-sm text-ink-secondary">{bookmark.note}</p>}
                <span className="mt-2 inline-block rounded-full border border-base-border bg-base-surface2 px-2.5 py-0.5 text-xs text-ink-secondary">
                  {bookmark.collection_name}
                </span>
              </div>
              <button
                onClick={() => deleteMutation.mutate(bookmark.id)}
                aria-label="Remove bookmark"
                className="shrink-0 rounded-lg p-2 text-ink-faint transition-colors hover:bg-rust/10 hover:text-rust"
              >
                <Trash2 size={16} />
              </button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
