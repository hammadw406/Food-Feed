"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { FoodImage } from "@/components/media/FoodImage";
import { MenuList } from "@/components/restaurant/MenuList";
import { Chip } from "@/components/ui/Chip";
import { Rating } from "@/components/ui/Rating";
import { Price } from "@/components/ui/Price";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { StateBlock } from "@/components/ui/StateBlock";
import { StubNotice } from "@/components/ui/StubNotice";
import { IconBack, IconChevron, IconHeart, IconHeartFill, IconSparkle } from "@/components/ui/icons";
import { readCachedItem } from "@/lib/session/itemCache";
import { useRestaurant } from "@/lib/hooks/useRestaurant";
import { recordDiscovery } from "@/lib/taste/localTaste";
import { trackEvent } from "@/lib/events/queue";
import type { FeedItem } from "@/lib/api/types";

function matchLabel(score: number): string | null {
  if (score >= 0.75) return "Great match";
  if (score >= 0.55) return "Picked for you";
  return null;
}

export function FoodDetailView({ id }: { id: string }) {
  const [item, setItem] = useState<FeedItem | null | undefined>(undefined);
  const [liked, setLiked] = useState(false);

  useEffect(() => {
    setItem(readCachedItem(id));
  }, [id]);

  const { data: restaurant, isLoading: loadingRestaurant } = useRestaurant(
    item?.restaurantId ?? null,
  );

  // Prefer authoritative values from the restaurant menu when available.
  const menuMatch = useMemo(
    () => restaurant?.items.find((it) => it.candidateId === id) ?? null,
    [restaurant, id],
  );

  if (item === undefined) {
    return (
      <div className="mx-auto max-w-content px-5 py-6 lg:px-8">
        <Skeleton className="h-72 w-full rounded-card" />
      </div>
    );
  }

  if (item === null) {
    return (
      <StateBlock
        tone="neutral"
        icon={<IconSparkle width={36} height={36} />}
        title="Open this from the feed"
        body="Dish details are loaded from your feed. Head back to Discover and tap a card."
        actions={<ButtonLink href="/discover">Go to Discover</ButtonLink>}
      />
    );
  }

  const name = item.displayName ?? menuMatch?.displayName ?? "Dish";
  const category = item.category ?? menuMatch?.category ?? null;
  const price = item.price ?? menuMatch?.price ?? null;
  const rating = item.rating ?? menuMatch?.rating ?? null;
  const match = item.score !== null ? matchLabel(item.score) : null;

  const like = () => {
    if (liked) return;
    setLiked(true);
    trackEvent(item.candidateId, "like");
    recordDiscovery(item, "like");
  };

  const otherDishes = restaurant
    ? { ...restaurant, items: restaurant.items.filter((it) => it.candidateId !== id) }
    : null;

  return (
    <div className="mx-auto max-w-content px-5 py-5 lg:px-8">
      <Link
        href="/discover"
        className="mb-4 inline-flex items-center gap-1.5 text-sm font-semibold text-ink-2 hover:text-ink"
      >
        <IconBack width={16} height={16} /> Discover
      </Link>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr] lg:gap-10">
        <div className="overflow-hidden rounded-card border border-hairline shadow-card">
          <FoodImage
            name={name}
            category={category}
            seed={item.candidateId}
            className="h-64 sm:h-80 lg:h-[420px]"
          />
        </div>

        <div>
          {match ? (
            <Chip tone="saffron" className="mb-3">
              <IconSparkle width={11} height={11} /> {match}
            </Chip>
          ) : null}
          <h1 className="font-display text-3xl font-extrabold leading-tight tracking-tight text-ink lg:text-4xl">
            {name}
          </h1>
          {item.restaurantName ? (
            <p className="mt-1.5 text-ink-2">
              {[item.restaurantName, item.area].filter(Boolean).join(" · ")}
            </p>
          ) : null}

          <div className="mt-4 flex flex-wrap items-center gap-2">
            {category ? <Chip>{category}</Chip> : null}
            {rating !== null ? (
              <Chip>
                <Rating value={rating} />
              </Chip>
            ) : null}
          </div>

          <div className="mt-5 flex items-center gap-4 border-y border-hairline py-4">
            <div>
              <div className="text-[0.72rem] uppercase tracking-wide text-ink-3">
                Price
              </div>
              {price !== null ? (
                <Price value={price} className="text-xl" />
              ) : (
                <span className="font-mono text-sm text-ink-3">not listed</span>
              )}
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            {item.restaurantId !== null ? (
              <ButtonLink href={`/restaurants/${item.restaurantId}`} size="lg">
                View this restaurant <IconChevron width={16} height={16} />
              </ButtonLink>
            ) : (
              <Button size="lg" disabled>
                Restaurant unavailable
              </Button>
            )}
            <Button
              variant={liked ? "soft" : "ghost"}
              size="lg"
              onClick={like}
            >
              {liked ? <IconHeartFill width={18} height={18} /> : <IconHeart width={18} height={18} />}
              {liked ? "Saved" : "Save"}
            </Button>
          </div>

          {/* "Why you might like this" is omitted unless the recommendation
              engine actually returns a score for this item. */}
        </div>
      </div>

      {item.restaurantId !== null ? (
        <section className="mt-12">
          <h2 className="mb-4 font-display text-xl font-bold text-ink">
            More from {item.restaurantName ?? "this restaurant"}
          </h2>
          {loadingRestaurant ? (
            <div className="grid gap-3 sm:grid-cols-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-24 rounded-2xl" />
              ))}
            </div>
          ) : otherDishes && otherDishes.items.length ? (
            <MenuList restaurant={otherDishes} />
          ) : (
            <p className="text-sm text-ink-2">No other dishes listed.</p>
          )}
        </section>
      ) : null}

      <section className="mt-12">
        <h2 className="mb-3 font-display text-xl font-bold text-ink">
          Related community posts
        </h2>
        <StubNotice>
          Community content isn&apos;t linked to individual dishes yet (no posts
          API). This section activates when the backend adds it.
        </StubNotice>
      </section>
    </div>
  );
}
