import Link from "next/link";

export function Logo({ href = "/discover" }: { href?: string }) {
  return (
    <Link
      href={href}
      className="flex items-center gap-2 font-display text-[1.15rem] font-extrabold tracking-tight text-ink"
    >
      <span
        aria-hidden
        className="grid h-7 w-7 place-items-center rounded-lg bg-ember text-sm text-white"
      >
        ◍
      </span>
      Food Feed
    </Link>
  );
}
