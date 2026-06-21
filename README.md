# Open Source Issue Recommender

Built incrementally, in phases that each leave something real and testable
behind:

- **Phase 1** — backend skeleton, database schema, GitHub OAuth login
- **Phase 2** — GitHub API client (cached, rate-limit aware), repository
  health scoring, and the personalized issue recommendation engine
- **Phase 3** — bookmarks/collections, the contribution tracker with a
  4-stage roadmap, and a one-call dashboard aggregate
- **Phase 4** — the frontend: a real React + TypeScript SPA wired up to
  every endpoint above

## Phase 1: the foundation

Backend skeleton, database schema, and GitHub OAuth login. The goal of
this phase is to get a real user authenticating against real GitHub data
and landing in a real Postgres database.

## What's in here

```
backend/
  app/
    main.py                FastAPI app, CORS, startup hook, router registration
    config.py               All env-driven settings (one source of truth)
    database.py             Async SQLAlchemy engine + session dependency
    models/                 ORM tables: User, Repository, Issue, Bookmark, Contribution
    schemas/                Pydantic response models
    routes/
      auth.py                GitHub OAuth login/callback/me endpoints
      repositories.py         Sync, list, detail, rate-limit-status endpoints
      issues.py                List issues + personalized recommendations
      bookmarks.py             Save/list/delete bookmarked issues, by collection
      contributions.py         Log + track contribution events, roadmap stats
      dashboard.py             One-call aggregate view for the main dashboard
    services/
      github_oauth.py         Talks to GitHub's OAuth handshake endpoints
      github_client.py         Talks to GitHub's REST API (repos/issues), Redis-cached, rate-limit aware
      redis_client.py          Shared Redis connection
      health_score.py          Repository health scoring (activity/community/friendliness)
      recommendation.py        Issue recommendation scoring + difficulty classification
      repository_sync.py       Orchestrates: fetch from GitHub -> store -> score
      roadmap.py                Maps contribution counts onto the 4-stage roadmap
    repositories/
      user_repository.py            Data-access layer for User
      repository_repository.py       Data-access layer for Repository
      issue_repository.py            Data-access layer for Issue
      bookmark_repository.py         Data-access layer for Bookmark
      contribution_repository.py     Data-access layer for Contribution
    utils/
      github_helpers.py          Shared helpers (GitHub timestamp parsing)
    core/
      security.py              JWT issue/verify
      deps.py                   get_current_user FastAPI dependency
  requirements.txt
  .env.example
docker-compose.yml          Postgres + Redis for local dev
frontend/
  src/
    main.tsx                 Entry point, React Query + Router + Auth providers
    App.tsx                  Route definitions, protected-route wrapper
    types.ts                 TypeScript types mirroring the backend's Pydantic schemas
    index.css                Design tokens, focus states, reduced-motion handling
    lib/
      api.ts                  Fetch wrapper, attaches the JWT to every request
      auth.tsx                 Auth context (current user, login state, logout)
    components/
      HealthRing.tsx           Signature element: 3-ring repo health visualization
      RoadmapTrail.tsx          4-waypoint contribution journey visualization
      ActivityHeatmap.tsx       90-day contribution calendar
      IssueCard.tsx / RepoCard.tsx / DifficultyBadge.tsx / LabelChip.tsx
      Layout.tsx                Sidebar nav + page shell for authenticated routes
      Card.tsx / EmptyState.tsx / LoadingSkeleton.tsx
    pages/
      Landing.tsx, AuthCallback.tsx, Dashboard.tsx, Explore.tsx,
      Repositories.tsx, RepositoryDetail.tsx, Saved.tsx
  package.json
  .env.example
```

## Why it's structured this way

