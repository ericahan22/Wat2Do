import React from "react";
import { useSearchParams } from "react-router-dom";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar, LayoutGrid, MousePointerClick, X } from "lucide-react";
import { useEvents, useEventSelection } from "@/hooks";
import EventsGrid from "@/components/EventsGrid";
import EventsCalendar from "@/components/EventsCalendar";
import EventLegend from "@/components/EventLegend";
import SearchInput from "@/components/SearchInput";
import { Button } from "@/components/ui/button";

function EventsPage() {
  const [searchParams] = useSearchParams();
  const view = (searchParams.get("view") as "grid" | "calendar") || "grid";

  const { data, isLoading, error, searchTerm, handleViewChange } = useEvents(
    view
  );
  const {
    isSelectMode,
    selectedEvents,
    toggleSelectMode,
    toggleEventSelection,
    exportToCalendar,
  } = useEventSelection(view);

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="sm:text-left">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Events
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Discover and explore upcoming events. Updates daily at ~8:30am EST.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <SearchInput placeholder="Search events..." className="flex-1" />

          {/* View toggle tabs */}
          <div className="flex gap-2">
            {view === "grid" && (
              <Button
                variant={isSelectMode ? "default" : "outline"}
                size="default"
                className="h-9"
                onMouseDown={toggleSelectMode}
              >
                {isSelectMode ? (
                  <>
                    <X className="h-4 w-4" />
                    Cancel
                  </>
                ) : (
                  <>
                    <MousePointerClick className="h-4 w-4" />
                    Export
                  </>
                )}
              </Button>
            )}
            <Tabs value={view} onValueChange={handleViewChange}>
              <TabsList>
                <TabsTrigger value="grid" className="flex items-center gap-2">
                  <LayoutGrid className="h-4 w-4" />
                  Grid
                </TabsTrigger>
                <TabsTrigger
                  value="calendar"
                  className="flex items-center gap-2"
                >
                  <Calendar className="h-4 w-4" />
                  Calendar
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {isLoading
              ? "Loading..."
              : searchTerm
              ? `Showing ${data.length} found events`
              : view === "grid"
              ? `Showing ${data.length} upcoming events`
              : `Showing ${data.length} events`}
          </p>
        </div>
      </div>

      {/* Loading state - show content with loading indicator */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <span>Loading events... (This may take a few seconds)</span>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="flex items-center justify-center py-8">
          <div className="text-lg text-red-600 dark:text-red-400">
            Error loading events: {error.message}
          </div>
        </div>
      )}

      {/* Render appropriate view */}
      {!isLoading && !error && (
        <>
          {view === "grid" ? (
            <EventsGrid
              data={data}
              isSelectMode={isSelectMode}
              selectedEvents={selectedEvents}
              onToggleEvent={toggleEventSelection}
            />
          ) : (
            <>
              <EventsCalendar events={data} />
              <EventLegend />
            </>
          )}
        </>
      )}

      {/* Floating Export Bar */}
      <div
        className={
          `fixed bottom-6 left-1/2 -translate-x-1/2 z-50 transform-gpu ` +
          `transition-all duration-300 ease-out ` +
          `${
            view === "grid" && isSelectMode && selectedEvents.size > 0
              ? "opacity-100 translate-y-0 scale-100"
              : "pointer-events-none opacity-0 translate-y-2 scale-95"
          }`
        }
        aria-hidden={
          view !== "grid" || !isSelectMode || selectedEvents.size === 0
        }
      >
        <div className="bg-white dark:bg-gray-800 rounded-full shadow-lg border border-gray-200 dark:border-gray-700 px-6 py-3 flex items-center gap-4">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {selectedEvents.size} event{selectedEvents.size !== 1 ? "s" : ""}{" "}
            selected
          </span>
          <Button
            size="sm"
            onMouseDown={toggleSelectMode}
            className="rounded-full"
          >
            <X className="h-4 w-4" />
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={() => exportToCalendar(data)}
            className="rounded-full"
          >
            <Calendar className="h-4 w-4" />
            Export to iCalendar
          </Button>
        </div>
      </div>
    </div>
  );
}

export default React.memo(EventsPage);
