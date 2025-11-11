import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useUser } from "@clerk/clerk-react";
import { toast } from "sonner";
import {
  ArrowLeft,
  Calendar,
  MapPin,
  DollarSign,
  Utensils,
  ExternalLink,
  Users,
  Check,
  X,
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import { formatRelativeEventDateWithTime } from "@/shared/lib/dateUtils";
import { EventStatusBadge, NewEventBadge, OrganizationBadge } from "@/shared/components/badges/EventBadges";
import { Event } from "@/features/events/types/events";
import { useApi } from "@/shared/hooks/useApi";

interface EventPreviewProps {
  event: Event;
}


export function EventPreview({ event }: EventPreviewProps) {
  const navigate = useNavigate();
  const { user } = useUser();
  const isAdmin = user?.publicMetadata?.role === "admin";
  const queryClient = useQueryClient();
  const { eventsAPIClient } = useApi();

  const reviewSubmissionMutation = useMutation({
    mutationFn: async ({ action }: { action: "approve" | "reject" }) => {
      if (!event?.id) {
        throw new Error("No submission found");
      }
      return eventsAPIClient.reviewSubmission(event.id, action);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["event", event.id] });
      if (variables.action === "approve") {
        toast.success("Event approved successfully");
      } else {
        toast.success("Event rejected");
      }
    },
  });

  const handleBack = () => {
    navigate(-1);
  };

  const handleExternalLink = () => {
    if (event?.source_url) {
      window.open(event.source_url, "_blank");
    }
  };

  const handleApprove = () => {
    reviewSubmissionMutation.mutate({ action: "approve" });
  };

  const handleReject = () => {
    reviewSubmissionMutation.mutate({ action: "reject" });
  };

  return (
    <div className="max-w-xl mx-auto">
      {/* Back Button */}
      <div className="mb-6">
        <Button onMouseDown={handleBack} variant="ghost" className="p-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Events
        </Button>
      </div>

      {/* Polaroid Frame */}
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg dark:shadow-gray-700 p-4">
        {/* Image Section */}
        <div className="relative mb-4">
          {event.source_image_url ? (
            <img
              src={event.source_image_url}
              alt={event.title}
              className="w-full h-auto rounded-lg"
            />
          ) : (
            <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-gray-700 dark:to-gray-600 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <Calendar className="h-16 w-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400 text-lg">
                  No image available
                </p>
              </div>
            </div>
          )}
          <EventStatusBadge event={event} />
          <NewEventBadge event={event} />
          <OrganizationBadge event={event} />
        </div>

        {/* Event Details */}
        <div className="space-y-4">
          {/* Title */}
          <h1 className="text-xl font-bold text-center text-gray-900 dark:text-white">
            {event.title}
          </h1>
          {event.description && (
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              {event.description}
            </p>
          )}

          {/* Event Info Grid */}
          <div className="grid gap-2">
            {/* Date & Time - Show all dates if available */}
            <div className="p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center space-x-3 mb-2">
                <Calendar className="h-5 w-5 flex-shrink-0" />
                <p className="font-semibold text-gray-900 dark:text-white">
                  Dates
                </p>
              </div>
              <div className="ml-8 flex flex-wrap gap-2">
                {event.occurrences?.map((date) => (
                  <Badge
                    key={date.dtstart_utc}
                    variant="outline"
                    className="text-xs py-1 px-2 bg-white dark:bg-gray-800"
                  >
                    {formatRelativeEventDateWithTime(
                      date.dtstart_utc,
                      date.dtend_utc
                    )}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Location */}
            {event.location && (
              <>
                <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <MapPin className="h-5 w-5 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      Location
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {event.location}
                    </p>
                  </div>
                </div>
                {/* Google Maps Embed - Only show for physical locations */}
                {(() => {
                  const isVirtual = [
                    "virtual",
                    "zoom",
                    "google meet",
                    "online"
                  ].some((word) => event.location.toLowerCase().includes(word));
                  return (
                    !isVirtual && (
                      <div className="w-full h-64 rounded-lg overflow-hidden">
                        <iframe
                          width="100%"
                          height="100%"
                          loading="lazy"
                          referrerPolicy="no-referrer-when-downgrade"
                          src={`https://www.google.com/maps/embed/v1/place?key=${
                            import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ""
                          }&q=${encodeURIComponent(
                            `${event.location}, ${event.school || ""}`
                          )}`}
                        ></iframe>
                      </div>
                    )
                  );
                })()}
              </>
            )}

            {/* Price */}
            <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <DollarSign className="h-5 w-5 flex-shrink-0" />
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
                <Utensils className="h-5 w-5 flex-shrink-0" />
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
                <Users className="h-5 w-5 flex-shrink-0" />
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

          {/* Admin Action Buttons */}
          {isAdmin && event.id && (
            <div className="text-center pt-2 space-x-2">
              <Button
                onClick={handleApprove}
                disabled={reviewSubmissionMutation.isPending}
                variant="default"
                className="bg-green-600 hover:bg-green-700"
              >
                <Check className="h-4 w-4 mr-2" />
                {reviewSubmissionMutation.isPending
                  ? "Approving..."
                  : "Approve"}
              </Button>
              <Button
                onClick={handleReject}
                disabled={reviewSubmissionMutation.isPending}
                variant="destructive"
              >
                <X className="h-4 w-4 mr-2" />
                {reviewSubmissionMutation.isPending ? "Rejecting..." : "Reject"}
              </Button>
            </div>
          )}

          {/* Action Button */}
          {event.source_url && (
            <div className="text-center pt-2">
              <Button onClick={handleExternalLink}>
                <ExternalLink className="h-4 w-4" />
                View Event Source
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
