/**
 * The single API client. Every network call to the FastAPI backend goes
 * through here — no duplicate fetch logic elsewhere.
 *
 * Base URL comes from NEXT_PUBLIC_API_URL (see .env.local.example).
 * Auth is optional on the backend (anonymous-first); we do not send a token.
 */

const BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
).replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  query?: Record<string, string | number | undefined | null>;
  signal?: AbortSignal;
}

export async function apiRequest<T>(
  path: string,
  { method = "GET", body, query, signal }: RequestOptions = {},
): Promise<T> {
  const url = new URL(BASE_URL + path);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
    }
  }

  let res: Response;
  try {
    res = await fetch(url.toString(), {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal,
      cache: "no-store",
    });
  } catch (err) {
    // Network failure / CORS / DNS — surfaced as a 0-status ApiError so the
    // UI can show the "Can't reach the kitchen" state.
    throw new ApiError(
      err instanceof Error ? err.message : "Network request failed",
      0,
    );
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data?.detail ?? detail;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(
      typeof detail === "string" ? detail : "Request failed",
      res.status,
    );
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export { BASE_URL };
