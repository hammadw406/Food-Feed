import type { ReactNode } from "react";
import Link from "next/link";
import { Logo } from "@/components/layout/Logo";
import { FoodImage } from "@/components/media/FoodImage";
import { StubNotice } from "@/components/ui/StubNotice";

/**
 * Shared layout for Sign In / Sign Up. These screens are intentionally
 * NON-FUNCTIONAL: the backend is anonymous-first and exposes no
 * register/login endpoints. The form is visual only and clearly labelled.
 */
export function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}) {
  return (
    <div className="min-h-dvh bg-paper lg:grid lg:grid-cols-2">
      <div className="hidden lg:block">
        <div className="grid h-full grid-cols-2 gap-2 p-2">
          <FoodImage name="Wood-fired Pizza" category="pizza" seed="auth-1" rounded="rounded-2xl" className="h-full" />
          <div className="grid grid-rows-2 gap-2">
            <FoodImage name="Chicken Karahi" category="desi" seed="auth-2" rounded="rounded-2xl" className="h-full" />
            <FoodImage name="Chocolate Cake" category="dessert" seed="auth-3" rounded="rounded-2xl" className="h-full" />
          </div>
        </div>
      </div>

      <div className="flex flex-col justify-center px-5 py-10 sm:px-10 lg:px-16">
        <div className="mx-auto w-full max-w-sm">
          <Logo href="/" />
          <h1 className="mt-8 font-display text-3xl font-extrabold tracking-tight text-ink">
            {title}
          </h1>
          <p className="mt-2 text-ink-2">{subtitle}</p>

          <div className="mt-5">
            <StubNotice>
              Accounts aren&apos;t live yet — the platform runs anonymously and
              remembers your taste on this device. This form is a preview.
            </StubNotice>
          </div>

          <div className="mt-5 space-y-3 opacity-60">{children}</div>

          <div className="mt-6 text-center text-sm text-ink-2">{footer}</div>
          <div className="mt-2 text-center">
            <Link href="/discover" className="text-sm font-semibold text-ember hover:underline">
              Continue as guest →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export function AuthField({
  label,
  type = "text",
  placeholder,
}: {
  label: string;
  type?: string;
  placeholder?: string;
}) {
  return (
    <label className="block">
      <span className="font-mono text-[0.7rem] uppercase tracking-wide text-ink-3">
        {label}
      </span>
      <input
        type={type}
        placeholder={placeholder}
        disabled
        className="mt-1.5 w-full cursor-not-allowed rounded-xl border border-hairline bg-surface px-3.5 py-3 text-ink outline-none placeholder:text-ink-3"
      />
    </label>
  );
}
