import React from "react";
import { Event } from "@/features/events/types/events";
import EventsGrid from "./EventsGrid";
import EventsCalendar from "./EventsCalendar";
import EventLegend from "./EventLegend";

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
    return (
      <div className="flex items-center justify-center py-8">
        <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 dark:border-gray-100"></div>
          <span>Loading events... (This may take a few seconds)</span>
        </div>
      </div>
    );
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
