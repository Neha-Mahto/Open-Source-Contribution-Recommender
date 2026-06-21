"""
Issue recommendation scoring.

Weights (documented so they're defensible in an interview):
  - Language match:     40%
  - Label match:        30%   (good-first-issue / help-wanted weighted highest)
  - Repository health:  20%
  - Issue freshness:    10%

Each issue gets a 0-100 score per user. This is intentionally a
transparent weighted-sum model, not a black box -- for any recommendation
you can point at the four sub-scores and explain exactly why it ranked
where it did. That matters more in an interview than a marginally
fancier algorithm you can't fully explain.
"""

from datetime import datetime, timezone

from app.models import Issue, User

LANGUAGE_WEIGHT = 0.40
LABEL_WEIGHT = 0.30
HEALTH_WEIGHT = 0.20
FRESHNESS_WEIGHT = 0.10

BEGINNER_LABELS = {"good first issue", "good-first-issue", "beginner friendly", "starter", "easy"}
HELP_WANTED_LABELS = {"help wanted", "help-wanted"}
LOW_VALUE_LABELS = {"wontfix", "duplicate", "invalid", "stale"}


def _language_score(issue: Issue, known_languages: list[str] | None) -> float:
    if not known_languages or not issue.repository or not issue.repository.primary_language:
        return 30.0  # neutral score -- don't punish issues we simply can't evaluate

    repo_language = issue.repository.primary_language.lower()
    user_languages = {lang.lower() for lang in known_languages}

    return 100.0 if repo_language in user_languages else 20.0


def _label_score(issue: Issue) -> float:
    if not issue.labels:
        return 40.0  # untagged issues are a coin flip, not a red flag

    labels = {label.lower() for label in issue.labels}

    if labels & LOW_VALUE_LABELS:
        return 0.0
    if labels & BEGINNER_LABELS:
        return 100.0
    if labels & HELP_WANTED_LABELS:
        return 80.0

    return 40.0


def _freshness_score(issue: Issue) -> float:
    if issue.github_created_at is None:
        return 50.0

    age_days = (datetime.now(timezone.utc) - issue.github_created_at).days

    # Brand-new issues might get claimed by someone else fast; very old
    # issues are often stale/abandoned. Sweet spot: a few days to a few weeks old.
    if age_days < 1:
        return 60.0
    if age_days <= 21:
        return 100.0
    if age_days <= 90:
        return 60.0
    return 30.0


def score_issue_for_user(issue: Issue, user: User) -> float:
    health = issue.repository.overall_health_score if issue.repository else 0.0

    score = (
        _language_score(issue, user.known_languages) * LANGUAGE_WEIGHT
        + _label_score(issue) * LABEL_WEIGHT
        + health * HEALTH_WEIGHT
        + _freshness_score(issue) * FRESHNESS_WEIGHT
    )
    return round(score, 1)


def rank_issues_for_user(issues: list[Issue], user: User) -> list[tuple[Issue, float]]:
    """Returns (issue, score) pairs sorted highest-score first."""
    scored = [(issue, score_issue_for_user(issue, user)) for issue in issues]
    return sorted(scored, key=lambda pair: pair[1], reverse=True)


def classify_difficulty(issue_labels: list[str], comments_count: int) -> str:
    """Used at sync time to tag each issue with a difficulty level for filtering."""
    labels = {label.lower() for label in issue_labels}

    if labels & BEGINNER_LABELS:
        return "beginner"
    if comments_count >= 15:
        return "advanced"  # heavily-discussed issues tend to be contentious or complex
    return "intermediate"
