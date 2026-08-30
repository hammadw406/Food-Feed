"use client";

import { useEffect } from "react";
import { Button, ButtonLink } from "@/components/ui/Button";
import { StateBlock } from "@/components/ui/StateBlock";
import { IconWifiOff } from "@/components/ui/icons";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="grid min-h-dvh place-items-center bg-paper">
      <StateBlock
        tone="ember"
        icon={<IconWifiOff width={38} height={38} />}
        title="Something went sideways"
        body="An unexpected error stopped this screen. Your place and your saved reactions are safe."
        actions={
          <>
            <Button onClick={reset}>Try again</Button>
            <ButtonLink href="/discover" variant="ghost">
              Back to Discover
            </ButtonLink>
          </>
        }
      />
    </div>
  );
}
