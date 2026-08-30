import { MarketingNav } from "@/components/layout/MarketingNav";
import { FoodCollage } from "@/components/marketing/FoodCollage";
import { ButtonLink } from "@/components/ui/Button";
import { IconCompass } from "@/components/ui/icons";

const STEPS = [
  ["Discover", "Open the feed to a diverse mix of real dishes from restaurants near you."],
  ["React", "View, dwell, skip, save, open. Every signal goes to the recommendation engine."],
  ["Personalize", "The feed shifts toward your taste — no forms, no quizzes, just behaviour."],
];

export default function LandingPage() {
  return (
    <div className="relative min-h-dvh overflow-hidden bg-paper">
      <MarketingNav />

      <section className="mx-auto grid max-w-shell items-center gap-10 px-5 pb-16 pt-28 lg:grid-cols-[1.05fr_1fr] lg:gap-16 lg:px-8 lg:pt-36">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.2em] text-ink-3">
            Discover · React · Personalize
          </p>
          <h1 className="mt-4 font-display text-[2.7rem] font-extrabold leading-[1.03] tracking-tight text-ink sm:text-6xl">
            &ldquo;I don&apos;t know what<br />I want to eat.&rdquo;
          </h1>
          <p className="mt-5 max-w-md text-lg text-ink-2">
            Start exploring. Food Feed learns what catches your eye and gradually
            tunes recommendations to your taste.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <ButtonLink href="/onboarding" size="lg">
              Start discovering <IconCompass width={18} height={18} />
            </ButtonLink>
            <ButtonLink href="/discover" variant="ghost" size="lg">
              Explore as guest
            </ButtonLink>
          </div>
          <p className="mt-4 font-mono text-xs text-ink-3">
            No account needed. Your taste is remembered on this device.
          </p>
        </div>

        <div className="lg:pl-4">
          <FoodCollage />
        </div>
      </section>

      <section className="border-t border-hairline bg-surface">
        <div className="mx-auto grid max-w-content gap-8 px-5 py-14 sm:grid-cols-3 lg:px-8">
          {STEPS.map(([title, body], i) => (
            <div key={title}>
              <span className="font-mono text-sm text-ember">0{i + 1}</span>
              <h3 className="mt-1 font-display text-lg font-bold text-ink">
                {title}
              </h3>
              <p className="mt-1.5 text-sm text-ink-2">{body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
