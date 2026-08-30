"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { clsx } from "clsx";
import { Logo } from "@/components/layout/Logo";
import { Button } from "@/components/ui/Button";
import { IconChevron, IconLocate, IconPin } from "@/components/ui/icons";
import { DHA_AREAS } from "@/lib/constants/areas";
import { setOnboarded } from "@/lib/session/identity";

export default function OnboardingPage() {
  const router = useRouter();
  const [area, setArea] = useState<string | null>(null);
  const [locating, setLocating] = useState(false);
  const [locNote, setLocNote] = useState<string | null>(null);

  const finish = (chosenArea?: string | null) => {
    setOnboarded(chosenArea ?? area ?? undefined);
    router.push("/discover");
  };

  const useLocation = () => {
    if (!("geolocation" in navigator)) {
      setLocNote("Location isn't available in this browser — pick an area below.");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      () => {
        // The backend /feed endpoint has no lat/lng or area parameter, so we
        // can't send coordinates anywhere. We record that the user allowed
        // location and move on.
        setLocating(false);
        finish("Near me");
      },
      () => {
        setLocating(false);
        setLocNote("No problem — location's off. Pick an area below instead.");
      },
      { timeout: 8000 },
    );
  };

  return (
    <div className="min-h-dvh bg-paper">
      <div className="mx-auto max-w-lg px-5 py-6">
        <Logo href="/" />
      </div>

      <div className="mx-auto max-w-lg px-5 pb-16">
        <div className="mb-8 flex gap-1.5">
          <span className="h-1 flex-1 rounded-full bg-ember" />
          <span className="h-1 flex-1 rounded-full bg-hairline" />
        </div>

        <div className="grid h-16 w-16 place-items-center rounded-2xl bg-ember-soft text-ember">
          <IconPin width={30} height={30} />
        </div>
        <h1 className="mt-5 font-display text-3xl font-extrabold leading-tight tracking-tight text-ink">
          Where are you discovering from?
        </h1>
        <p className="mt-2 text-ink-2">
          We only use this to keep recommendations nearby. Roughly is fine — and
          you can skip it.
        </p>

        <Button
          full
          size="lg"
          className="mt-6"
          onClick={useLocation}
          disabled={locating}
        >
          <IconLocate width={18} height={18} />
          {locating ? "Getting your location…" : "Use my current location"}
        </Button>

        {locNote ? (
          <p className="mt-3 rounded-xl bg-saffron-soft px-3.5 py-2.5 text-[0.83rem] text-[#7c5a1c]">
            {locNote}
          </p>
        ) : null}

        <div className="my-6 flex items-center gap-3 text-xs text-ink-3">
          <span className="h-px flex-1 bg-hairline" />
          or pick an area
          <span className="h-px flex-1 bg-hairline" />
        </div>

        <ul className="space-y-2.5">
          {DHA_AREAS.map((a) => (
            <li key={a}>
              <button
                onClick={() => setArea(a)}
                className={clsx(
                  "flex w-full items-center justify-between rounded-2xl border px-4 py-3.5 text-left transition-colors",
                  area === a
                    ? "border-ember bg-ember-soft"
                    : "border-hairline hover:bg-surface-2",
                )}
              >
                <span className={clsx("font-semibold", area === a && "text-[#b13c17]")}>
                  {a}
                </span>
                <IconChevron
                  width={18}
                  height={18}
                  className={area === a ? "text-ember" : "text-ink-3"}
                />
              </button>
            </li>
          ))}
        </ul>

        <div className="mt-8 flex gap-3">
          <Button variant="soft" className="flex-1" onClick={() => finish(null)}>
            Skip for now
          </Button>
          <Button
            className="flex-[1.4]"
            disabled={!area}
            onClick={() => finish()}
          >
            Continue
          </Button>
        </div>
      </div>
    </div>
  );
}
