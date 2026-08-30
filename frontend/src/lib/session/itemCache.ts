import type { FeedItem } from "@/lib/api/types";

/**
 * The backend has no GET /foods/{id}. When the user opens a dish from the
 * feed we stash that FeedItem in sessionStorage so the Food Detail page can
 * render immediately; it then fetches the parent restaurant (a real endpoint)
 * for the full menu + context.
 */
const PREFIX = "ff.item.";

export function cacheItem(item: FeedItem) {
  try {
    sessionStorage.setItem(PREFIX + item.candidateId, JSON.stringify(item));
  } catch {
    /* ignore */
  }
}

export function readCachedItem(id: string): FeedItem | null {
  try {
    const raw = sessionStorage.getItem(PREFIX + id);
    return raw ? (JSON.parse(raw) as FeedItem) : null;
  } catch {
    return null;
  }
}
