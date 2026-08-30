"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { clsx } from "clsx";
import { FoodImage } from "@/components/media/FoodImage";
import { Chip } from "@/components/ui/Chip";
import { Rating } from "@/components/ui/Rating";
import { Price } from "@/components/ui/Price";
import { IconHeart, IconHeartFill, IconOpen, IconSkip, IconSparkle } from "@/components/ui/icons";
import { useInteractionTracker } from "./useInteractionTracker";
import { cacheItem } from "@/lib/session/itemCache";
import { recordDiscovery } from "@/lib/taste/localTaste";
import type { FeedItem } from "@/lib/api/types";

/** Human label for a real ranking score. Only used when score != null. */
function matchLabel(score: number): string | null {
  if (score >= 0.75) return "Great match";
  if (score >= 0.55) return "Picked for you";
  return null;
}

export function FoodCard({
  item,
  layout = "grid",
  onSkip,
}: {
  item: FeedItem;
  layout?: "grid" | "wide";
  onSkip?: (id: string) => void;
}) {
  const router = useRouter();
  const { ref, markResolved } = useInteractionTracker(item.candidateId);
  const [liked, setLiked] = useState(false);
  const [gone, setGone] = useState(false);

  const match = item.score !== null ? matchLabel(item.score) : null;

  const open = () => {
    markResolved("tap");
    recordDiscovery(item, "tap");
    cacheItem(item);
    router.push(`/foods/${encodeURIComponent(item.candidateId)}`);
  };

  const like = () => {
    if (liked) return;
    setLiked(true);
    markResolved("like");
    recordDiscovery(item, "like");
  };

  const skip = () => {
    setGone(true);
    onSkip?.(item.candidateId);
  };

  if (gone) return null;

  return (
    <article
      ref={ref as React.RefObject<HTMLElement>}
      className={clsx(
        "group flex flex-col overflow-hidden rounded-card border border-hairline bg-surface shadow-card transition-shadow hover:shadow-pop",
        layout === "wide" && "sm:flex-row",
      )}
    >
      <div
        className={clsx(
          "relative cursor-pointer",
          layout === "wide" ? "sm:w-64 sm:shrink-0" : "",
        )}
        onClick={open}
      >
        <FoodImage
          name={item.displayName}
          category={item.category}
          seed={item.candidateId}
          className={clsx(
            layout === "wide" ? "h-44 sm:h-full" : "h-48 lg:h-52",
          )}
        />
        {match ? (
          <span className="absolute left-3 top-3 inline-flex items-center gap-1 rounded-pill bg-black/55 px-2 py-1 font-mono text-[0.66rem] text-white backdrop-blur-sm">
            <IconSparkle width={11} height={11} /> {match}
          </span>
        ) : null}
      </div>

      <div className="flex flex-1 flex-col p-4">
        <button
          onClick={open}
          className="text-left font-display text-[1.15rem] font-bold leading-tight text-ink hover:text-ember"
        >
          {item.displayName ?? "Dish"}
        </button>
        <p className="mt-0.5 text-sm text-ink-2">
          {[item.restaurantName, item.area].filter(Boolean).join(" · ") || "—"}
        </p>

        <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
          {item.category ? <Chip>{item.category}</Chip> : null}
          {item.rating !== null ? (
            <Chip>
              <Rating value={item.rating} />
            </Chip>
          ) : null}
        </div>

        <div className="mt-auto flex items-center justify-between border-t border-hairline pt-3">
          {item.price !== null ? (
            <Price value={item.price} className="text-[1.05rem]" />
          ) : (
            <span className="font-mono text-xs text-ink-3">price n/a</span>
          )}
          <div className="flex gap-2">
            <button
              onClick={skip}
              aria-label="Not for me"
              className="grid h-10 w-10 place-items-center rounded-pill border border-hairline text-ink-2 hover:bg-surface-2"
            >
              <IconSkip width={18} height={18} />
            </button>
            <button
              onClick={like}
              aria-label={liked ? "Saved" : "Save"}
              className={clsx(
                "grid h-10 w-10 place-items-center rounded-pill border transition-colors",
                liked
                  ? "border-ember bg-ember text-white"
                  : "border-hairline text-ink-2 hover:bg-surface-2",
              )}
            >
              {liked ? <IconHeartFill width={18} height={18} /> : <IconHeart width={18} height={18} />}
            </button>
            <button
              onClick={open}
              aria-label="Open"
              className="grid h-10 w-10 place-items-center rounded-pill border border-hairline text-ink-2 hover:bg-surface-2"
            >
              <IconOpen width={18} height={18} />
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
