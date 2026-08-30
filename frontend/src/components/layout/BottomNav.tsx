"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import { NAV } from "./navConfig";

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-hairline bg-paper/95 pb-[env(safe-area-inset-bottom)] backdrop-blur md:hidden">
      <ul className="mx-auto flex max-w-md">
        {NAV.map(({ href, label, Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <li key={href} className="flex-1">
              <Link
                href={href}
                className={clsx(
                  "flex flex-col items-center gap-1 py-2.5 text-[0.66rem] font-semibold",
                  active ? "text-ember" : "text-ink-3",
                )}
              >
                <Icon width={22} height={22} />
                {label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
