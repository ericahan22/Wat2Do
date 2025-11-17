import React from "react";
import { Event } from "@/features/events/types/events";
import EventsGrid from "./EventsGrid";
import EventsCalendar from "./EventsCalendar";
import EventLegend from "./EventLegend";
import { Card, Skeleton } from "@/shared";

interface EventsContentProps {
  view: "grid" | "calendar";
  data: Event[];
  isSelectMode: boolean;
  selectedEvents: Set<string>;
  onToggleEvent: (eventId: string) => void;
  isLoading: boolean;
  error: Error | null;
  fetchNextPage?: () => void;
  hasNextPage?: boolean;
  isFetchingNextPage?: boolean;
}

const EventsGridSkeleton = () => {
  return (
    <div className="space-y-6">
      {/* Section header skeleton */}
      <Skeleton className="h-7 w-32 mt-5" />

      {/* Events grid skeleton */}
      <div className="grid grid-cols-2 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2 sm:gap-2.5">
        {Array.from({ length: 12 }).map((_, i) => (
          <Card key={i} className="border-none rounded-xl shadow-none p-0">
            <Skeleton className="w-full h-40 rounded-t-xl" />
            <div className="px-3.5 pb-3.5 pt-1 space-y-2">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              <div className="space-y-2 pt-2">
                <Skeleton className="h-4 w-2/3" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

const EventsContent: React.FC<EventsContentProps> = ({
  view,
  data,
  isSelectMode,
  selectedEvents,
  onToggleEvent,
  isLoading,
  error,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
}) => {
  if (isLoading) {
    return <EventsGridSkeleton />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-lg text-red-600 dark:text-red-400">
          Error loading events: {error.message}
        </div>
      </div>
    );
  }

  if (view === "grid") {
    return (
      <EventsGrid
        data={data}
        isSelectMode={isSelectMode}
        selectedEvents={selectedEvents}
        onToggleEvent={onToggleEvent}
        isLoading={isLoading}
        fetchNextPage={fetchNextPage}
        hasNextPage={hasNextPage}
        isFetchingNextPage={isFetchingNextPage}
      />
    );
  }

  return (
    <>
      <EventsCalendar events={data} />
      <EventLegend />
    </>
  );
};

export default EventsContent;
