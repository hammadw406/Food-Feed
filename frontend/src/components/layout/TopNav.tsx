"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import { Logo } from "./Logo";
import { NAV } from "./navConfig";

export function TopNav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-hairline bg-paper/85 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-shell items-center gap-6 px-5 lg:px-8">
        <Logo />
        <nav className="hidden items-center gap-1 md:flex">
          {NAV.slice(0, 3).map(({ href, label }) => {
            const active = pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={clsx(
                  "rounded-pill px-3.5 py-2 text-sm font-semibold transition-colors",
                  active
                    ? "bg-ember-soft text-[#b13c17]"
                    : "text-ink-2 hover:text-ink hover:bg-surface-2",
                )}
              >
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="ml-auto flex items-center gap-3">
          <Link
            href="/profile"
            className={clsx(
              "grid h-9 w-9 place-items-center rounded-pill border text-sm font-bold transition-colors",
              pathname.startsWith("/profile")
                ? "border-ember bg-ember-soft text-[#b13c17]"
                : "border-hairline text-ink-2 hover:bg-surface-2",
            )}
            aria-label="Profile"
          >
            🍽
          </Link>
        </div>
      </div>
    </header>
  );
}
