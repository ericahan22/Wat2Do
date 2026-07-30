import { Badge } from "@/shared/components/ui/badge";
import BadgeMask from "@/shared/components/ui/badge-mask";
import { getEventStatus, isEventNew } from "@/shared/lib/eventUtils";
import type { Event } from "@/features/events/types/events";

/**
 * Badge component for event status (live, soon)
 */
export function EventStatusBadge({ event }: { event: Event }) {
  const status = getEventStatus(event);

  if (status === "live") {
    return (
      <BadgeMask variant="top-right">
        <Badge variant="live" className="font-extrabold">
          LIVE
        </Badge>
      </BadgeMask>
    );
  }

  if (status === "soon") {
    return (
      <BadgeMask variant="top-right">
        <Badge variant="soon" className="font-extrabold">
          Starting soon
        </Badge>
      </BadgeMask>
    );
  }

  return null;
}

/**
 * Badge component for new events
 */
export function NewEventBadge({ event }: { event: Event }) {
  if (!isEventNew(event)) return null;

  return (
    <BadgeMask variant="top-left">
      <Badge variant="new" className="font-extrabold">
        NEW
      </Badge>
    </BadgeMask>
  );
}

/**
 * Badge component for organization/handle display
 * @param event - Event object
 * @param isSelectMode - Whether selection mode is active (prevents link clicks)
 */
export function OrganizationBadge({
  event,
  isSelectMode = false,
}: {
  event: Event;
  isSelectMode?: boolean;
}) {
  // Use ig_handle if available, otherwise fallback to display_handle
  const rawHandle = event.ig_handle || event.display_handle;
  if (!rawHandle) return null;

  // Ensure it has a single leading @
  const handleWithAt = rawHandle.startsWith("@") ? rawHandle : `@${rawHandle}`;
  const isInstagram = !!event.ig_handle;

  return (
    <BadgeMask variant="bottom-left">
      <Badge
        onMouseDown={(e) => {
          e.stopPropagation();
          if (!isSelectMode && event.ig_handle) {
            const cleanUsername = event.ig_handle.replace(/^@+/, "");
            window.open(
              `https://www.instagram.com/${cleanUsername}/`,
              "_blank",
              "noopener,noreferrer"
            );
          }
        }}
        variant="outline"
        className={`font-extrabold${isInstagram ? " cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800" : ""}`}
      >
        {handleWithAt}
      </Badge>
    </BadgeMask>
  );
}
