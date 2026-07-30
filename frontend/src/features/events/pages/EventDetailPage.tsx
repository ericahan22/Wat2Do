import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { Button, Skeleton } from "@/shared/components/ui";
import { SEOHead } from "@/shared/components/SEOHead";
import { formatEventDate } from "@/shared/lib/dateUtils";
import { EventPreview } from "@/features/events/components/EventPreview";
import { useApi } from "@/shared/hooks/useApi";
import { useKeyboardShortcuts } from "@/shared/hooks/useKeyboardShortcuts";

const EventDetailSkeleton = () => {
  return (
    <div className="max-w-xl mx-auto mt-8">
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg dark:shadow-gray-700 p-4">
        <Skeleton className="w-full h-64 rounded-lg mb-4" />
        <Skeleton className="h-8 w-3/4 mx-auto mb-4" />
        <div className="space-y-2 mb-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-16 w-full rounded-lg" />
          <Skeleton className="h-16 w-full rounded-lg" />
          <Skeleton className="h-16 w-full rounded-lg" />
        </div>
      </div>
    </div>
  );
};

function EventDetailPage() {
  const { eventId } = useParams<{ eventId: string }>();
  const { eventsAPIClient } = useApi();
  const navigate = useNavigate();

  useKeyboardShortcuts({
    onEscape: () => {
      navigate("/events");
    },
  });

  const { data: event, isLoading, error } = useQuery({
    queryKey: ["event", eventId],
    queryFn: () => eventsAPIClient.getEvent(Number(eventId)),
    enabled: !!eventId,
  });

  if (isLoading) {
    return <EventDetailSkeleton />;
  }

  if (error || !event) {
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
        url={`/events/${event.id}`}
        keywords={[
          event.title,
          event.location || "",
          event.display_handle || "",
          "campus events",
          "student events",
          "event",
        ].filter(Boolean)}
      />
      <EventPreview event={event} />
    </>
  );
}

export default EventDetailPage;
