"use client";

import { useEffect, useRef } from "react";
import { trackEvent } from "@/lib/events/queue";

/**
 * Attaches to a feed card element. Emits the four real backend signals:
 *  - view : first time ≥50% visible in this session
 *  - dwell_time_ms : accrued while ≥50% visible + tab focused
 *  - skip : card was viewed, then left the viewport with low dwell and no
 *           like/tap
 * `like` and `tap` are emitted by the card's buttons, which also call
 * markResolved() so no spurious skip fires.
 */
const SKIP_DWELL_MS = 2000;

export function useInteractionTracker(candidateId: string) {
  const ref = useRef<HTMLElement | null>(null);
  const viewed = useRef(false);
  const resolved = useRef(false);
  const dwell = useRef(0);
  const visibleSince = useRef<number | null>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || !candidateId) return;

    const startTimer = () => {
      if (visibleSince.current === null && document.visibilityState === "visible")
        visibleSince.current = performance.now();
    };
    const stopTimer = () => {
      if (visibleSince.current !== null) {
        dwell.current += performance.now() - visibleSince.current;
        visibleSince.current = null;
      }
    };

    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
          if (!viewed.current) {
            viewed.current = true;
            trackEvent(candidateId, "view");
          }
          startTimer();
        } else {
          stopTimer();
          if (viewed.current && !resolved.current) {
            resolved.current = true;
            if (dwell.current < SKIP_DWELL_MS) {
              trackEvent(candidateId, "skip", Math.round(dwell.current));
            }
          }
        }
      },
      { threshold: [0, 0.5, 1] },
    );
    io.observe(el);

    const onVis = () =>
      document.visibilityState === "visible" ? startTimer() : stopTimer();
    document.addEventListener("visibilitychange", onVis);

    return () => {
      io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
      stopTimer();
    };
  }, [candidateId]);

  const markResolved = (type: "like" | "tap") => {
    if (visibleSince.current !== null) {
      dwell.current += performance.now() - visibleSince.current;
      visibleSince.current = null;
    }
    resolved.current = true;
    trackEvent(candidateId, type, Math.round(dwell.current));
  };

  return { ref, markResolved };
}
