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
  if (!event.display_handle) return null;

  // Only link if display_handle is an ig_handle
  const isInstagram = !!event.ig_handle && event.display_handle === event.ig_handle;

  return (
    <BadgeMask variant="bottom-left">
      <Badge
        onMouseDown={() => {
          if (!isSelectMode && isInstagram) {
            window.open(
              `https://www.instagram.com/${event.display_handle}/`,
              "_blank"
            );
          }
        }}
        variant="outline"
        className={`font-extrabold${isInstagram ? " cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800" : ""}`}
      >
        {isInstagram ? `@${event.display_handle}` : event.display_handle}
      </Badge>
    </BadgeMask>
  );
}

