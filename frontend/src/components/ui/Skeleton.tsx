import { clsx } from "clsx";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={clsx(
        "animate-pulse rounded-lg bg-surface-2 motion-reduce:animate-none",
        className,
      )}
    />
  );
}

export function FoodCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-card border border-hairline bg-surface shadow-soft">
      <Skeleton className="h-48 rounded-none" />
      <div className="space-y-2 p-4">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-3.5 w-1/2" />
        <div className="flex gap-2 pt-2">
          <Skeleton className="h-6 w-16 rounded-pill" />
          <Skeleton className="h-6 w-12 rounded-pill" />
        </div>
        <div className="flex items-center justify-between pt-3">
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-10 w-28 rounded-pill" />
        </div>
      </div>
    </div>
  );
}
