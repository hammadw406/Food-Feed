import Link from "next/link";
import { Logo } from "./Logo";
import { ButtonLink } from "@/components/ui/Button";

export function MarketingNav() {
  return (
    <header className="absolute inset-x-0 top-0 z-30">
      <div className="mx-auto flex max-w-shell items-center gap-6 px-5 py-4 lg:px-8">
        <Logo href="/" />
        <nav className="hidden items-center gap-1 md:flex">
          {[
            ["Discover", "/discover"],
            ["Community", "/community"],
            ["For You", "/for-you"],
          ].map(([label, href]) => (
            <Link
              key={href}
              href={href}
              className="rounded-pill px-3.5 py-2 text-sm font-semibold text-ink-2 hover:bg-surface-2 hover:text-ink"
            >
              {label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-2">
          <ButtonLink href="/login" variant="quiet" size="sm">
            Login
          </ButtonLink>
          <ButtonLink href="/signup" variant="ghost" size="sm">
            Sign Up
          </ButtonLink>
        </div>
      </div>
    </header>
  );
}
