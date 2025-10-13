import React from "react";
import { useSearchParams } from "react-router-dom";
import { Tabs, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { Calendar, LayoutGrid, X } from "lucide-react";
import { useEvents, getLastUpdatedText } from "../hooks/useEvents";
import { useEventSelection } from "../hooks/useEventSelection";
import EventsGrid from "../components/EventsGrid";
import EventsCalendar from "../components/EventsCalendar";
import EventLegend from "../components/EventLegend";
import SearchInput from "@/features/search/components/SearchInput";
import QuickFilters from "../components/QuickFilters";
import FloatingEventExportBar from "@/shared/components/common/FloatingEventExportBar";
import { Button } from "@/shared/components/ui/button";

function EventsPage() {
  const [searchParams] = useSearchParams();
  const view = (searchParams.get("view") as "grid" | "calendar") || "grid";

  const { data, isLoading, error, searchTerm, handleViewChange } = useEvents();
  const {
    isSelectMode,
    selectedEvents,
    toggleSelectMode,
    toggleEventSelection,
    exportToCalendar,
    exportToGoogleCalendar,
  } = useEventSelection(view);

  const lastUpdatedText = getLastUpdatedText();

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="sm:text-left">
        <h1 className="text-3xl font-bold mb-2">
          Events
        </h1>
        <p>
          Discover and explore upcoming events. Updates daily at ~8:30am EST.
          {lastUpdatedText && <span className="ml-1">{lastUpdatedText}.</span>}
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <SearchInput placeholder="Filter events by..." className="flex-1" />

          {/* View toggle tabs */}
          <div className="flex justify-end ml-auto gap-2">
            {view === "grid" && (
              <Button
                variant="outline"
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
                    <Calendar className="h-4 w-4" />
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

        <QuickFilters />

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {isLoading
              ? "Loading..."
              : searchTerm
              ? `Showing ${data.length} found events`
              : `Showing ${data.length} upcoming events`}
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
      <FloatingEventExportBar
        view={view}
        isSelectMode={isSelectMode}
        selectedEvents={selectedEvents}
        onCancel={toggleSelectMode}
        onExportICalendar={exportToCalendar}
        onExportGoogleCalendar={exportToGoogleCalendar}
      />
    </div>
  );
}

export default React.memo(EventsPage);
