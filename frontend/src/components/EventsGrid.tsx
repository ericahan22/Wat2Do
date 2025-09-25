import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Calendar,
  Clock,
  MapPin,
  ExternalLink,
  DollarSign,
} from "lucide-react";
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

const getEventStatus = (event: Event): "live" | "soon" | "none" => {
  const now = new Date();
  const startDateTime = new Date(`${event.date}T${event.start_time}`);
  const endDateTime = new Date(`${event.date}T${event.end_time}`);

  const nowTime = now.getTime();
  const startTime = startDateTime.getTime();
  const endTime = endDateTime.getTime();
  const oneHourInMs = 60 * 60 * 1000;

  if (nowTime >= startTime && nowTime <= endTime) return "live";

  if (startTime > nowTime && startTime - nowTime <= oneHourInMs) return "soon";

  return "none";
};

const isEventNew = (event: Event): boolean => {
  if (!event.added_at) return false;
  
  const now = new Date();
  const addedAt = new Date(event.added_at);
  const twentyFourHoursInMs = 24 * 60 * 60 * 1000;
  
  return (now.getTime() - addedAt.getTime()) <= twentyFourHoursInMs;
};

const EventStatusBadge = ({ event }: { event: Event }) => {
  const status = getEventStatus(event);

  if (status === "live") {
    return (
      <Badge variant="live" className="absolute top-2 right-2 z-10">
        LIVE
      </Badge>
    );
  }

  if (status === "soon") {
    return (
      <Badge variant="soon" className="absolute top-2 right-2 z-10">
        Starts in 1 hr
      </Badge>
    );
  }

  return null;
};

const NewEventBadge = ({ event }: { event: Event }) => {
  if (!isEventNew(event)) return null;

  return (
    <Badge variant="new" className="absolute top-2 left-2 z-10">
      NEW
    </Badge>
  );
};

const EventsGrid = memo(({ data }: EventsGridProps) => {
  return (
    <div className="space-y-8">
      {/* Events Grid */}
      <div className="grid grid-cols-[repeat(auto-fit,_minmax(185px,_1fr))] gap-2 sm:gap-3.5">
        {data.map((event) => (
          <Card
            key={event.id}
            className="relative p-0 hover:shadow-lg gap-0 h-full overflow-hidden "
          >
            <EventStatusBadge event={event} />
            <NewEventBadge event={event} />

            {/* Event Image */}
            {event.image_url && (
              <div className=" ">
                <img
                  src={event.image_url}
                  alt={event.name}
                  className="w-full h-40 object-cover brightness-75"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = "none";
                  }}
                />
              </div>
            )}
            <CardHeader className="p-3.5 pb-0">
              <CardTitle className="text-sm line-clamp-2 leading-tight text-gray-900 dark:text-white">
                {event.name}
              </CardTitle>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                @{event.club_handle}
              </p>
            </CardHeader>
            <CardContent className="flex flex-col gap-1 h-full p-3.5 pt-2.5">
              <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                <Calendar className="h-3.5 w-3.5 flex-shrink-0" />
                <span className="truncate">{formatPrettyDate(event.date)}</span>
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
                    : `${event.price}`}
                </span>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-2 w-full mt-auto">
                {event.url ? (
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 w-full"
                    onMouseDown={() => window.open(event.url, "_blank")}
                  >
                    <ExternalLink className="h-3.5 w-3.5 mr-2" />
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
            <p className="text-gray-400 dark:text-gray-500 text-xs">
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
