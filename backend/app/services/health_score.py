"""
Computes the three sub-scores (0-100 each) plus an overall weighted health
score for a repository. Runs every time a repo is synced.

Weights (documented here so they're easy to defend in an interview):
  overall = 0.35 * activity + 0.35 * community + 0.30 * friendliness
"""

import math
from datetime import datetime, timezone

ACTIVITY_WEIGHT = 0.35
COMMUNITY_WEIGHT = 0.35
FRIENDLINESS_WEIGHT = 0.30


def calculate_activity_score(last_commit_at: datetime | None, open_issues_count: int) -> float:
    """
    Rewards repos that are still being actively worked on, using time
    since the last push as the main signal.
    """
    if last_commit_at is None:
        return 0.0

    days_since_commit = (datetime.now(timezone.utc) - last_commit_at).days

    if days_since_commit <= 7:
        recency_score = 100.0
    elif days_since_commit <= 30:
        recency_score = 80.0
    elif days_since_commit <= 90:
        recency_score = 50.0
    elif days_since_commit <= 365:
        recency_score = 20.0
    else:
        recency_score = 5.0

    return round(recency_score, 1)


def calculate_community_score(stars: int, forks: int) -> float:
    """
    Logarithmic scaling so a repo with 50k stars doesn't completely dwarf
    one with 500 -- both can be "healthy", just at different scales.
    """
    star_component = min(math.log10(stars + 1) / math.log10(100_000) * 100, 100)
    fork_component = min(math.log10(forks + 1) / math.log10(20_000) * 100, 100)

    return round(star_component * 0.7 + fork_component * 0.3, 1)


def calculate_friendliness_score(open_issues_count: int, good_first_issue_count: int) -> float:
    """
    Rewards repos that actually tag issues for newcomers, rather than just
    having a big undifferentiated backlog.
    """
    if open_issues_count == 0:
        return 0.0

    ratio = good_first_issue_count / open_issues_count
    # 10%+ of open issues tagged "good first issue" is excellent
    ratio_score = min(ratio / 0.10, 1.0) * 70
    # Bonus just for having ANY beginner-tagged issues at all
    presence_bonus = 30 if good_first_issue_count > 0 else 0

    return round(ratio_score + presence_bonus, 1)


def calculate_overall_health_score(activity: float, community: float, friendliness: float) -> float:
    return round(
        activity * ACTIVITY_WEIGHT + community * COMMUNITY_WEIGHT + friendliness * FRIENDLINESS_WEIGHT, 1
    )
