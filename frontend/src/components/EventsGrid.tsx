import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar, Clock, MapPin, ExternalLink, Bookmark } from "lucide-react";
import { Event } from "@/hooks";
import { memo } from "react";
import {
  formatPrettyDate,
  formatTimeRange,
  formatPrettyTime,
} from "@/lib/dateUtils";

interface EventsGridProps {
  data: Event[];
}

const EventsGrid = memo(({ data }: EventsGridProps) => {
  return (
    <div className="space-y-8">
      {/* Events Grid */}
      <div className="grid grid-cols-[repeat(auto-fit,_minmax(300px,_1fr))] gap-4 sm:gap-6">
        {data.map((event) => (
          <Card
            key={event.id}
            className="hover:shadow-lg h-full overflow-hidden bg-white"
          >
            <CardHeader className="pb-3">
              {/* Event Image */}
              {event.image_url && (
                <div className="mb-3 -mx-6 -mt-6">
                  <img
                    src={event.image_url}
                    alt={event.name}
                    className="w-full h-40 object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = "none";
                    }}
                  />
                </div>
              )}
              <CardTitle className="text-lg line-clamp-2 leading-tight text-gray-900 dark:text-white">
                {event.name}
              </CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                @{event.club_handle}
              </p>
              {event.categories && event.categories.length > 0 && (
                <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                  <Bookmark className="h-4 w-4 flex-shrink-0" />
                  <span
                    className="line-clamp-1"
                    title={event.categories.join(" | ")}
                  >
                    {event.categories.join(" | ")}
                  </span>
                </div>
              )}
            </CardHeader>
            <CardContent className="space-y-3 flex flex-col h-full">
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <Calendar className="h-4 w-4 flex-shrink-0" />
                <span className="truncate">{formatPrettyDate(event.date)}</span>
              </div>

              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <Clock className="h-4 w-4 flex-shrink-0" />
                <span className="truncate">
                  {event.end_time
                    ? formatTimeRange(event.start_time, event.end_time)
                    : formatPrettyTime(event.start_time)}
                </span>
              </div>

              {event.location && (
                <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                  <MapPin className="h-4 w-4 flex-shrink-0" />
                  <span className="line-clamp-1" title={event.location}>
                    {event.location}
                  </span>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-2 w-full mt-auto">
                {event.url ? (
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 w-full"
                    onMouseDown={() => window.open(event.url, "_blank")}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Open Event
                  </Button>
                ) : (
                  <div className="text-center py-2 w-full">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      No event link available
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* No results message */}
      {data.length === 0 && (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <p className="text-gray-500 dark:text-gray-400 text-lg mb-2">
              No events found
            </p>
            <p className="text-gray-400 dark:text-gray-500 text-sm">
              Try adjusting your search or filters
            </p>
          </div>
        </div>
      )}
    </div>
  );
});

EventsGrid.displayName = "EventsGrid";

export default EventsGrid;
