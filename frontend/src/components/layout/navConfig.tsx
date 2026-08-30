import { IconCompass, IconSparkle, IconUser, IconUsers } from "@/components/ui/icons";
import type { ComponentType, SVGProps } from "react";

export interface NavDest {
  href: string;
  label: string;
  Icon: ComponentType<SVGProps<SVGSVGElement>>;
}

/** The complete product structure. Every entry routes to a real screen. */
export const NAV: NavDest[] = [
  { href: "/discover", label: "Discover", Icon: IconCompass },
  { href: "/community", label: "Community", Icon: IconUsers },
  { href: "/for-you", label: "For You", Icon: IconSparkle },
  { href: "/profile", label: "Profile", Icon: IconUser },
];
