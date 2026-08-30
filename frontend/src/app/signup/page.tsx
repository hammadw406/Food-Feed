import Link from "next/link";
import { AuthShell, AuthField } from "@/components/marketing/AuthShell";
import { Button } from "@/components/ui/Button";

export const metadata = { title: "Sign up — Food Feed" };

export default function SignupPage() {
  return (
    <AuthShell
      title="Create your account"
      subtitle="Keep your taste profile as you switch phone and laptop."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="font-semibold text-ember hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <AuthField label="Name" placeholder="Your name" />
      <AuthField label="Email" type="email" placeholder="you@example.com" />
      <AuthField label="Password" type="password" placeholder="Choose a password" />
      <Button full disabled>
        Create account
      </Button>
    </AuthShell>
  );
}
