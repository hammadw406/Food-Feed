import { apiRequest } from "./client";
import { normalizeFeedResponse } from "./normalizeFeedItem";
import type { FeedResponse } from "./types";

export interface FeedParams {
  userId?: string | null;
  /** Pinned to 20 for the primary feed so we stay on the Redis key the
   *  backend invalidates after an event (see BLOCKER 8). */
  limit?: number;
  offset?: number;
  signal?: AbortSignal;
}

export async function getFeed({
  userId,
  limit = 20,
  offset = 0,
  signal,
}: FeedParams): Promise<FeedResponse> {
  const raw = await apiRequest<Record<string, unknown>>("/feed", {
    query: { user_id: userId ?? undefined, limit, offset },
    signal,
  });
  return normalizeFeedResponse(raw);
}
