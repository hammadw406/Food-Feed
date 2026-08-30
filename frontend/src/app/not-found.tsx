import { ButtonLink } from "@/components/ui/Button";
import { StateBlock } from "@/components/ui/StateBlock";
import { IconCompass } from "@/components/ui/icons";

export default function NotFound() {
  return (
    <div className="grid min-h-dvh place-items-center bg-paper">
      <StateBlock
        tone="neutral"
        icon={<IconCompass width={38} height={38} />}
        title="This page isn't on the menu"
        body="The link may be old or the item was removed."
        actions={<ButtonLink href="/discover">Go to Discover</ButtonLink>}
      />
    </div>
  );
}
