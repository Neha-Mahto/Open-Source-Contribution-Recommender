import { Github } from "lucide-react";
import { Navigate } from "react-router-dom";
import { githubLoginUrl } from "../lib/api";
import { useAuth } from "../lib/auth";

// The one deliberate signature moment in the whole app: a literal trail
// through contour lines, with three waypoints at increasing "elevation"
// (beginner -> intermediate -> advanced) leading to a flag at the summit
// (becoming a contributor). Everything else in the product stays quiet
// so this lands.
function TrailHero() {
  return (
    <svg viewBox="0 0 480 320" className="w-full max-w-xl" aria-hidden="true">
      {[60, 100, 140, 180, 220, 260].map((y, i) => (
        <path
          key={y}
          d={`M0 ${y} Q 120 ${y - 30 + i * 4}, 240 ${y} T 480 ${y}`}
          fill="none"
          stroke="#2C3431"
          strokeWidth="1.5"
        />
      ))}
      <path
        d="M30 280 C 120 260, 160 180, 230 150 C 300 120, 340 90, 420 50"
        fill="none"
        stroke="#D97742"
        strokeWidth="2.5"
        strokeDasharray="6 6"
        strokeLinecap="round"
      />
      <circle cx="30" cy="280" r="7" fill="#7FA66B" />
      <circle cx="230" cy="150" r="7" fill="#D4A017" />
      <circle cx="340" cy="90" r="7" fill="#B5533C" />
      <g transform="translate(412, 36)">
        <line x1="0" y1="0" x2="0" y2="24" stroke="#ECE8DE" strokeWidth="2" />
        <path d="M0 0 L18 5 L0 11 Z" fill="#D97742" />
      </g>
      <text x="30" y="300" fill="#9CA39B" fontSize="11" fontFamily="IBM Plex Mono" textAnchor="middle">
        beginner
      </text>
      <text x="230" y="170" fill="#9CA39B" fontSize="11" fontFamily="IBM Plex Mono" textAnchor="middle">
        intermediate
      </text>
      <text x="340" y="110" fill="#9CA39B" fontSize="11" fontFamily="IBM Plex Mono" textAnchor="middle">
        advanced
      </text>
    </svg>
  );
}

export function Landing() {
  const { isAuthenticated, isLoading } = useAuth();
  if (!isLoading && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-base-bg px-6 text-center">
      <TrailHero />
      <h1 className="mt-6 max-w-2xl font-display text-4xl font-semibold leading-tight text-ink-primary sm:text-5xl">
        Find your next contribution,
        <br />
        not your next dead end.
      </h1>
      <p className="mt-4 max-w-md text-ink-secondary">
        Trailhead ranks open-source issues against your languages, the
        label, and how healthy the repo actually is — so you stop opening
        ten tabs to find one good first issue.
      </p>
      <a
        href={githubLoginUrl()}
        className="mt-8 inline-flex items-center gap-2.5 rounded-lg bg-blaze px-5 py-3 font-display text-sm font-medium text-base-bg transition-colors hover:bg-blaze-bright"
      >
        <Github size={18} />
        Sign in with GitHub
      </a>
      <p className="mt-4 font-mono text-xs text-ink-faint">
        Read-only on your profile. We only act on repos you choose to sync.
      </p>
    </div>
  );
}
