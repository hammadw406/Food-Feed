import { clsx } from "clsx";
import {
  cuisineFamily,
  FAMILY_STYLE,
  monogram,
  seedFraction,
} from "@/lib/media/foodVisual";

/**
 * Food image slot. The backend exposes no media_url today, so this always
 * renders the deterministic fallback treatment (cuisine colour + monogram).
 * `src` is accepted for the day the backend adds real photos — pass it and
 * the real image renders instead.
 */
export function FoodImage({
  name,
  category,
  seed,
  src,
  className,
  rounded = "rounded-none",
}: {
  name?: string | null;
  category?: string | null;
  seed: string;
  src?: string | null;
  className?: string;
  rounded?: string;
}) {
  const fam = cuisineFamily(category || name);
  const style = FAMILY_STYLE[fam];
  const f = seedFraction(seed);
  const angle = Math.round(120 + f * 120);
  const bx = Math.round(15 + f * 55);
  const by = Math.round(10 + seedFraction(seed + "y") * 50);

  if (src) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={src}
        alt={name ?? "Food"}
        className={clsx("h-full w-full object-cover", rounded, className)}
      />
    );
  }

  return (
    <div
      role="img"
      aria-label={`${name ?? "Food"} — image not available`}
      className={clsx(
        "relative flex h-full w-full items-center justify-center overflow-hidden",
        rounded,
        className,
      )}
      style={{
        backgroundImage: `radial-gradient(60% 60% at ${bx}% ${by}%, rgba(255,255,255,.28), transparent 60%), radial-gradient(70% 70% at ${100 - bx}% ${100 - by}%, rgba(0,0,0,.28), transparent 62%), linear-gradient(${angle}deg, ${style.from}, ${style.to})`,
      }}
    >
      <span className="select-none font-display text-[2.2rem] font-extrabold tracking-tight text-white/90 drop-shadow">
        {monogram(name)}
      </span>
      <span className="absolute bottom-2 left-2 rounded-pill bg-black/35 px-2 py-0.5 font-mono text-[0.6rem] uppercase tracking-wide text-white/80 backdrop-blur-sm">
        {style.label}
      </span>
    </div>
  );
}
