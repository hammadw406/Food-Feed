/**
 * Anonymous identity. The backend is anonymous-first — no login required.
 * We mint a stable user_id and a rolling session_id and keep them in
 * localStorage. These are the exact values sent with every POST /events.
 */

const USER_KEY = "ff.user_id";
const SESSION_KEY = "ff.session";
const ONBOARDED_KEY = "ff.onboarded";
const AREA_KEY = "ff.area";
const SESSION_IDLE_MS = 30 * 60 * 1000;

function uid(prefix: string): string {
  const rnd =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : Math.random().toString(36).slice(2) + Date.now().toString(36);
  return `${prefix}_${rnd}`;
}

function safeGet(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}
function safeSet(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* private mode / disabled storage */
  }
}

export function getUserId(): string {
  let id = safeGet(USER_KEY);
  if (!id) {
    id = uid("web_user");
    safeSet(USER_KEY, id);
  }
  return id;
}

export function getSessionId(): string {
  const now = Date.now();
  try {
    const raw = safeGet(SESSION_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as { id: string; last: number };
      if (now - parsed.last < SESSION_IDLE_MS) {
        safeSet(SESSION_KEY, JSON.stringify({ id: parsed.id, last: now }));
        return parsed.id;
      }
    }
  } catch {
    /* fall through to new session */
  }
  const id = uid("web_sess");
  safeSet(SESSION_KEY, JSON.stringify({ id, last: now }));
  return id;
}

export function isOnboarded(): boolean {
  return safeGet(ONBOARDED_KEY) === "1";
}
export function setOnboarded(area?: string): void {
  safeSet(ONBOARDED_KEY, "1");
  if (area) safeSet(AREA_KEY, area);
}
export function getArea(): string | null {
  return safeGet(AREA_KEY);
}

export function resetIdentity(): void {
  try {
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem("ff.tasteLog");
  } catch {
    /* ignore */
  }
}
