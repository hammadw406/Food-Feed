import { postEvent } from "@/lib/api/events";
import { getSessionId, getUserId } from "@/lib/session/identity";
import type { EventType } from "@/lib/api/types";

/**
 * Interaction event queue. Batches POST /events with retry + localStorage
 * persistence so a dropped connection never loses a signal. Flushes on an
 * interval, when the queue fills, and on tab hide.
 *
 * Only the four real backend event types are ever emitted: view, skip, like, tap.
 */

interface QueuedEvent {
  candidate_id: string;
  event_type: EventType;
  dwell_time_ms?: number | null;
  created_at: string;
}

const STORE_KEY = "ff.eventQueue";
const FLUSH_MS = 4000;
const MAX_BEFORE_FLUSH = 8;

let queue: QueuedEvent[] = [];
let timer: ReturnType<typeof setInterval> | null = null;
let started = false;

function load() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) queue = JSON.parse(raw) as QueuedEvent[];
  } catch {
    queue = [];
  }
}
function persist() {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(queue));
  } catch {
    /* ignore */
  }
}

export function pendingCount(): number {
  return queue.length;
}

export async function flushEvents(): Promise<void> {
  if (!queue.length) return;
  const batch = [...queue];
  const userId = getUserId();
  const sessionId = getSessionId();
  const sent: QueuedEvent[] = [];

  for (const ev of batch) {
    try {
      await postEvent({
        user_id: userId,
        session_id: sessionId,
        candidate_id: ev.candidate_id,
        event_type: ev.event_type,
        dwell_time_ms: ev.dwell_time_ms ?? null,
        created_at: ev.created_at,
      });
      sent.push(ev);
    } catch {
      // Stop on first failure; keep the rest queued for the next flush.
      break;
    }
  }

  if (sent.length) {
    queue = queue.filter((e) => !sent.includes(e));
    persist();
  }
}

export function trackEvent(
  candidateId: string,
  eventType: EventType,
  dwellMs?: number,
): void {
  if (!candidateId) return;
  ensureStarted();
  queue.push({
    candidate_id: candidateId,
    event_type: eventType,
    dwell_time_ms: dwellMs ?? null,
    created_at: new Date().toISOString(),
  });
  persist();
  if (eventType === "tap" || eventType === "like" || queue.length >= MAX_BEFORE_FLUSH) {
    void flushEvents();
  }
}

function ensureStarted() {
  if (started || typeof window === "undefined") return;
  started = true;
  load();
  timer = setInterval(() => void flushEvents(), FLUSH_MS);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") void flushEvents();
  });
  window.addEventListener("online", () => void flushEvents());
  void flushEvents();
}

export function stopQueue() {
  if (timer) clearInterval(timer);
  timer = null;
  started = false;
}
