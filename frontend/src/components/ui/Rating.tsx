import { IconStar } from "./icons";

/** Renders nothing when rating is null — we never fabricate a rating. */
export function Rating({
  value,
  count,
  className,
}: {
  value: number | null;
  count?: number | null;
  className?: string;
}) {
  if (value === null || Number.isNaN(value)) return null;
  return (
    <span
      className={
        "inline-flex items-center gap-1 font-mono text-[0.78rem] text-ink-2 " +
        (className ?? "")
      }
    >
      <IconStar width={12} height={12} className="text-saffron" />
      {value.toFixed(1)}
      {count ? <span className="text-ink-3">· {count}</span> : null}
    </span>
  );
}
