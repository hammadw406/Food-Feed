"use client";

import { useMemo, useState } from "react";
import { useFeed } from "@/lib/hooks/useFeed";
import { FoodCard } from "./FoodCard";
import { SearchBar } from "./SearchBar";
import { FilterChips, applyFilter, type FeedFilter } from "./FilterChips";
import { ContextRail } from "./ContextRail";
import { FoodCardSkeleton } from "@/components/ui/Skeleton";
import { StateBlock } from "@/components/ui/StateBlock";
import { Button } from "@/components/ui/Button";
import { IconClock, IconSparkle, IconWifiOff } from "@/components/ui/icons";
import { pendingCount } from "@/lib/events/queue";

export function FeedWorkspace() {
  const { items, status, isColdStart, errorStatus, loadMore, refresh } = useFeed();
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<FeedFilter>({ kind: "all" });
  const [skipped, setSkipped] = useState<Set<string>>(new Set());

  const visible = useMemo(() => {
    let list = items.filter((i) => !skipped.has(i.candidateId));
    list = applyFilter(list, filter);
    if (query.trim()) {
      const q = query.toLowerCase();
      list = list.filter((i) =>
        [i.displayName, i.restaurantName, i.category, i.area]
          .filter(Boolean)
          .some((s) => s!.toLowerCase().includes(q)),
      );
    }
    return list;
  }, [items, skipped, filter, query]);

  return (
    <div className="mx-auto flex w-full max-w-shell gap-8 px-5 py-6 lg:px-8">
      <div className="min-w-0 flex-1">
        <header className="max-w-content">
          <p className="text-sm text-ink-2">Good to see you 👋</p>
          <h1 className="mt-1 font-display text-3xl font-extrabold tracking-tight text-ink lg:text-[2.5rem]">
            Let&apos;s find something you&apos;ll love.
          </h1>
          <p className="mt-2 max-w-xl text-[0.95rem] text-ink-2">
            A diverse mix to start. Each dish you view, skip, save or open tells
            the recommendation engine a little more — and the feed shifts toward
            your taste.
          </p>
        </header>

        <div className="mt-5 max-w-content space-y-3">
          <SearchBar value={query} onChange={setQuery} />
          <FilterChips items={items} active={filter} onChange={setFilter} />
        </div>

        {isColdStart && status !== "error" ? (
          <div className="mt-5 flex max-w-content items-center gap-2 rounded-xl border border-[#eed7ac] bg-saffron-soft px-3.5 py-2.5 text-[0.83rem] text-[#7c5a1c]">
            <IconSparkle width={15} height={15} />
            Finding your taste — the more you react, the sharper this gets.
          </div>
        ) : null}

        {/* ---- states ---- */}
        {status === "loading" ? (
          <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <FoodCardSkeleton key={i} />
            ))}
          </div>
        ) : null}

        {status === "error" ? (
          <StateBlock
            tone="ember"
            icon={<IconWifiOff width={38} height={38} />}
            title="Can't reach the kitchen"
            body={
              <>
                {errorStatus && errorStatus >= 500
                  ? "The feed service hiccuped. Your place is saved — try again in a moment."
                  : "Your connection dropped. We'll keep your place and load everything you've seen."}
                {pendingCount() > 0 ? (
                  <span className="mt-2 flex items-center justify-center gap-1.5 font-mono text-xs">
                    <IconClock width={13} height={13} /> {pendingCount()} reactions
                    queued
                  </span>
                ) : null}
              </>
            }
            actions={<Button onClick={refresh}>Try again</Button>}
          />
        ) : null}

        {status === "empty" ? (
          <StateBlock
            tone="saffron"
            icon={<IconSparkle width={38} height={38} />}
            title="We're still plating up"
            body="No dishes came back just now. Give it a second and try again."
            actions={<Button onClick={refresh}>Try again</Button>}
          />
        ) : null}

        {(status === "ready" || status === "end") && visible.length === 0 ? (
          <StateBlock
            tone="neutral"
            icon={<IconSparkle width={36} height={36} />}
            title="Nothing matches that filter"
            body="Clear the search or filter to see the full feed again."
            actions={
              <Button
                variant="ghost"
                onClick={() => {
                  setQuery("");
                  setFilter({ kind: "all" });
                }}
              >
                Reset
              </Button>
            }
          />
        ) : null}

        {visible.length > 0 ? (
          <>
            <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
              {visible.map((item) => (
                <FoodCard
                  key={item.candidateId}
                  item={item}
                  onSkip={(id) =>
                    setSkipped((s) => new Set(s).add(id))
                  }
                />
              ))}
            </div>

            <div className="mt-8 flex justify-center">
              {status === "end" ? (
                <div className="text-center">
                  <p className="text-sm text-ink-2">
                    That&apos;s everything fresh for now.
                  </p>
                  <Button
                    variant="ghost"
                    className="mt-3"
                    onClick={refresh}
                  >
                    Shuffle a fresh feed
                  </Button>
                </div>
              ) : (
                <Button variant="soft" onClick={loadMore}>
                  Load more
                </Button>
              )}
            </div>
          </>
        ) : null}
      </div>

      <ContextRail items={items} />
    </div>
  );
}
