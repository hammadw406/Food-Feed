import type { FeedItem, FeedResponse } from "./types";

/**
 * BLOCKER 1 shim. `backend/app/schemas/feed.py` declares FeedItem with
 * { id, name, cuisine_type, price_range, image_url, ... } but
 * `feed_service.py` constructs it with
 * { candidate_id, display_name, category, price, restaurant_id, ... }.
 *
 * This accepts EITHER shape and maps to our single internal FeedItem.
 * If Person 2 aligns the schema later, nothing here needs to change.
 */

type RawItem = Record<string, unknown>;

function num(v: unknown): number | null {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function str(v: unknown): string | null {
  if (v === null || v === undefined) return null;
  const s = String(v).trim();
  return s.length ? s : null;
}

export function normalizeFeedItem(raw: RawItem): FeedItem {
  return {
    candidateId: String(raw.candidate_id ?? raw.id ?? ""),
    displayName: str(raw.display_name ?? raw.name),
    category: str(raw.category ?? raw.cuisine_type ?? raw.cuisine),
    price: num(raw.price ?? raw.price_range),
    rating: num(raw.rating),
    restaurantId: num(raw.restaurant_id),
    restaurantName: str(raw.restaurant_name),
    area: str(raw.area),
    score: num(raw.score),
  };
}

export function normalizeFeedResponse(raw: RawItem): FeedResponse {
  const items = Array.isArray(raw.items) ? (raw.items as RawItem[]) : [];
  return {
    userId: str(raw.user_id),
    items: items.map(normalizeFeedItem).filter((i) => i.candidateId),
    total: num(raw.total) ?? items.length,
    isColdStart: Boolean(raw.is_cold_start),
  };
}
