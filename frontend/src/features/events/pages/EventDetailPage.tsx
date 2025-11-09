import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useUser } from "@clerk/clerk-react";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { SEOHead } from "@/shared/components/SEOHead";
import { formatEventDate } from "@/shared/lib/dateUtils";
import { EventEditForm } from "@/features/events/components/EventEditForm";
import { EventPreview } from "@/features/events/components/EventPreview";
import { useApi } from "@/shared/hooks/useApi";

function EventDetailPage() {
  const { eventId } = useParams<{ eventId: string }>();
  const { user } = useUser();
  const isAdmin = user?.publicMetadata?.role === "admin";
  const { eventsAPIClient } = useApi();

  const { data: event, isLoading, error } = useQuery({
    queryKey: ["event", eventId],
    queryFn: () => eventsAPIClient.getEvent(Number(eventId!)),
    enabled: !!eventId,
  });

  const canEditEvent = event?.is_submitter || isAdmin;
  const isPendingAndUnauthorized = event?.status === "PENDING" && !canEditEvent;

  // Show loading while either query is loading
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 dark:border-gray-100"></div>
          <span>Loading event...</span>
        </div>
      </div>
    );
  }

  // Show "Event Not Found" for actual errors, or if pending and unauthorized
  if (error || !event || isPendingAndUnauthorized) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Event Not Found
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          The event you're looking for doesn't exist or has been removed.
        </p>
        <Button onClick={() => window.history.back()} variant="outline">
          <ArrowLeft className="h-4 w-4" />
          Go Back
        </Button>
      </div>
    );
  }

  // Render edit mode for pending events when user has permission, OR for admins regardless of status
  if ((event.status === "PENDING" && canEditEvent) || isAdmin) {
    return (
      <>
        <SEOHead
          title={`${event.title} - Edit Event`}
          description="Edit pending event details"
          url={`/event/${event.id}`}
        />
        <EventEditForm event={event} />
      </>
    );
  }

  // Render preview mode for confirmed events
  return (
    <>
      <SEOHead
        title={`${event.title} - Event Details`}
        description={
          event.description ||
          `Join us for ${event.title} on ${formatEventDate(
            event.dtstart_utc,
            event.dtend_utc
          )}`
        }
        url={`/event/${event.id}`}
        keywords={[
          event.title,
          event.location || "",
          event.display_handle || "",
          "University of Waterloo",
          "event",
          "campus event",
        ].filter(Boolean)}
      />
      <EventPreview event={event}/>
    </>
  );
}

export default EventDetailPage;
