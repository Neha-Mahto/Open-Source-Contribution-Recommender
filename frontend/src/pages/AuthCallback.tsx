import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { setToken } from "../lib/api";
import { useAuth } from "../lib/auth";

// The backend redirects here after a successful GitHub login, with our
// own JWT in the query string (see backend/app/routes/auth.py).
// We grab it once, store it, and move on -- the token never sits in the
// URL bar for longer than this one render.
export function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refetchUser } = useAuth();

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      setToken(token);
      refetchUser().then(() => navigate("/dashboard", { replace: true }));
    } else {
      navigate("/", { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-base-bg">
      <p className="font-mono text-sm text-ink-secondary">Signing you in…</p>
    </div>
  );
}
