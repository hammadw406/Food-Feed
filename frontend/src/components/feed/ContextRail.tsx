"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Chip } from "@/components/ui/Chip";
import { IconChevron, IconSparkle } from "@/components/ui/icons";
import { getObservedCategories, totalInteractions } from "@/lib/taste/localTaste";
import type { FeedItem } from "@/lib/api/types";

/**
 * Desktop-only right rail. Everything here is REAL data:
 *  - "What you've been opening" = local device log (labelled as such; no %s)
 *  - "Places in your feed" = unique restaurants from the loaded feed items
 * No invented statistics, no fake "top rated nearby" ranking.
 */
export function ContextRail({ items }: { items: FeedItem[] }) {
  const [observed, setObserved] = useState<{ label: string; count: number }[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    setObserved(getObservedCategories());
    setTotal(totalInteractions());
  }, [items.length]);

  const places = dedupePlaces(items).slice(0, 6);

  return (
    <aside className="hidden w-72 shrink-0 space-y-5 xl:block">
      <section className="rounded-card border border-hairline bg-surface p-4">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-[1.05rem] font-bold">Your taste</h3>
          <Link
            href="/for-you"
            className="font-mono text-[0.7rem] text-ember hover:underline"
          >
            details
          </Link>
        </div>
        {total >= 3 ? (
          <>
            <p className="mt-1 text-[0.82rem] text-ink-2">
              Based on {total} dishes you&apos;ve opened or saved on this device.
            </p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {observed.map((o) => (
                <Chip key={o.label} tone="saffron">
                  {o.label}
                </Chip>
              ))}
            </div>
          </>
        ) : (
          <p className="mt-1 text-[0.82rem] text-ink-2">
            React to a few dishes and your leanings show up here. The feed itself
            personalises server-side as you go.
          </p>
        )}
      </section>

      <section className="rounded-card border border-hairline bg-surface p-4">
        <h3 className="font-display text-[1.05rem] font-bold">Places in your feed</h3>
        <ul className="mt-3 space-y-1">
          {places.map((p) => (
            <li key={p.id}>
              <Link
                href={`/restaurants/${p.id}`}
                className="flex items-center justify-between rounded-lg px-2 py-2 text-sm hover:bg-surface-2"
              >
                <span className="min-w-0">
                  <span className="block truncate font-semibold text-ink">
                    {p.name}
                  </span>
                  <span className="block truncate text-[0.76rem] text-ink-3">
                    {p.area ?? "DHA, Lahore"}
                  </span>
                </span>
                <IconChevron width={15} height={15} className="shrink-0 text-ink-3" />
              </Link>
            </li>
          ))}
          {!places.length ? (
            <li className="px-2 py-2 text-[0.82rem] text-ink-3">
              Loading dishes…
            </li>
          ) : null}
        </ul>
      </section>

      <section className="rounded-card border border-[#eed7ac] bg-saffron-soft p-4 text-[#7c5a1c]">
        <IconSparkle width={16} height={16} />
        <p className="mt-1.5 text-[0.82rem]">
          The more you view, skip, save and open, the sharper the feed gets — the
          ranking updates on the server after every interaction.
        </p>
      </section>
    </aside>
  );
}

function dedupePlaces(items: FeedItem[]) {
  const seen = new Set<number>();
  const out: { id: number; name: string; area: string | null }[] = [];
  for (const i of items) {
    if (i.restaurantId === null || seen.has(i.restaurantId)) continue;
    seen.add(i.restaurantId);
    out.push({
      id: i.restaurantId,
      name: i.restaurantName ?? "Restaurant",
      area: i.area,
    });
  }
  return out;
}
