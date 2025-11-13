import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import GeeveKickingRocks from "@/assets/artwork/geeve-kicking-rocks.svg?react";
import {
  Calendar,
  Clock,
  MapPin,
  DollarSign,
  Utensils,
  Check,
  Heart,
  Loader2,
  Trash2,
  ExternalLink,
} from "lucide-react";
import { Event } from "@/features/events";
import { memo, useMemo, useEffect, useRef } from "react";
import {
  formatTimeRange,
  formatRelativeEventDate,
  getDateCategory,
} from "@/shared/lib/dateUtils";
import {
  EventStatusBadge,
  NewEventBadge,
  OrganizationBadge,
} from "@/shared/components/badges/EventBadges";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@clerk/clerk-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useApi } from "@/shared/hooks/useApi";
import { useAdmin } from "@/shared/hooks/useAdmin";
import {
  useMyInterestedEvents,
  useToggleEventInterest,
} from "../hooks/useEventInterest";

interface EventsGridProps {
  data: Event[];
  isSelectMode?: boolean;
  selectedEvents?: Set<string>;
  onToggleEvent?: (eventId: string) => void;
  isLoading?: boolean;
  fetchNextPage?: () => void;
  hasNextPage?: boolean;
  isFetchingNextPage?: boolean;
}

const InterestButton = ({ event }: { event: Event }) => {
  const { isSignedIn } = useAuth();
  const navigate = useNavigate();
  const { data: interestedEvents } = useMyInterestedEvents();
  const toggleInterest = useToggleEventInterest(event.id);

  const viewerHasInterested = interestedEvents?.has(event.id) ?? false;

  const handleClick = () => {
    if (!isSignedIn) {
      navigate("/auth/sign-in");
      return;
    }

    const nextInterested = !viewerHasInterested;
    toggleInterest.mutate(nextInterested);
  };

  return (
    <Button
      variant="outline"
      size="sm"
      className="flex-1 w-full"
      onMouseDown={(e) => {
        e.stopPropagation();
        handleClick();
      }}
      disabled={toggleInterest.isPending}
    >
      <Heart
        className={`h-3.5 w-3.5 ${
          viewerHasInterested ? "fill-red-500 text-red-500" : ""
        }`}
      />
    </Button>
  );
};

