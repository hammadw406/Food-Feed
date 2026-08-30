import type { ReactNode } from "react";
import { clsx } from "clsx";

/** Shared shell for empty / error / "coming soon" screens. */
export function StateBlock({
  icon,
  title,
  body,
  actions,
  tone = "neutral",
  className,
}: {
  icon: ReactNode;
  title: string;
  body?: ReactNode;
  actions?: ReactNode;
  tone?: "neutral" | "ember" | "saffron" | "basil";
  className?: string;
}) {
  const orb = {
    neutral: "bg-surface-2 text-ink-2",
    ember: "bg-ember-soft text-ember",
    saffron: "bg-saffron-soft text-saffron",
    basil: "bg-basil-soft text-basil",
  }[tone];

  return (
    <div
      className={clsx(
        "mx-auto flex max-w-sm flex-col items-center gap-2 px-6 py-16 text-center",
        className,
      )}
    >
      <div className={clsx("mb-2 grid h-20 w-20 place-items-center rounded-pill", orb)}>
        {icon}
      </div>
      <h2 className="font-display text-xl font-bold text-ink">{title}</h2>
      {body ? <p className="text-sm text-ink-2">{body}</p> : null}
      {actions ? <div className="mt-3 flex flex-wrap justify-center gap-3">{actions}</div> : null}
    </div>
  );
}