- **routes/** only handle HTTP concerns (parse request, call a service, return response).
- **services/** hold business logic and talk to external APIs (GitHub).
- **repositories/** are the only place that touches the database directly.
- **models/** are pure SQLAlchemy ORM — no logic.

This separation is what lets you say "clean architecture" in an interview
and actually back it up by pointing at the folder structure.

## Database schema (Phase 1)

| Table | Purpose |
|---|---|
| `users` | GitHub profile + known languages (used later for matching) |
| `repositories` | Cached GitHub repo metadata + health score columns (scores computed in Phase 2) |
| `issues` | Cached GitHub issues, labels, difficulty tag |
| `bookmarks` | User-saved issues, grouped into named collections |
| `contributions` | Tracked issue/PR activity per user |

All five tables exist now so the schema doesn't need to change shape later
— Phase 2 fills in the *logic* (recommendation scoring, health score calc),
not new tables.

## Setup

### 1. Create a GitHub OAuth App
Go to https://github.com/settings/developers → "New OAuth App":
- Homepage URL: `http://localhost:5173`
- Authorization callback URL: `http://localhost:8000/auth/github/callback`

Copy the Client ID and generate a Client Secret.

### 2. Start Postgres + Redis
```bash
docker compose up -d
```

### 3. Configure the backend
```bash
cd backend
cp .env.example .env
# edit .env: paste in your GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
# and replace JWT_SECRET with a real random string
```

### 4. Install dependencies and run
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is now live at `http://localhost:8000`. Tables are created
automatically on startup (fine for dev — see "Migrations" below for prod).

### 5. Test the login flow
Open in your browser:
```
http://localhost:8000/auth/github/login
```
This redirects you to GitHub's consent screen, then back to a callback URL
that issues a JWT and redirects to `FRONTEND_URL/auth/callback?token=...`.
Since the frontend doesn't exist yet, that last redirect will 404 in your
browser — that's expected. Grab the `token` from the URL bar and test it:

```bash
curl http://localhost:8000/auth/me -H "Authorization: Bearer <paste token here>"
```

You should get back your GitHub profile as JSON.

### 6. Explore the auto-generated API docs
```
http://localhost:8000/docs
```

## Phase 2: the recommendation engine

Phase 2 adds the part that makes this an actual recommender, not just auth + schema.

### New endpoints

| Endpoint | What it does |
|---|---|
| `POST /repositories/sync?full_name=owner/repo` | Pulls a repo + its open issues from GitHub, stores them, computes health scores |
| `GET /repositories` | List synced repos, ranked by health score |
| `GET /repositories/{id}` | Single repo detail |
| `GET /repositories/meta/rate-limit` | Check remaining GitHub API quota for your token |
| `GET /issues` | List synced open issues |
| `GET /issues/recommended` | **Personalized** issue recommendations for the logged-in user |

### How repository health scoring works

Each synced repo gets three 0–100 sub-scores, combined into one overall score:

```
overall = 0.35 * activity + 0.35 * community + 0.30 * friendliness
```

- **Activity** — based on time since the last push (`pushed_at`). Recent activity scores high; a repo untouched for a year scores near zero.
- **Community** — log-scaled stars + forks, so a 50k-star repo doesn't completely dwarf a 500-star one on the chart.
- **Friendliness** — the ratio of `good first issue`-labeled issues to total open issues, plus a flat bonus just for having any at all.

See `app/services/health_score.py` for the exact formulas — they're deliberately simple and commented so you can defend every number in an interview.

### How issue recommendation scoring works

Each issue gets scored per-user as a weighted sum:

```
score = 0.40 * language_match + 0.30 * label_match + 0.20 * repo_health + 0.10 * freshness
```

- **Language match** — does the repo's primary language appear in the user's `known_languages`?
- **Label match** — `good first issue` scores highest, `help wanted` next, low-value labels (`wontfix`, `duplicate`, `stale`) score zero.
- **Repo health** — pulls in the score described above.
- **Freshness** — issues a few days to a few weeks old score highest (new enough to still be open, old enough that the obvious takers have passed).

This is intentionally a transparent weighted-sum model, not a black box — `app/services/recommendation.py` has the full breakdown, and you can point at any single recommendation and explain exactly why it ranked where it did.

### Caching and rate-limit handling

`app/services/github_client.py` wraps every GitHub REST call in a Redis cache-aside pattern (10 min TTL for repo metadata, 3 min for issues — issues change faster). If GitHub's rate limit is exhausted, the client raises a typed `GitHubRateLimitError` that the route layer turns into a clean `429` response with a `Try again after <time>` message, instead of a raw crash.

Note: GitHub's unauthenticated rate limit is only 60 requests/hour. Once a user is logged in, their own GitHub access token (stored server-side after OAuth) is used automatically, raising the limit to 5,000/hour.

### Try it yourself

After completing the Phase 1 setup and logging in to get a JWT:

```bash
# Sync a real repo (pick something with actual open issues)
curl -X POST "http://localhost:8000/repositories/sync?full_name=facebook/react" \
  -H "Authorization: Bearer <your token>"

# See it ranked by health score
curl http://localhost:8000/repositories

# Get personalized recommendations
curl http://localhost:8000/issues/recommended -H "Authorization: Bearer <your token>"
```

## Phase 3: bookmarks, contribution tracking, and the dashboard

Phase 3 adds the features that make someone come back to this app
repeatedly, instead of using it once to find one issue.

### New endpoints

| Endpoint | What it does |
|---|---|
| `POST /bookmarks` | Save an issue into a named collection (e.g. "Hacktoberfest Targets") |
| `GET /bookmarks` | List your saved issues, optionally filtered by collection |
| `GET /bookmarks/collections` | List your collection names with counts |
| `DELETE /bookmarks/{id}` | Remove a saved issue |
| `POST /contributions` | Log a contribution event (issue opened / PR submitted / merged / closed) |
| `GET /contributions` | List your tracked events, optionally filtered by status |
| `GET /contributions/stats` | Aggregated counts + your current roadmap stage |
| `PATCH /contributions/{id}` | Update status as a contribution progresses |
| `GET /dashboard` | One call: contribution stats, roadmap stage, activity timeline, language breakdown, bookmark collections |

### The contribution roadmap

Four stages, derived purely from what's in the `contributions` table — no separate "roadmap" data to keep in sync:

1. **Explore repositories** — no tracked activity yet
2. **Solve your first issue** — at least one `issue_opened` event
3. **Submit a pull request** — at least one `pr_submitted` event
4. **Become a contributor** — at least one `pr_merged` event

The stage is recalculated live every time `/contributions/stats` or
`/dashboard` is called — there's no stored "current stage" field to drift
out of sync with reality. See `app/services/roadmap.py`.

### Why bookmarks don't just reuse "favorites"

Bookmarks carry a `collection_name`, so the same save-an-issue action
doubles as the basis for the "Saved Repositories" / collections feature
from the original spec (e.g. "Backend Projects", "Hacktoberfest
Targets") without needing a separate collections table — `GROUP BY
collection_name` does the work.

### Try it yourself

```bash
# Bookmark an issue into a collection
curl -X POST http://localhost:8000/bookmarks \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"issue_id": 1, "collection_name": "Hacktoberfest Targets"}'

# Log that you opened an issue
curl -X POST http://localhost:8000/contributions \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"repository_full_name": "facebook/react", "issue_or_pr_number": 123, "title": "Fix typo in docs", "url": "https://github.com/facebook/react/issues/123", "status": "issue_opened"}'

# Check your roadmap stage
curl http://localhost:8000/contributions/stats -H "Authorization: Bearer <token>"

# Pull everything the dashboard needs in one call
curl http://localhost:8000/dashboard -H "Authorization: Bearer <token>"
```

## Phase 4: the frontend

A real React + TypeScript + Vite SPA — not a mockup. It's wired up to every
endpoint built in Phases 1–3.

### Design direction

The product's own content — issue **difficulty** (beginner/intermediate/
advanced), repo **health**, a 4-**stage** contribution journey — already
reads like terrain and a trail. So the UI leans into that instead of
generic SaaS-dashboard styling:

- **Color** — a dark, warm slate background (`#14181A`) instead of
  near-black-plus-neon, with a rust/blaze accent (`#D97742`) standing in
  for a trail blaze mark, and moss/ochre/rust as a three-tone difficulty
  and health scale.
- **Type** — Space Grotesk (display), IBM Plex Sans (body), IBM Plex Mono
  (scores, repo names, anything data-shaped) — a technical, not-default
  pairing.
- **Signature element** — a repo's health score renders as three
  concentric contour rings (`HealthRing.tsx`), one per sub-score, echoing
  a topographic map. The contribution roadmap renders as a literal trail
  with four waypoints (`RoadmapTrail.tsx`).

### Pages

| Route | What's there |
|---|---|
| `/` | Landing page, sign-in with GitHub |
| `/auth/callback` | Captures the JWT after the OAuth redirect, then forwards to the dashboard |
| `/dashboard` | Roadmap trail, contribution stat cards, 90-day activity heatmap, language breakdown chart, collection summary |
| `/explore` | Recommended issues (personalized ranking) vs. all synced issues, with one-click bookmarking |
| `/repositories` | Sync a new `owner/repo`, see all synced repos ranked by health score |
| `/repositories/:id` | Health ring detail, repo stats, that repo's open issues |
| `/saved` | Bookmarked issues, filterable by collection |

### Setup

```bash
cd frontend
cp .env.example .env   # points at http://localhost:8000 by default
npm install
npm run dev
```

Visit `http://localhost:5173`. Make sure the backend is running first
(see the Phase 1 setup above) — the frontend's CORS allowlist on the
backend side already expects this exact origin.

### Notable implementation choices

- **Auth token handling** — the backend redirects to
  `/auth/callback?token=<jwt>` after GitHub login; `AuthCallback.tsx`
  grabs it once and stores it in `localStorage`, then every API call in
  `lib/api.ts` attaches it as a Bearer token. (This is a real deployed
  app the user runs locally — not an embedded preview — so `localStorage`
  is the normal, correct choice here, unlike in a sandboxed component.)
- **React Query** for all data fetching — handles loading/error states
  and cache invalidation (e.g. bookmarking an issue invalidates the
  bookmarks list and the dashboard in one line) without hand-rolled
  `useEffect` chains.
- **Duplicate bookmarks** — the backend returns `409` if an issue's
  already saved; the frontend treats that as a no-op rather than an error
  banner, since the end state the user wanted ("this is saved") is
  already true.

## What's NOT in this project (on purpose, for now)

- Scheduled background sync (sync only happens when triggered manually, via the UI or the API)
- Notifications (new good-first-issue alerts, PR status changes)
- Alembic migrations (using `create_all` for now)
- Settings page (no user-editable preferences yet — `known_languages` is set at login and not user-editable from the UI)

These are the natural "Phase 5" set if you want to keep extending it —
but the four phases above already cover everything that makes a strong
story in an interview: auth, API design, caching, rate limiting,
database schema design, a transparent scoring algorithm, and a real
frontend talking to all of it.
