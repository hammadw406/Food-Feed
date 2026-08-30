"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getFeed } from "@/lib/api/feed";
import { ApiError } from "@/lib/api/client";
import { useSession } from "@/lib/session/SessionProvider";
import type { FeedItem } from "@/lib/api/types";

type Status = "loading" | "ready" | "error" | "empty" | "end";

/**
 * Feed as a stream. The backend's cold-start sample re-seeds per request
 * (BLOCKER 7), so we dedupe by candidateId and treat "no new items" as the
 * end of the stream rather than trusting offset pagination.
 */
export function useFeed() {
  const { userId, ready } = useSession();
  const [items, setItems] = useState<FeedItem[]>([]);
  const [status, setStatus] = useState<Status>("loading");
  const [isColdStart, setIsColdStart] = useState(true);
  const [errorStatus, setErrorStatus] = useState<number | null>(null);
  const seen = useRef<Set<string>>(new Set());
  const offset = useRef(0);
  const loadingMore = useRef(false);

  const fetchPage = useCallback(
    async (reset: boolean) => {
      if (loadingMore.current) return;
      loadingMore.current = true;
      if (reset) {
        setStatus("loading");
        seen.current = new Set();
        offset.current = 0;
      }
      try {
        const res = await getFeed({
          userId,
          limit: 20,
          offset: offset.current,
        });
        setIsColdStart(res.isColdStart);
        const fresh = res.items.filter((i) => !seen.current.has(i.candidateId));
        fresh.forEach((i) => seen.current.add(i.candidateId));
        offset.current += 20;

        setItems((prev) => {
          const next = reset ? fresh : [...prev, ...fresh];
          if (!next.length) setStatus("empty");
          else if (fresh.length === 0) setStatus("end");
          else setStatus("ready");
          return next;
        });
        setErrorStatus(null);
      } catch (err) {
        setErrorStatus(err instanceof ApiError ? err.status : null);
        setStatus("error");
      } finally {
        loadingMore.current = false;
      }
    },
    [userId],
  );

  useEffect(() => {
    if (ready) void fetchPage(true);
  }, [ready, fetchPage]);

  return {
    items,
    status,
    isColdStart,
    errorStatus,
    loadMore: () => fetchPage(false),
    refresh: () => fetchPage(true),
  };
}
