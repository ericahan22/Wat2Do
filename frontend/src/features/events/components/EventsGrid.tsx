import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/shared/components/ui/pagination";
import GeeveKickingRocks from "@/assets/artwork/geeve-kicking-rocks.svg?react";
import {
  Calendar,
  Clock,
  MapPin,
  ExternalLink,
  DollarSign,
  Utensils,
  Check,
} from "lucide-react";
import { Event } from "@/features/events/types/events";
import { memo, useState, useMemo, useEffect } from "react";
import {
  formatPrettyDate,
  formatTimeRange,
  formatPrettyTime,
} from "@/shared/lib/dateUtils";
import { getEventStatus, isEventNew } from "@/shared/lib/eventUtils";
import EventBadgeMaskRight from "@/assets/event-badge-mask-right.svg?react";
import EventBadgeMaskLeft from "@/assets/event-badge-mask-left.svg?react";
import EventBadgeMaskRightLong from "@/assets/event-badge-mask-right-long.svg?react";
import { EVENTS_PER_PAGE } from "@/features/events/constants/events";

interface EventsGridProps {
  data: Event[];
  isSelectMode?: boolean;
  selectedEvents?: Set<string>;
  onToggleEvent?: (eventId: string) => void;
  isLoading?: boolean;
}

const EventStatusBadge = ({ event }: { event: Event }) => {
  const status = getEventStatus(event);

  if (status === "live") {
    return (
      <>
        <EventBadgeMaskRight className="absolute top-0 right-0 z-10 h-8 w-auto text-white dark:text-gray-900" />
        <Badge
          variant="live"
          className="font-extrabold tracking-[0.043em] absolute top-0 right-0 z-10"
        >
          LIVE
        </Badge>
      </>
    );
  }

  if (status === "soon") {
    return (
      <>
        <EventBadgeMaskRightLong className="absolute top-0 right-0 z-10 h-8 w-auto text-white dark:text-gray-900" />
        <Badge
          variant="soon"
          className="font-extrabold tracking-[0.03em] absolute top-0 right-0 z-10"
        >
          Starting soon
        </Badge>
      </>
    );
  }

  return null;
};

const NewEventBadge = ({ event }: { event: Event }) => {
  if (!isEventNew(event)) return null;

  return (
    <>
      <EventBadgeMaskLeft className="absolute top-0 left-0 z-10 h-8 w-auto text-white dark:text-gray-900" />
      <Badge
        variant="new"
        className="font-extrabold absolute top-0 left-0 z-10"
      >
        NEW
      </Badge>
    </>
  );
};

