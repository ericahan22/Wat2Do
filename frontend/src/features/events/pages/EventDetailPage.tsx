import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Calendar,
  MapPin,
  DollarSign,
  Utensils,
  ExternalLink,
  Users,
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import { SEOHead } from "@/shared/components/SEOHead";
import { API_BASE_URL } from "@/shared/constants/api";
import { formatEventTimeRange, formatEventDate } from "@/shared/lib/dateUtils";
import { getEventStatus, isEventNew } from "@/shared/lib/eventUtils";
import { Event } from "@/features/events/types/events";
import BadgeMask from "@/shared/components/ui/badge-mask";

const fetchEvent = async (eventId: string): Promise<Event> => {
  const response = await fetch(`${API_BASE_URL}/events/${eventId}`);
  if (!response.ok) {
    throw new Error("Event not found");
  }
  return response.json();
};

const EventStatusBadge = ({ event }: { event: Event }) => {
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
};

const NewEventBadge = ({ event }: { event: Event }) => {
  if (!isEventNew(event)) return null;

  return (
    <BadgeMask variant="top-left">
      <Badge variant="new" className="font-extrabold">
        NEW
      </Badge>
    </BadgeMask>
  );
};

const OrganizationBadge = ({ event }: { event: Event }) => {
  if (!event.display_handle) return null;

  return (
    <BadgeMask variant="bottom-left">
      <Badge variant="outline" className="font-extrabold">
        {event.display_handle}
      </Badge>
    </BadgeMask>
  );
};

function EventDetailPage() {
  const { eventId } = useParams<{ eventId: string }>();
  const navigate = useNavigate();

  const { data: event, isLoading, error } = useQuery({
    queryKey: ["event", eventId],
    queryFn: () => fetchEvent(eventId!),
    enabled: !!eventId,
  });

  const handleBack = () => {
    navigate(-1);
  };

  const handleExternalLink = () => {
    if (event?.source_url) {
      window.open(event.source_url, "_blank");
    }
  };

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

  if (error || !event) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Event Not Found
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          The event you're looking for doesn't exist or has been removed.
        </p>
        <Button onClick={handleBack} variant="outline">
          <ArrowLeft className="h-4 w-4" />
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <SEOHead
        title={`${event.title} - Event Details`}
        description={
          event.description ||
          `Join us for ${event.title} on ${formatEventDate(event.dtstart_utc, event.dtend_utc)}`
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

      {/* Back Button */}
      <div className="mb-6">
        <Button onClick={handleBack} variant="ghost" className="p-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Events
        </Button>
      </div>

      {/* Polaroid-style Event Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative max-w-lg mx-auto"
      >
        {/* Polaroid Frame */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-4 transform rotate-1 hover:rotate-0 transition-transform duration-300">
          {/* Image Section */}
          <div className="relative mb-4">
            {event.source_image_url ? (
              <div className="relative">
                <img
                  src={event.source_image_url}
                  alt={event.title}
                  className="w-full h-48 object-cover rounded-lg shadow-lg aspect-square"
                />
                <EventStatusBadge event={event} />
                <NewEventBadge event={event} />
                <OrganizationBadge event={event} />
              </div>
            ) : (
              <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-gray-700 dark:to-gray-600 rounded-lg shadow-lg flex items-center justify-center aspect-square">
                <div className="text-center">
                  <Calendar className="h-16 w-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400 text-lg">
                    No image available
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Event Details */}
          <div className="space-y-4">
            {/* Title */}
            <div className="text-center">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {event.title}
              </h1>
              {event.description && (
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  {event.description}
                </p>
              )}
            </div>

            {/* Event Info Grid */}
            <div className="grid gap-2">
              {/* Date & Time */}
              <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <Calendar className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {formatEventDate(event.dtstart_utc, event.dtend_utc)}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {formatEventTimeRange(event.dtstart_utc, event.dtend_utc)}
                  </p>
                </div>
              </div>

              {/* Location */}
              {event.location && (
                <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <MapPin className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      Location
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {event.location}
                    </p>
                  </div>
                </div>
              )}

              {/* Price */}
              <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <DollarSign className="h-5 w-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0" />
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    Price
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {event.price === null || event.price === 0
                      ? "Free"
                      : `$${event.price}`}
                  </p>
                </div>
              </div>

              {/* Food */}
              {event.food && (
                <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <Utensils className="h-5 w-5 text-orange-600 dark:text-orange-400 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      Food
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {event.food}
                    </p>
                  </div>
                </div>
              )}

              {/* Registration */}
              {event.registration && (
                <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <Users className="h-5 w-5 text-purple-600 dark:text-purple-400 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      Registration
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Required
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Social Links */}
            {(event.ig_handle ||
              event.discord_handle ||
              event.x_handle ||
              event.tiktok_handle ||
              event.fb_handle) && (
              <div className="p-2 bg-gray-50 dark:bg-gray-700 rounded-lg flex flex-wrap gap-2">
                {event.ig_handle && (
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-pink-50 dark:hover:bg-pink-900/20"
                  >
                    Instagram: {event.ig_handle}
                  </Badge>
                )}
                {event.discord_handle && (
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
                  >
                    Discord: {event.discord_handle}
                  </Badge>
                )}
                {event.x_handle && (
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20"
                  >
                    X: {event.x_handle}
                  </Badge>
                )}
                {event.tiktok_handle && (
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-900/20"
                  >
                    TikTok: {event.tiktok_handle}
                  </Badge>
                )}
                {event.fb_handle && (
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20"
                  >
                    Facebook: {event.fb_handle}
                  </Badge>
                )}
              </div>
            )}

            {/* Action Button */}
            {event.source_url && (
              <div className="text-center pt-2">
                <Button onClick={handleExternalLink}>
                  <ExternalLink className="h-4 w-4" />
                  View Event Details
                </Button>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default EventDetailPage;
