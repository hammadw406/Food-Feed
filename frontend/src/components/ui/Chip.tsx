import { clsx } from "clsx";
import type { ReactNode } from "react";

type Tone = "neutral" | "ember" | "saffron" | "basil";

const tones: Record<Tone, string> = {
  neutral: "bg-surface-2 border-hairline text-ink-2",
  ember: "bg-ember-soft border-[#f2cdbd] text-[#b13c17]",
  saffron: "bg-saffron-soft border-[#eed7ac] text-[#9a6a1c]",
  basil: "bg-basil-soft border-[#c3ddc7] text-[#2f6544]",
};

export function Chip({
  children,
  tone = "neutral",
  className,
}: {
  children: ReactNode;
  tone?: Tone;
  className?: string;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-pill border px-2.5 py-1 font-mono text-[0.7rem] leading-none whitespace-nowrap",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
