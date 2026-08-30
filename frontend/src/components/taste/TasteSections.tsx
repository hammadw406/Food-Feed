"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FoodImage } from "@/components/media/FoodImage";
import { Chip } from "@/components/ui/Chip";
import { StubNotice } from "@/components/ui/StubNotice";
import { IconSparkle } from "@/components/ui/icons";
import { getFeed } from "@/lib/api/feed";
import { useSession } from "@/lib/session/SessionProvider";
import {
  getObservedCategories,
  getRecentDiscoveries,
  totalInteractions,
  type TasteLogEntry,
} from "@/lib/taste/localTaste";

/** Real signal from the backend: is the feed still in cold-start? */
export function FeedLearningStatus() {
  const { userId, ready } = useSession();
  const { data } = useQuery({
    queryKey: ["feed-status", userId],
    queryFn: () => getFeed({ userId, limit: 20 }),
    enabled: ready,
    staleTime: 15_000,
  });

  const cold = data?.isColdStart ?? true;

  return (
    <div className="overflow-hidden rounded-card bg-gradient-to-br from-plum to-ember p-6 text-white">
      <p className="font-mono text-[0.7rem] uppercase tracking-[0.16em] text-white/80">
        Your feed · {cold ? "learning" : "tuned to you"}
      </p>
      <h2 className="mt-2.5 font-display text-2xl font-extrabold leading-tight">
        {cold ? "Getting to know your taste" : "Your feed is tuned to you"}
      </h2>
      <p className="mt-2 max-w-md text-sm text-white/85">
        {cold
          ? "Keep viewing, skipping, saving and opening dishes. The recommendation engine updates on the server after every interaction — the feed shifts toward what you like."
          : "The recommendation engine has enough signal to personalise your feed. It keeps adapting as you explore."}
      </p>
    </div>
  );
}

/** Local, device-only. Counts, never percentages — the backend exposes no
 *  taste-profile endpoint, so we do not invent one. */
export function ObservedTaste() {
  const [cats, setCats] = useState<{ label: string; count: number }[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    setCats(getObservedCategories());
    setTotal(totalInteractions());
  }, []);

  return (
    <section>
      <h3 className="font-display text-lg font-bold text-ink">
        What you&apos;ve been drawn to
      </h3>
      <p className="mt-1 text-sm text-ink-2">
        From {total} dishes you&apos;ve opened or saved on this device.
      </p>

      {cats.length ? (
        <ul className="mt-4 space-y-3">
          {cats.map((c) => {
            const max = cats[0].count || 1;
            return (
              <li key={c.label}>
                <div className="mb-1 flex justify-between text-sm">
                  <span className="font-semibold text-ink">{c.label}</span>
                  <span className="font-mono text-xs text-ink-3">
                    {c.count} {c.count === 1 ? "time" : "times"}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-pill bg-surface-2">
                  <div
                    className="h-full rounded-pill bg-gradient-to-r from-saffron to-ember"
                    style={{ width: `${Math.round((c.count / max) * 100)}%` }}
                  />
                </div>
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="mt-4 rounded-xl border border-hairline bg-surface p-4 text-sm text-ink-2">
          Nothing yet. Open and save a few dishes and your leanings show up here.
        </p>
      )}

      <div className="mt-4">
        <StubNotice>
          Full cuisine-affinity and spice percentages come from the server-side
          taste profile — no <code className="font-mono">/users/me/taste-profile</code>{" "}
          endpoint exists yet, so they aren&apos;t shown here rather than guessed.
        </StubNotice>
      </div>
    </section>
  );
}

export function RecentlyDiscovered() {
  const [items, setItems] = useState<TasteLogEntry[]>([]);
  useEffect(() => {
    setItems(getRecentDiscoveries(12));
  }, []);

  if (!items.length) {
    return (
      <section>
        <h3 className="font-display text-lg font-bold text-ink">
          Recently discovered
        </h3>
        <p className="mt-2 text-sm text-ink-2">
          Dishes you open from the feed collect here.
        </p>
      </section>
    );
  }

  return (
    <section>
      <div className="flex items-center gap-2">
        <IconSparkle width={16} height={16} className="text-saffron" />
        <h3 className="font-display text-lg font-bold text-ink">
          Recently discovered
        </h3>
      </div>
      <div className="no-scrollbar mt-3 flex gap-3 overflow-x-auto pb-1">
        {items.map((it) => (
          <Link
            key={it.candidateId}
            href={`/foods/${encodeURIComponent(it.candidateId)}`}
            className="w-32 shrink-0"
          >
            <div className="overflow-hidden rounded-xl border border-hairline">
              <FoodImage
                name={it.displayName}
                category={it.category}
                seed={it.candidateId}
                className="h-24"
              />
            </div>
            <p className="mt-1.5 line-clamp-1 font-display text-[0.82rem] font-bold text-ink">
              {it.displayName ?? "Dish"}
            </p>
            <p className="line-clamp-1 text-[0.72rem] text-ink-3">
              {it.restaurantName ?? ""}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}

export function tasteChips() {
  return getObservedCategories().map((c) => (
    <Chip key={c.label} tone="saffron">
      {c.label}
    </Chip>
  ));
}
