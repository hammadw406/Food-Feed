import Link from "next/link";
import { AuthShell, AuthField } from "@/components/marketing/AuthShell";
import { Button } from "@/components/ui/Button";

export const metadata = { title: "Sign in — Food Feed" };

export default function LoginPage() {
  return (
    <AuthShell
      title="Welcome back"
      subtitle="Sign in to sync your taste across devices."
      footer={
        <>
          New here?{" "}
          <Link href="/signup" className="font-semibold text-ember hover:underline">
            Create an account
          </Link>
        </>
      }
    >
      <AuthField label="Email" type="email" placeholder="you@example.com" />
      <AuthField label="Password" type="password" placeholder="••••••••" />
      <Button full disabled>
        Sign in
      </Button>
    </AuthShell>
  );
}
