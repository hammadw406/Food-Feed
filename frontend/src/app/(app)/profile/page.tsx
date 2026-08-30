"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ObservedTaste, RecentlyDiscovered } from "@/components/taste/TasteSections";
import { Button } from "@/components/ui/Button";
import { StubNotice } from "@/components/ui/StubNotice";
import { useSession } from "@/lib/session/SessionProvider";
import { getArea } from "@/lib/session/identity";
import { totalInteractions } from "@/lib/taste/localTaste";

export default function ProfilePage() {
  const router = useRouter();
  const { userId, reset } = useSession();
  const [area, setArea] = useState<string | null>(null);
  const [count, setCount] = useState(0);

  useEffect(() => {
    setArea(getArea());
    setCount(totalInteractions());
  }, []);

  const shortId = userId ? userId.split("_").pop()!.slice(0, 6) : "······";

  const doReset = () => {
    if (
      confirm(
        "Reset your taste and start fresh? This clears what this device has learned.",
      )
    ) {
      reset();
      router.push("/discover");
    }
  };

  return (
    <div className="mx-auto max-w-content px-5 py-6 lg:px-8">
      <div className="overflow-hidden rounded-card bg-gradient-to-br from-plum to-ember p-6 text-white">
        <div className="flex items-center gap-4">
          <div className="grid h-14 w-14 place-items-center rounded-pill bg-white/20 text-2xl">
            🍽
          </div>
          <div>
            <h1 className="font-display text-2xl font-extrabold">Your taste</h1>
            <p className="font-mono text-[0.78rem] text-white/75">
              guest · {count} discoveries · id {shortId}
            </p>
          </div>
        </div>
        <p className="mt-4 text-sm text-white/85">
          {area
            ? `Discovering around ${area}.`
            : "No area set — you can add one anytime from onboarding."}
        </p>
      </div>

      <div className="mt-6">
        <StubNotice>
          There&apos;s no accounts backend, so there&apos;s no name, email or
          cross-device sync yet. Your taste lives on this device.
        </StubNotice>
      </div>

      <div className="mt-8 grid gap-8 lg:grid-cols-2">
        <ObservedTaste />
        <RecentlyDiscovered />
      </div>

      <div className="mt-10 border-t border-hairline pt-6">
        <Button variant="soft" onClick={doReset}>
          Reset my taste &amp; start fresh
        </Button>
      </div>
    </div>
  );
}
