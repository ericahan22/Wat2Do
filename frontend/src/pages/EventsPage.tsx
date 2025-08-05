import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useEvents } from "@/hooks";
import EventsGrid from "@/components/EventsGrid";
import SearchInput from "@/components/SearchInput";
import { memo } from "react";

const EventsPage = memo(() => {
  const {
    allEvents,
    filteredEvents,
    uniqueTimes,
    handleSearch,
    timeFilter,
    setTimeFilter,
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,
    infiniteScrollRef,
    totalCount,
    formatDate,
    formatTime,
  } = useEvents();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center sm:text-left">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Events
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {totalCount
            ? `Discover ${totalCount} events and activities`
            : "Loading events..."}
        </p>
      </div>

      {/* Filters */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <SearchInput onSearch={handleSearch} placeholder="Search events..." />

          <Select value={timeFilter} onValueChange={setTimeFilter}>
            <SelectTrigger className="w-full sm:w-auto">
              <SelectValue placeholder="Filter by time" />
            </SelectTrigger>
            <SelectContent>
              {uniqueTimes.map((time: string) => (
                <SelectItem key={time} value={time}>
                  {time}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Content Area - Shows loading, error, or events grid */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="text-lg text-gray-900 dark:text-gray-100">
            Loading events...
          </div>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="text-lg text-red-600 dark:text-red-400">
            Error loading events: {error.message}
          </div>
        </div>
      ) : (
        <EventsGrid
          events={filteredEvents}
          allEvents={allEvents}
          hasNextPage={hasNextPage}
          isFetchingNextPage={isFetchingNextPage}
          infiniteScrollRef={infiniteScrollRef}
          formatDate={formatDate}
          formatTime={formatTime}
        />
      )}
    </div>
  );
});

EventsPage.displayName = "EventsPage";

export default EventsPage;
