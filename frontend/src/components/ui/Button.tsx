import Link from "next/link";
import { clsx } from "clsx";
import type { ComponentProps, ReactNode } from "react";

type Variant = "primary" | "ghost" | "soft" | "quiet";
type Size = "md" | "lg" | "sm";

const styles: Record<Variant, string> = {
  primary:
    "bg-ember text-white hover:bg-ember-hover shadow-[0_8px_22px_rgba(222,74,30,0.28)]",
  ghost: "border border-hairline text-ink hover:bg-surface-2",
  soft: "bg-surface-2 text-ink hover:bg-hairline",
  quiet: "text-ink-2 hover:text-ink hover:bg-surface-2",
};
const sizes: Record<Size, string> = {
  sm: "text-sm px-3.5 py-2",
  md: "text-[0.95rem] px-5 py-3",
  lg: "text-base px-6 py-3.5",
};

function cls(variant: Variant, size: Size, full?: boolean, extra?: string) {
  return clsx(
    "inline-flex items-center justify-center gap-2 rounded-pill font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ember",
    styles[variant],
    sizes[size],
    full && "w-full",
    extra,
  );
}

interface CommonProps {
  variant?: Variant;
  size?: Size;
  full?: boolean;
  children: ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  full,
  className,
  children,
  ...rest
}: CommonProps & ComponentProps<"button">) {
  return (
    <button className={cls(variant, size, full, className)} {...rest}>
      {children}
    </button>
  );
}

export function ButtonLink({
  variant = "primary",
  size = "md",
  full,
  className,
  children,
  ...rest
}: CommonProps & ComponentProps<typeof Link>) {
  return (
    <Link className={cls(variant, size, full, className)} {...rest}>
      {children}
    </Link>
  );
}
