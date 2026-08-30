import { apiRequest } from "./client";
import type { EventPayload } from "./types";

/**
 * POST /events — one interaction per call. The backend persists it and
 * invalidates the user's feed cache so the next GET /feed reflects the signal.
 */
export async function postEvent(payload: EventPayload): Promise<void> {
  await apiRequest("/events", { method: "POST", body: payload });
}
