import {
  FeedLearningStatus,
  ObservedTaste,
  RecentlyDiscovered,
} from "@/components/taste/TasteSections";
import { ButtonLink } from "@/components/ui/Button";

export const metadata = { title: "For You — Food Feed" };

export default function ForYouPage() {
  return (
    <div className="mx-auto max-w-content space-y-8 px-5 py-6 lg:px-8">
      <FeedLearningStatus />

      <div className="grid gap-8 lg:grid-cols-2">
        <ObservedTaste />
        <RecentlyDiscovered />
      </div>

      <div className="rounded-card border border-hairline bg-surface p-5 text-center">
        <p className="text-sm text-ink-2">
          The best way to improve your feed is to use it.
        </p>
        <ButtonLink href="/discover" className="mt-3">
          Back to discovering
        </ButtonLink>
      </div>
    </div>
  );
}
