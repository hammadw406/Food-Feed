import type { FeedItem } from "@/lib/api/types";

/**
 * LOCAL, device-only reflection of what the user has been reacting to.
 *
 * This is NOT a taste profile and NOT a recommendation signal. The backend
 * owns ranking and taste. There is no GET /users/me/taste-profile endpoint,
 * so the Profile / For-You screens show:
 *   - "recently discovered" dishes (from this log)
 *   - a coarse count of categories the user opened/liked ON THIS DEVICE
 * and clearly label it as such. No percentages are invented.
 */

const KEY = "ff.tasteLog";
const MAX = 60;

export interface TasteLogEntry {
  candidateId: string;
  displayName: string | null;
  category: string | null;
  restaurantId: number | null;
  restaurantName: string | null;
  action: "like" | "tap";
  at: number;
}

function read(): TasteLogEntry[] {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as TasteLogEntry[]) : [];
  } catch {
    return [];
  }
}
function write(entries: TasteLogEntry[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(entries.slice(0, MAX)));
  } catch {
    /* ignore */
  }
}

export function recordDiscovery(item: FeedItem, action: "like" | "tap") {
  const entries = read().filter((e) => e.candidateId !== item.candidateId);
  entries.unshift({
    candidateId: item.candidateId,
    displayName: item.displayName,
    category: item.category,
    restaurantId: item.restaurantId,
    restaurantName: item.restaurantName,
    action,
    at: Date.now(),
  });
  write(entries);
}

export function getRecentDiscoveries(limit = 12): TasteLogEntry[] {
  return read().slice(0, limit);
}

/** Category counts observed on this device — labelled, never shown as % */
export function getObservedCategories(): { label: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const e of read()) {
    if (!e.category) continue;
    counts.set(e.category, (counts.get(e.category) ?? 0) + 1);
  }
  return Array.from(counts.entries())
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);
}

export function totalInteractions(): number {
  return read().length;
}