const EventsGrid = memo(
  ({
    data,
    isSelectMode = false,
    selectedEvents = new Set(),
    onToggleEvent,
    isLoading = false,
  }: EventsGridProps) => {
    const [currentPage, setCurrentPage] = useState(1);

    const paginatedData = useMemo(() => {
      const startIndex = (currentPage - 1) * EVENTS_PER_PAGE;
      const endIndex = startIndex + EVENTS_PER_PAGE;
      return data.slice(startIndex, endIndex);
    }, [data, currentPage]);

    const totalPages = Math.ceil(data.length / EVENTS_PER_PAGE);

    const handlePageChange = (page: number) => {
      setCurrentPage(page);
    };

    // Reset to first page when data changes
    useEffect(() => {
      setCurrentPage(1);
    }, [data]);

    return (
      <div className="space-y-8">
        {/* Events Grid */}
        <div className="grid sm:grid-cols-[repeat(auto-fit,_minmax(185px,_1fr))] grid-cols-2 gap-2 sm:gap-2.5">
          {paginatedData.map((event) => {
            const isSelected = selectedEvents.has(event.id);
            return (
              <Card
                key={event.id}
                className={`border-none rounded-xl shadow-none relative p-0 hover:shadow-lg gap-0 h-full ${
                  isSelectMode ? "cursor-pointer" : ""
                } ${isSelected ? "ring-2 ring-blue-500" : ""}`}
                onMouseDown={() => isSelectMode && onToggleEvent?.(event.id)}
              >
                <EventStatusBadge event={event} />
                <NewEventBadge event={event} />

                {/* Selection Circle */}
                {isSelectMode && (
                  <div
                    className="absolute top-2 right-2 z-20 w-6 h-6 rounded-full border-2 border-white bg-gray-800/70 dark:bg-gray-200/70 flex items-center justify-center cursor-pointer"
                    onMouseDown={(e) => {
                      e.stopPropagation();
                      onToggleEvent?.(event.id);
                    }}
                  >
                    {isSelected && (
                      <Check className="h-4 w-4 text-white dark:text-gray-800" />
                    )}
                  </div>
                )}

                {/* Event Image */}
                {event.image_url && (
                  <img
                    src={event.image_url}
                    alt={event.name}
                    loading="lazy"
                    className="w-full h-40 object-cover rounded-t-xl"
                  />
                )}
                <CardHeader className="p-3.5 pb-0 border-gray-200 dark:border-gray-700 border-l border-r">
                  <CardTitle className="text-sm line-clamp-2 leading-tight text-gray-900 dark:text-white">
                    {event.name}
                  </CardTitle>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    @{event.club_handle}
                  </p>
                </CardHeader>
                <CardContent className="flex border-gray-200 dark:border-gray-700 flex-col border-b border-l rounded-b-xl border-r gap-1 h-full p-3.5 pt-2.5">
                  <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                    <Calendar className="h-3.5 w-3.5 flex-shrink-0" />
                    <span className="truncate">
                      {formatPrettyDate(event.date)}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                    <Clock className="h-3.5 w-3.5 flex-shrink-0" />
                    <span className="truncate">
                      {event.end_time
                        ? formatTimeRange(event.start_time, event.end_time)
                        : formatPrettyTime(event.start_time)}
                    </span>
                  </div>

                  {event.location && (
                    <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                      <MapPin className="h-3.5 w-3.5 flex-shrink-0" />
                      <span className="line-clamp-1" title={event.location}>
                        {event.location}
                      </span>
                    </div>
                  )}

                  <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                    <DollarSign className="h-3.5 w-3.5 flex-shrink-0" />
                    <span className="truncate">
                      {event.price === null || event.price === 0
                        ? "Free"
                        : `$${event.price}`}
                    </span>
                  </div>

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
                    <div className="flex space-x-3 pt-2 w-full mt-auto">
                      {event.url ? (
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1 w-full"
                          onMouseDown={() => window.open(event.url, "_blank")}
                        >
                          <ExternalLink className="h-3.5 w-3.5" />
                          Open Event
                        </Button>
                      ) : (
                        <div className="text-center py-2 w-full">
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            No event link available
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* No results message */}
        {data.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <GeeveKickingRocks className="w-48 h-48 mb-6 mx-auto text-gray-400 dark:text-gray-600" />
              <p className="text-gray-500 dark:text-gray-400 text-lg mb-2">
                No upcoming events found
              </p>
              <p className="text-gray-400 dark:text-gray-500 text-xs">
                Try adjusting your search or filters
              </p>
            </div>
          </div>
        )}

        {/* Pagination */}
        {data.length > 0 && totalPages > 1 && (
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
                  className={currentPage === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                />
              </PaginationItem>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <PaginationItem key={page}>
                  <PaginationLink
                    onClick={() => handlePageChange(page)}
                    isActive={currentPage === page}
                    className="cursor-pointer"
                  >
                    {page}
                  </PaginationLink>
                </PaginationItem>
              ))}
              
              <PaginationItem>
                <PaginationNext
                  onClick={() => handlePageChange(Math.min(totalPages, currentPage + 1))}
                  className={currentPage === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        )}
      </div>
    );
  }
);

EventsGrid.displayName = "EventsGrid";

export default EventsGrid;
