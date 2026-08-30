import type { ReactNode } from "react";
import { TopNav } from "./TopNav";
import { BottomNav } from "./BottomNav";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-dvh bg-paper">
      <TopNav />
      <main className="pb-24 md:pb-0">{children}</main>
      <BottomNav />
    </div>
  );
}
