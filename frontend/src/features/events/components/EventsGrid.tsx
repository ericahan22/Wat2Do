import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
  PaginationEllipsis,
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
import { formatEventDate, formatEventTimeRange } from "@/shared/lib/dateUtils";
import { getEventStatus, isEventNew } from "@/shared/lib/eventUtils";
import { EVENTS_PER_PAGE } from "@/features/events/constants/events";
import BadgeMask from "@/shared/components/ui/badge-mask";
import { motion } from "framer-motion";

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
        <motion.div
          key={`events-grid-${data.length}-${currentPage}`}
          className="grid sm:grid-cols-[repeat(auto-fit,_minmax(175px,_1fr))] grid-cols-2 gap-2 sm:gap-2.5"
          initial="hidden"
          animate="visible"
          variants={{
            visible: {
              transition: {
                staggerChildren: 0.0175,
              },
            },
          }}
        >
          {paginatedData.map((event: Event) => {
            const isSelected = selectedEvents.has(event.id.toString());
            return (
              <motion.div
                key={event.id}
                variants={{
                  hidden: { opacity: 0, y: 20 },
                  visible: {
                    opacity: 1,
                    y: 0,
                    transition: {
                      duration: 0.5,
                      ease: [0.18, 0.39, 0.14, 0.9],
                    },
                  },
                }}
              >
                <Card
                  className={`border-none rounded-xl shadow-none relative p-0 hover:shadow-lg gap-0 h-full ${
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
                        className="w-full h-40 object-cover rounded-t-xl"
                      />
                    )}
                    <EventStatusBadge event={event} />
                    <NewEventBadge event={event} />
                    <OrganizationBadge event={event} />
                  </div>
                  <CardHeader className="p-3.5 pb-0 border-gray-200 dark:border-gray-700 border-l border-r">
                    <CardTitle className="text-sm line-clamp-2 leading-tight text-gray-900 dark:text-white">
                      {event.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="flex border-gray-200 dark:border-gray-700 flex-col border-b border-l rounded-b-xl border-r gap-1 h-full p-3.5 pt-0">
                    <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                      <Calendar className="h-3.5 w-3.5 flex-shrink-0" />
                      <span className="truncate">
                        {formatEventDate(event.dtstart)}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                      <Clock className="h-3.5 w-3.5 flex-shrink-0" />
                      <span className="truncate">
                        {formatEventTimeRange(event.dtstart, event.dtend)}
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
                        {event.source_url ? (
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex-1 w-full"
                            onMouseDown={() =>
                              window.open(event.source_url || "", "_blank")
                            }
                          >
                            <ExternalLink className="h-3.5 w-3.5" />
                            View Source
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
              </motion.div>
            );
          })}
        </motion.div>

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
                  onMouseDown={() =>
                    handlePageChange(Math.max(1, currentPage - 1))
                  }
                  className={
                    currentPage === 1
                      ? "pointer-events-none opacity-50"
                      : "cursor-pointer"
                  }
                />
              </PaginationItem>

              {(() => {
                const pages = [];
                const showEllipsis = totalPages > 7;
                
                if (showEllipsis) {
                  // Show first 3 pages
                  for (let i = 1; i <= 3; i++) {
                    pages.push(
                      <PaginationItem key={i}>
                        <PaginationLink
                          onMouseDown={() => handlePageChange(i)}
                          isActive={currentPage === i}
                          className="cursor-pointer"
                        >
                          {i}
                        </PaginationLink>
                      </PaginationItem>
                    );
                  }
                  
                  // Show ellipsis if current page is far from start
                  if (currentPage > 5) {
                    pages.push(
                      <PaginationItem key="ellipsis-start">
                        <PaginationEllipsis />
                      </PaginationItem>
                    );
                  }
                  
                  // Show current page and surrounding pages
                  const start = Math.max(4, currentPage - 1);
                  const end = Math.min(totalPages - 2, currentPage + 1);
                  
                  for (let i = start; i <= end; i++) {
                    if (i > 3 && i < totalPages - 2) {
                      pages.push(
                        <PaginationItem key={i}>
                          <PaginationLink
                            onMouseDown={() => handlePageChange(i)}
                            isActive={currentPage === i}
                            className="cursor-pointer"
                          >
                            {i}
                          </PaginationLink>
                        </PaginationItem>
                      );
                    }
                  }
                  
                  // Show ellipsis if current page is far from end
                  if (currentPage < totalPages - 4) {
                    pages.push(
                      <PaginationItem key="ellipsis-end">
                        <PaginationEllipsis />
                      </PaginationItem>
                    );
                  }
                  
                  // Show last 3 pages
                  for (let i = totalPages - 2; i <= totalPages; i++) {
                    pages.push(
                      <PaginationItem key={i}>
                        <PaginationLink
                          onMouseDown={() => handlePageChange(i)}
                          isActive={currentPage === i}
                          className="cursor-pointer"
                        >
                          {i}
                        </PaginationLink>
                      </PaginationItem>
                    );
                  }
                } else {
                  // Show all pages if 7 or fewer
                  for (let i = 1; i <= totalPages; i++) {
                    pages.push(
                      <PaginationItem key={i}>
                        <PaginationLink
                          onMouseDown={() => handlePageChange(i)}
                          isActive={currentPage === i}
                          className="cursor-pointer"
                        >
                          {i}
                        </PaginationLink>
                      </PaginationItem>
                    );
                  }
                }
                
                return pages;
              })()}

              <PaginationItem>
                <PaginationNext
                  onMouseDown={() =>
                    handlePageChange(Math.min(totalPages, currentPage + 1))
                  }
                  className={
                    currentPage === totalPages
                      ? "pointer-events-none opacity-50"
                      : "cursor-pointer"
                  }
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
