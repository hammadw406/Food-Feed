import type { ReactNode } from "react";
import { IconLock } from "./icons";

/**
 * Honest label for UI that has no backend behind it yet. Used on the
 * auth screens, Community, Create Post and the taste-percentage panels.
 * We never fake data or a success response — this makes the gap explicit.
 */
export function StubNotice({ children }: { children: ReactNode }) {
  return (
    <div className="flex items-start gap-2.5 rounded-xl border border-[#eed7ac] bg-saffron-soft px-3.5 py-3 text-[0.82rem] text-[#7c5a1c]">
      <IconLock width={16} height={16} className="mt-0.5 shrink-0" />
      <span>{children}</span>
    </div>
  );
}
