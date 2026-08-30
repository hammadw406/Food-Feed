/** Formats a numeric price as PKR. Renders nothing when price is null. */
export function Price({
  value,
  className,
}: {
  value: number | null;
  className?: string;
}) {
  if (value === null || Number.isNaN(value)) return null;
  return (
    <span className={"font-display font-bold " + (className ?? "")}>
      Rs {Math.round(value).toLocaleString("en-PK")}
    </span>
  );
}
