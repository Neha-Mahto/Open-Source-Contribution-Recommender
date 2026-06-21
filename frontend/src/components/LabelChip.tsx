export function LabelChip({ label }: { label: string }) {
  return (
    <span className="inline-flex items-center rounded-md border border-base-border bg-base-surface2 px-2 py-0.5 text-xs text-ink-secondary">
      {label}
    </span>
  );
}
