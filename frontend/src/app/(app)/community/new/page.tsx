"use client";

import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { StubNotice } from "@/components/ui/StubNotice";
import { IconBack, IconCamera } from "@/components/ui/icons";

export default function CreatePostPage() {
  const [caption, setCaption] = useState("");

  return (
    <div className="mx-auto max-w-xl px-5 py-6">
      <div className="flex items-center justify-between">
        <Link
          href="/community"
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-ink-2 hover:text-ink"
        >
          <IconBack width={16} height={16} /> Community
        </Link>
        <Button size="sm" disabled>
          Post
        </Button>
      </div>

      <h1 className="mt-4 font-display text-2xl font-extrabold tracking-tight text-ink">
        Share a find
      </h1>

      <div className="mt-4">
        <StubNotice>
          Posting isn&apos;t available — there&apos;s no posts API and no media
          upload in the current backend. This composer is a preview of the flow.
        </StubNotice>
      </div>

      <div className="mt-5 space-y-5 opacity-70">
        <div className="grid h-44 place-items-center gap-2 rounded-2xl border-2 border-dashed border-hairline bg-surface text-ink-3">
          <IconCamera width={32} height={32} />
          <span className="text-sm font-semibold text-ink-2">
            Add a photo of your food
          </span>
          <span className="font-mono text-xs">upload not implemented</span>
        </div>

        <label className="block">
          <span className="font-mono text-[0.7rem] uppercase tracking-wide text-ink-3">
            Caption
          </span>
          <textarea
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            rows={3}
            placeholder="What made this worth sharing?"
            className="mt-1.5 w-full rounded-xl border border-hairline bg-surface px-3.5 py-3 text-ink outline-none placeholder:text-ink-3 focus:border-ember"
          />
        </label>

        <label className="block">
          <span className="font-mono text-[0.7rem] uppercase tracking-wide text-ink-3">
            What did you have?
          </span>
          <input
            disabled
            placeholder="Search a dish or restaurant"
            className="mt-1.5 w-full cursor-not-allowed rounded-xl border border-hairline bg-surface px-3.5 py-3 text-ink placeholder:text-ink-3"
          />
        </label>
      </div>
    </div>
  );
}
