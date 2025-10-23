import { useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { useEvents, useEventSelection, EventsHeader, EventsStatusBar, EventsContent, QuickFilters } from "@/features/events";
import { getTodayString, SEOHead, Button, Tabs, TabsList, TabsTrigger, FloatingEventExportBar } from "@/shared";
import { Calendar, X, History, LayoutGrid, Sparkles } from "lucide-react";
import SearchInput from "@/features/search/components/SearchInput";

function EventsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const view = (searchParams.get("view") as "grid" | "calendar") || "grid";
  const placeholder = searchParams.get("placeholder") || "Free food";

  const handleViewChange = useCallback(
    (newView: "grid" | "calendar") => {
      const newParams = new URLSearchParams(searchParams);
      newParams.set("view", newView);
      setSearchParams(newParams);
    },
    [searchParams, setSearchParams]
  );

  const {
    data,
    isLoading,
    error,
    searchTerm,
    dtstart,
    addedAt,
    handleToggleStartDate,
    handleToggleNewEvents,
  } = useEvents();

  const {
    isSelectMode,
    selectedEvents,
    toggleSelectMode,
    toggleEventSelection,
    exportToCalendar,
    exportToGoogleCalendar,
  } = useEventSelection(view);

  const todayString = getTodayString();
  const isShowingPastEvents = Boolean(dtstart && dtstart !== todayString);
  const isShowingNewEvents = Boolean(addedAt);

  return (
    <div className="flex flex-col gap-4">
      <SEOHead
        title="Events - Discover University of Waterloo Club Events"
        description="Browse and discover exciting club events at the University of Waterloo. Find upcoming events, filter by date, and stay connected with campus activities."
        url="/events"
        keywords={[
          "University of Waterloo events",
          "UW club events",
          "campus events",
          "student events",
          "Waterloo university events",
          "upcoming events",
          "event calendar",
          "campus activities",
        ]}
      />
      <EventsHeader />

      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-4">
          <SearchInput placeholder={placeholder} className="flex-1" />
          <Tabs
            value={view}
            onValueChange={(value) =>
              handleViewChange(value as "grid" | "calendar")
            }
          >
            <TabsList>
              <TabsTrigger value="grid" className="flex items-center gap-2">
                <LayoutGrid className="h-4 w-4" />
                Grid
              </TabsTrigger>
              <TabsTrigger value="calendar" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Calendar
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <QuickFilters />

        <div className="flex items-center justify-between">
          <EventsStatusBar
            isLoading={isLoading}
            searchTerm={searchTerm}
            isShowingPastEvents={isShowingPastEvents}
            totalCount={data.length}
          />
          <div className="flex">
            <Button variant="ghost" onMouseDown={handleToggleNewEvents}>
              <Sparkles className="h-4 w-4" />
              {isShowingNewEvents ? "All" : "New"}
            </Button>
            {!isShowingNewEvents && (
              <Button variant="ghost" onMouseDown={handleToggleStartDate}>
                <History className="h-4 w-4" />
                {isShowingPastEvents ? "Upcoming" : "Past"}
              </Button>
            )}
            {view === "grid" && (
              <Button variant="ghost" onMouseDown={toggleSelectMode}>
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
          </div>
        </div>
      </div>

      <EventsContent
        view={view}
        data={data}
        isSelectMode={isSelectMode}
        selectedEvents={selectedEvents}
        onToggleEvent={toggleEventSelection}
        isLoading={isLoading}
        error={error}
      />

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

export default EventsPage;
