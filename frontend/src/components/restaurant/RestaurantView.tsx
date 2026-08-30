"use client";

import Link from "next/link";
import { useRestaurant } from "@/lib/hooks/useRestaurant";
import { FoodImage } from "@/components/media/FoodImage";
import { MenuList } from "./MenuList";
import { Rating } from "@/components/ui/Rating";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { StateBlock } from "@/components/ui/StateBlock";
import { StubNotice } from "@/components/ui/StubNotice";
import { IconBack, IconPin, IconWifiOff } from "@/components/ui/icons";
import { ApiError } from "@/lib/api/client";

export function RestaurantView({ id }: { id: string }) {
  const { data, isLoading, isError, error, refetch } = useRestaurant(id);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-content px-5 py-6 lg:px-8">
        <Skeleton className="h-56 w-full rounded-card" />
        <Skeleton className="mt-5 h-9 w-2/3" />
        <Skeleton className="mt-2 h-4 w-1/2" />
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (isError || !data) {
    const status = error instanceof ApiError ? error.status : null;
    return (
      <StateBlock
        tone="ember"
        icon={<IconWifiOff width={38} height={38} />}
        title={status === 404 ? "This place isn't on the menu anymore" : "Can't load this restaurant"}
        body={
          status === 404
            ? "It may have been removed from the dataset."
            : "Your connection dropped or the service is busy."
        }
        actions={
          status === 404 ? (
            <ButtonLink href="/discover">Back to Discover</ButtonLink>
          ) : (
            <Button onClick={() => refetch()}>Try again</Button>
          )
        }
      />
    );
  }

  const mapsQuery = encodeURIComponent(
    [data.name, data.area, "Lahore"].filter(Boolean).join(" "),
  );

  return (
    <div>
      <div className="relative">
        <FoodImage
          name={data.name}
          category={data.cuisine}
          seed={`rest-${data.restaurantId}`}
          className="h-52 sm:h-64 lg:h-72"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/10 to-black/45" />
        <Link
          href="/discover"
          className="absolute left-4 top-4 grid h-10 w-10 place-items-center rounded-pill bg-white/90 text-ink shadow-soft"
          aria-label="Back to Discover"
        >
          <IconBack width={20} height={20} />
        </Link>
      </div>

      <div className="mx-auto -mt-8 max-w-content rounded-t-card bg-paper px-5 pt-6 lg:px-8">
        <div className="lg:flex lg:gap-10">
          {/* left / sticky summary on desktop */}
          <div className="lg:w-72 lg:shrink-0">
            <div className="lg:sticky lg:top-20">
              <h1 className="font-display text-3xl font-extrabold tracking-tight text-ink">
                {data.name}
              </h1>
              <p className="mt-2 flex flex-wrap items-center gap-2 text-sm text-ink-2">
                {data.area ? (
                  <span className="inline-flex items-center gap-1">
                    <IconPin width={13} height={13} /> {data.area}
                  </span>
                ) : null}
                {data.cuisine ? <span>· {data.cuisine}</span> : null}
              </p>

              <div className="mt-4 flex flex-wrap gap-2">
                {data.rating !== null ? (
                  <div className="rounded-xl border border-hairline bg-surface px-3 py-2">
                    <div className="font-display text-lg font-bold">
                      <Rating value={data.rating} count={data.reviewCount} />
                    </div>
                    <div className="text-[0.7rem] text-ink-3">rating</div>
                  </div>
                ) : null}
                {data.priceBand ? (
                  <div className="rounded-xl border border-hairline bg-surface px-3 py-2">
                    <div className="font-display text-lg font-bold">
                      {data.priceBand}
                    </div>
                    <div className="text-[0.7rem] text-ink-3">price band</div>
                  </div>
                ) : null}
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <a
                  href={`https://www.google.com/maps/search/?api=1&query=${mapsQuery}`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-pill border border-hairline bg-surface px-4 py-2.5 text-sm font-semibold text-ink hover:bg-surface-2"
                >
                  <IconPin width={16} height={16} /> Directions
                </a>
              </div>
            </div>
          </div>

          {/* right / content */}
          <div className="mt-8 min-w-0 flex-1 lg:mt-0">
            <h2 className="mb-4 font-display text-xl font-bold text-ink">Menu</h2>
            <MenuList restaurant={data} />

            <h2 className="mb-3 mt-10 font-display text-xl font-bold text-ink">
              Bank offers
            </h2>
            <StubNotice>
              Offers aren&apos;t connected to this build — there&apos;s no offers
              data in the current backend.
            </StubNotice>

            <h2 className="mb-3 mt-10 font-display text-xl font-bold text-ink">
              Community posts
            </h2>
            <StubNotice>
              Community is on-device only for now (no posts API). Posts tied to
              this restaurant will appear here once the backend supports them.
            </StubNotice>
            <div className="h-10" />
          </div>
        </div>
      </div>
    </div>
  );
}
