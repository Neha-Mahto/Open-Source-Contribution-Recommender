import type { ReactNode } from "react";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-base-border px-6 py-16 text-center">
      <div className="mb-4 text-ink-faint">{icon}</div>
      <h3 className="font-display text-base font-medium text-ink-primary">{title}</h3>
      <p className="mt-1.5 max-w-sm text-sm text-ink-secondary">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
