// Mirrors the Pydantic schemas on the backend (app/schemas/*.py).
// Kept as one file since the project is small enough that hunting across
// multiple type files would cost more than it saves.

export interface User {
  id: number;
  github_username: string;
  name: string | null;
  email: string | null;
  avatar_url: string | null;
  known_languages: string[] | null;
  created_at: string;
}

export type IssueDifficulty = "beginner" | "intermediate" | "advanced";

export interface IssueOut {
  id: number;
  title: string;
  url: string;
  labels: string[] | null;
  difficulty: IssueDifficulty;
  comments_count: number;
  is_open: boolean;
}

export interface RecommendedIssue {
  id: number;
  title: string;
  url: string;
  labels: string[] | null;
  difficulty: IssueDifficulty;
  repository_full_name: string | null;
  repository_health_score: number | null;
  match_score: number;
}

export interface RepositoryOut {
  id: number;
  full_name: string;
  description: string | null;
  url: string;
  primary_language: string | null;
  topics: string[] | null;
  stars: number;
  forks: number;
  open_issues_count: number;
  activity_score: number;
  community_score: number;
  friendliness_score: number;
  overall_health_score: number;
  last_synced_at: string | null;
}

export interface RepositorySyncResult {
  repository: RepositoryOut;
  issues_synced: number;
  good_first_issues: number;
}

export type ContributionStatus = "issue_opened" | "pr_submitted" | "pr_merged" | "pr_closed";

export interface Contribution {
  id: number;
  repository_full_name: string;
  issue_or_pr_number: number;
  title: string;
  url: string;
  status: ContributionStatus;
  occurred_at: string;
  created_at: string;
}

export interface ContributionStats {
  issues_opened: number;
  pr_submitted: number;
  pr_merged: number;
  pr_closed: number;
  total: number;
  roadmap_stage: number;
  roadmap_label: string;
}

export interface Bookmark {
  id: number;
  issue_id: number;
  collection_name: string;
  note: string | null;
  created_at: string;
  issue_title: string | null;
  issue_url: string | null;
  repository_full_name: string | null;
}

export interface CollectionSummary {
  collection_name: string;
  count: number;
}

export interface LanguageBreakdownItem {
  language: string;
  count: number;
}

export interface ActivityDay {
  date: string;
  count: number;
}

export interface DashboardOut {
  contribution_stats: ContributionStats;
  language_breakdown: LanguageBreakdownItem[];
  activity_timeline: ActivityDay[];
  bookmarked_collections: CollectionSummary[];
  recent_bookmarks_count: number;
}
