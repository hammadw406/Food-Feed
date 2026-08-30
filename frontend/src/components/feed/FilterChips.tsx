"use client";

import { clsx } from "clsx";
import { useMemo } from "react";
import { IconSparkle } from "@/components/ui/icons";
import type { FeedItem } from "@/lib/api/types";

/**
 * Client-side FILTERS over the backend-ranked feed. These never re-rank and
 * never call a second recommendation path — "For you" is always the backend's
 * own order. Cuisine chips are derived from the categories actually present
 * in the loaded data, so there are no dead options.
 */
export type FeedFilter = { kind: "all" } | { kind: "category"; value: string } | { kind: "top" } | { kind: "budget" };

export function applyFilter(items: FeedItem[], filter: FeedFilter): FeedItem[] {
  switch (filter.kind) {
    case "all":
      return items;
    case "category":
      return items.filter(
        (i) => (i.category ?? "").toLowerCase() === filter.value.toLowerCase(),
      );
    case "top":
      return items.filter((i) => i.rating !== null && i.rating >= 4);
    case "budget": {
      const prices = items
        .map((i) => i.price)
        .filter((p): p is number => p !== null)
        .sort((a, b) => a - b);
      if (!prices.length) return items;
      const median = prices[Math.floor(prices.length / 2)];
      return items.filter((i) => i.price !== null && i.price <= median);
    }
  }
}

function eq(a: FeedFilter, b: FeedFilter) {
  return JSON.stringify(a) === JSON.stringify(b);
}

export function FilterChips({
  items,
  active,
  onChange,
}: {
  items: FeedItem[];
  active: FeedFilter;
  onChange: (f: FeedFilter) => void;
}) {
  const categories = useMemo(() => {
    const set = new Map<string, number>();
    for (const i of items) {
      if (!i.category) continue;
      set.set(i.category, (set.get(i.category) ?? 0) + 1);
    }
    return Array.from(set.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([c]) => c);
  }, [items]);

  const chip = (label: string, f: FeedFilter, icon?: boolean) => (
    <button
      key={label}
      onClick={() => onChange(f)}
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-pill border px-3 py-1.5 text-sm font-semibold transition-colors",
        eq(active, f)
          ? "border-ember bg-ember text-white"
          : "border-hairline bg-surface text-ink-2 hover:bg-surface-2",
      )}
    >
      {icon ? <IconSparkle width={13} height={13} /> : null}
      {label}
    </button>
  );

  return (
    <div className="flex flex-wrap gap-2">
      {chip("For you", { kind: "all" }, true)}
      {chip("Top rated", { kind: "top" })}
      {chip("Budget-friendly", { kind: "budget" })}
      {categories.map((c) => chip(c, { kind: "category", value: c }))}
    </div>
  );
}
