/**
 * Types for the REAL backend contract (4 endpoints):
 *   GET  /feed?user_id&limit&offset
 *   POST /events
 *   GET  /restaurants/{restaurant_id}
 *   GET  /health
 *
 * The feed item type below matches what `feed_service.py` actually constructs
 * (see BLOCKER 1 in the design spec — the declared schema in schemas/feed.py
 * disagrees; `normalizeFeedItem` tolerates both).
 */

export type EventType = "view" | "skip" | "like" | "tap";

/** A single dish card in the feed, as produced by feed_service.build_feed(). */
export interface FeedItem {
  candidateId: string;
  displayName: string | null;
  category: string | null;
  price: number | null;
  rating: number | null;
  restaurantId: number | null;
  restaurantName: string | null;
  area: string | null;
  /** 0..1 from the ranking layer; currently always null (ranking not wired). */
  score: number | null;
}

export interface FeedResponse {
  userId: string | null;
  items: FeedItem[];
  total: number;
  /** true when the feed was built without a user embedding (new user). */
  isColdStart: boolean;
}

export interface MenuItem {
  candidateId: string;
  displayName: string;
  category: string | null;
  price: number | null;
  rating: number | null;
}

export interface RestaurantDetail {
  restaurantId: number;
  name: string;
  area: string | null;
  cuisine: string | null;
  priceBand: string | null;
  rating: number | null;
  reviewCount: number | null;
  items: MenuItem[];
}

export interface EventPayload {
  user_id?: string | null;
  candidate_id: string;
  event_type: EventType;
  dwell_time_ms?: number | null;
  session_id?: string | null;
  created_at?: string | null;
}
