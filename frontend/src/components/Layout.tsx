import { NavLink, Outlet } from "react-router-dom";
import { Compass, LayoutDashboard, MapPin, Bookmark, LogOut } from "lucide-react";
import { useAuth } from "../lib/auth";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/explore", label: "Explore Issues", icon: Compass },
  { to: "/repositories", label: "Repositories", icon: MapPin },
  { to: "/saved", label: "Saved", icon: Bookmark },
];

export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-base-bg">
      <aside className="flex w-60 shrink-0 flex-col border-r border-base-border px-4 py-6">
        <div className="mb-8 flex items-center gap-2 px-2">
          <span className="font-display text-lg font-semibold text-ink-primary">Trailhead</span>
        </div>

        <nav className="flex flex-1 flex-col gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg border-l-2 px-3 py-2.5 text-sm transition-colors ${
                  isActive
                    ? "border-blaze bg-blaze/10 text-ink-primary"
                    : "border-transparent text-ink-secondary hover:bg-base-surface hover:text-ink-primary"
                }`
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-base-border pt-4">
          {user && (
            <div className="mb-3 flex items-center gap-2.5 px-2">
              {user.avatar_url && (
                <img src={user.avatar_url} alt="" className="h-8 w-8 rounded-full" />
              )}
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-ink-primary">
                  {user.name || user.github_username}
                </p>
                <p className="truncate font-mono text-xs text-ink-faint">@{user.github_username}</p>
              </div>
            </div>
          )}
          <button
            onClick={logout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-ink-secondary transition-colors hover:bg-base-surface hover:text-rust"
          >
            <LogOut size={16} />
            Log out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto px-10 py-8">
        <Outlet />
      </main>
    </div>
  );
}
