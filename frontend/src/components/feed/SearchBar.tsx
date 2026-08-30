"use client";

import { IconSearch } from "@/components/ui/icons";

/**
 * The backend has no search endpoint. This filters the dishes already loaded
 * in the feed (client-side, over backend-ranked data). It does not fetch and
 * does not emit a SEARCH event — there is no backend path for one.
 */
export function SearchBar({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <label className="flex items-center gap-3 rounded-2xl border border-hairline bg-surface px-4 py-3 focus-within:border-ember">
      <IconSearch width={18} height={18} className="shrink-0 text-ink-3" />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search a craving, place or dish"
        className="w-full bg-transparent text-[0.95rem] text-ink outline-none placeholder:text-ink-3"
      />
      {value ? (
        <button
          onClick={() => onChange("")}
          className="font-mono text-xs text-ink-3 hover:text-ink"
        >
          clear
        </button>
      ) : null}
    </label>
  );
}
