"use client";

import { useState } from "react";
import { clsx } from "clsx";
import { ButtonLink } from "@/components/ui/Button";
import { StateBlock } from "@/components/ui/StateBlock";
import { StubNotice } from "@/components/ui/StubNotice";
import { IconPlus, IconUsers } from "@/components/ui/icons";

const LENSES = ["Discoveries", "Near you"];

export default function CommunityPage() {
  const [lens, setLens] = useState(0);

  return (
    <div className="mx-auto max-w-content px-5 py-6 lg:px-8">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl font-extrabold tracking-tight text-ink">
          Community
        </h1>
        <ButtonLink href="/community/new" size="sm">
          <IconPlus width={16} height={16} /> Share a find
        </ButtonLink>
      </div>

      <p className="mt-2 max-w-xl text-[0.95rem] text-ink-2">
        Discover food through what other people are eating. Every post links
        straight to the dish and the restaurant.
      </p>

      <div className="mt-5 inline-flex rounded-pill bg-surface-2 p-1">
        {LENSES.map((l, i) => (
          <button
            key={l}
            onClick={() => setLens(i)}
            className={clsx(
              "rounded-pill px-4 py-2 text-sm font-semibold transition-colors",
              lens === i ? "bg-surface text-ink shadow-soft" : "text-ink-2",
            )}
          >
            {l}
          </button>
        ))}
      </div>

      <div className="mt-6">
        <StubNotice>
          Community isn&apos;t connected in this build — the backend has no posts
          API. The screen, the post composer and the post → dish → restaurant
          links are all built and will light up when{" "}
          <code className="font-mono">GET/POST /posts</code> exists.
        </StubNotice>
      </div>

      <StateBlock
        tone="basil"
        icon={<IconUsers width={38} height={38} />}
        title="No posts to show yet"
        body="Once the community backend is live, finds from people near you appear here."
        actions={
          <ButtonLink href="/community/new" variant="ghost">
            Preview the composer
          </ButtonLink>
        }
      />
    </div>
  );
}