const EventsGrid = memo(
  ({
    data,
    isSelectMode = false,
    selectedEvents = new Set(),
    onToggleEvent,
    isLoading = false,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  }: EventsGridProps) => {
    const navigate = useNavigate();
    const loadMoreRef = useRef<HTMLDivElement>(null);
    const prevEventIdsRef = useRef<Set<number>>(new Set());
    const { isAdmin } = useAdmin();
    const { eventsAPIClient } = useApi();
    const queryClient = useQueryClient();

    // Delete event mutation (admin only)
    const deleteEventMutation = useMutation({
      mutationFn: async (eventId: number) => {
        return eventsAPIClient.deleteEvent(eventId);
      },
      onSuccess: () => {
        // Invalidate and refetch events
        queryClient.invalidateQueries({ queryKey: ["events"] });
      },
    });

    // Calculate new events and their stagger indices synchronously during render
    const newEventStagger = useMemo(() => {
      const previousEventIds = prevEventIdsRef.current;

      // Find newly added events in order they appear in data
      const newEventsList: number[] = [];
      data.forEach((event) => {
        if (!previousEventIds.has(event.id)) {
          newEventsList.push(event.id);
        }
      });

      // Create a map of event ID to its stagger index
      const staggerMap = new Map<number, number>();
      newEventsList.forEach((id, index) => {
        staggerMap.set(id, index);
      });

      return staggerMap;
    }, [data]);

    // Update the ref after render
    useEffect(() => {
      const currentEventIds = new Set(data.map((e) => e.id));
      prevEventIdsRef.current = currentEventIds;
    }, [data]);

    // Group all events without pagination
    const groupedEvents = useMemo(() => {
      const groups: { [key: string]: Event[] } = {
        today: [],
        tomorrow: [],
        "later this week": [],
        "later this month": [],
        later: [],
        past: [],
      };

      data.forEach((event) => {
        const category = getDateCategory(event.dtstart_utc, event.dtend_utc);
        groups[category].push(event);
      });

      return groups;
    }, [data]);

    // Infinite scroll using Intersection Observer
    useEffect(() => {
      if (!fetchNextPage || !hasNextPage || isFetchingNextPage) return;

      const observer = new IntersectionObserver(
        (entries) => {
          const first = entries[0];
          if (first.isIntersecting) {
            fetchNextPage();
          }
        },
        { threshold: 0.1 }
      );

      const currentRef = loadMoreRef.current;
      if (currentRef) {
        observer.observe(currentRef);
      }

      return () => {
        if (currentRef) {
          observer.unobserve(currentRef);
        }
      };
    }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

    const renderEventCard = (event: Event) => {
      const isSelected = selectedEvents.has(event.id.toString());
      const staggerIndex = newEventStagger.get(event.id);

      // Calculate stagger delay for new events only
      // If staggerIndex exists, this is a new event
      const delay = staggerIndex !== undefined ? staggerIndex * 0.033 : 0;

      return (
        <motion.div
          key={event.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.5,
            delay: delay,
            ease: [0.18, 0.39, 0.14, 0.9],
          }}
          style={{ pointerEvents: "auto" }}
        >
          <Card
            className={`border-none rounded-xl shadow-none relative p-0 hover:shadow-lg dark:hover:shadow-gray-700 gap-0 h-full ${
              isSelectMode ? "cursor-pointer" : ""
            } ${isSelected ? "ring-2 ring-blue-500" : ""}`}
            onMouseDown={() =>
              isSelectMode && onToggleEvent?.(event.id.toString())
            }
          >
            {/* Selection Circle */}
            {isSelectMode && (
              <div
                className="absolute top-2 right-2 z-20 w-6 h-6 rounded-full border-2 border-white bg-gray-800/70 dark:bg-gray-200/70 flex items-center justify-center cursor-pointer"
                onMouseDown={(e) => {
                  e.stopPropagation();
                  onToggleEvent?.(event.id.toString());
                }}
              >
                {isSelected && (
                  <Check className="h-4 w-4 text-white dark:text-gray-800" />
                )}
              </div>
            )}

            <div className="relative min-h-40">
              {/* Event Image */}
              {event.source_image_url && (
                <img
                  src={event.source_image_url}
                  alt={event.title}
                  loading="lazy"
                  className="w-full h-40 object-cover rounded-t-xl cursor-pointer"
                  onMouseDown={(e) => {
                    if (!isSelectMode) {
                      e.stopPropagation();
                      navigate(`/events/${event.id}`);
                    }
                  }}
                />
              )}
              <EventStatusBadge event={event} />
              <NewEventBadge event={event} />
              <OrganizationBadge event={event} isSelectMode={isSelectMode} />
            </div>
            <CardHeader className="p-3.5 pb-0 border-gray-200 dark:border-gray-700 border-l border-r">
              <CardTitle
                className="text-sm line-clamp-2 leading-tight text-gray-900 dark:text-white"
                title={event.title}
              >
                {event.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="flex border-gray-200 dark:border-gray-700 flex-col border-b border-l rounded-b-xl border-r gap-1 h-full p-3.5 pt-0">
              <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                <Calendar className="h-3.5 w-3.5 flex-shrink-0" />
                <span className="truncate">
                  {formatRelativeEventDate(event.dtstart_utc)}
                </span>
              </div>

              <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                <Clock className="h-3.5 w-3.5 flex-shrink-0" />
                <span className="truncate">
                  {formatTimeRange(event.dtstart_utc, event.dtend_utc)}
                </span>
              </div>

              {event.location && (
                <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                  <MapPin className="flex-shrink-0 h-3.5 w-3.5" />
                  <span className="line-clamp-1" title={event.location}>
                    {event.location}
                  </span>
                </div>
              )}

              {event.price !== null && (
                <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                  <DollarSign className="h-3.5 w-3.5 flex-shrink-0" />
                  <span className="truncate">
                    {event.price === 0 ? "Free" : `$${event.price}`}
                  </span>
                </div>
              )}

              {event.food && (
                <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                  <Utensils className="h-3.5 w-3.5 flex-shrink-0" />
                  <span className="line-clamp-1" title={event.food}>
                    {event.food}
                  </span>
                </div>
              )}

              {event.registration && (
                <div className="text-xs text-gray-600 dark:text-gray-400 italic mt-1">
                  Registration required
                </div>
              )}

              {/* Action Buttons */}
              {!isSelectMode && (
                <div className="flex space-x-2 pt-2 w-full mt-auto">
                  <InterestButton event={event} />
                  {event.source_url && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-shrink-0"
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        if (event.source_url) {
                          window.open(
                            event.source_url,
                            "_blank",
                            "noopener,noreferrer"
                          );
                        }
                      }}
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                    </Button>
                  )}
                  {isAdmin && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex-1 text-xs h-8 text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-950/30"
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        if (
                          confirm(
                            `Delete "${event.title}"? This will also delete all associated event dates and cannot be undone.`
                          )
                        ) {
                          deleteEventMutation.mutate(event.id);
                        }
                      }}
                      disabled={deleteEventMutation.isPending}
                    >
                      {deleteEventMutation.isPending ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Trash2 className="h-3.5 w-3.5" />
                      )}
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      );
    };

    return (
      <div className="space-y-8 mt-4">
        {/* Events Grid with Section Headers */}
        <div className="space-y-6">
          {[
            "past",
            "today",
            "tomorrow",
            "later this week",
            "later this month",
            "later",
          ].map((category) => {
            const events = groupedEvents[category];
            if (events.length === 0) return null;

            const sectionTitle =
              category.charAt(0).toUpperCase() + category.slice(1);

            return (
              <div key={category} className="space-y-4">
                <p className="sm:text-xl text-lg font-semibold text-gray-900 dark:text-white">
                  {sectionTitle}
                </p>
                <div className="grid grid-cols-2 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2 sm:gap-2.5">
                  {events.map((event) => renderEventCard(event))}
                </div>
              </div>
            );
          })}
        </div>

        {/* No results message */}
        {data.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <GeeveKickingRocks className="w-48 h-48 mb-6 mx-auto text-gray-400 dark:text-gray-600" />
              <p className="text-gray-500 dark:text-gray-400 text-lg mb-2">
                No events found
              </p>
              <p className="text-gray-400 dark:text-gray-500 text-xs">
                Try adjusting your search or filters
              </p>
            </div>
          </div>
        )}

        {/* Infinite Scroll Loader */}
        {hasNextPage && (
          <div ref={loadMoreRef} className="flex justify-center py-8">
            <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span>Loading more events...</span>
            </div>
          </div>
        )}

        {/* All events loaded message */}
        {data.length > 0 && !hasNextPage && !isLoading && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
            You've reached the end! 🎉
          </div>
        )}
      </div>
    );
  }
);

EventsGrid.displayName = "EventsGrid";

export default EventsGrid;
