"use client";

import { useRouter } from "next/navigation";
import { useMemo } from "react";
import { FoodImage } from "@/components/media/FoodImage";
import { Rating } from "@/components/ui/Rating";
import { Price } from "@/components/ui/Price";
import { cacheItem } from "@/lib/session/itemCache";
import type { MenuItem, RestaurantDetail } from "@/lib/api/types";

export function MenuList({ restaurant }: { restaurant: RestaurantDetail }) {
  const router = useRouter();

  const groups = useMemo(() => {
    const map = new Map<string, MenuItem[]>();
    for (const it of restaurant.items) {
      const key = it.category?.trim() || "More dishes";
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(it);
    }
    return Array.from(map.entries());
  }, [restaurant.items]);

  const openItem = (it: MenuItem) => {
    cacheItem({
      candidateId: it.candidateId,
      displayName: it.displayName,
      category: it.category,
      price: it.price,
      rating: it.rating,
      restaurantId: restaurant.restaurantId,
      restaurantName: restaurant.name,
      area: restaurant.area,
      score: null,
    });
    router.push(`/foods/${encodeURIComponent(it.candidateId)}`);
  };

  if (!restaurant.items.length) {
    return (
      <p className="rounded-card border border-hairline bg-surface p-5 text-sm text-ink-2">
        No menu items are listed for this restaurant yet.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      {groups.map(([category, items]) => (
        <section key={category}>
          <h3 className="mb-3 font-display text-lg font-bold text-ink">
            {category}
          </h3>
          <ul className="grid gap-3 sm:grid-cols-2">
            {items.map((it) => (
              <li key={it.candidateId}>
                <button
                  onClick={() => openItem(it)}
                  className="flex w-full items-center gap-3.5 rounded-2xl border border-hairline bg-surface p-3 text-left transition-shadow hover:shadow-soft"
                >
                  <div className="h-16 w-16 shrink-0 overflow-hidden rounded-xl">
                    <FoodImage
                      name={it.displayName}
                      category={it.category}
                      seed={it.candidateId}
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-display font-bold text-ink">
                      {it.displayName}
                    </p>
                    <div className="mt-1 flex items-center gap-2">
                      <Rating value={it.rating} />
                    </div>
                  </div>
                  <Price value={it.price} className="shrink-0 text-[0.95rem]" />
                </button>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
